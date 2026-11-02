
"""
executors.py

MAF workflow executors with structured validation and telemetry.

Both executors share one MAF agent and the same MCP tools.
Each stage creates a fresh agent session.
"""

import json

from agent_framework import Executor, WorkflowContext, handler

from app.models import (
    AgreementDocument,
    ClauseExtractionResult,
    ClauseExtractionHandoff,
    FinancialRiskResult,
    FinancialRiskHandoff,
    ComplianceAnalysisResult,
    ComplianceAnalysisHandoff,
    AgreementAnalysisReport,
)
from app.telemetry import WorkflowTelemetry
from app.validators import validate_clauses, validate_financial_risks, validate_compliance


def parse_json_response(response_text: str, model_type):
    """Extract a JSON object and validate it against a Pydantic contract."""

    text = response_text.strip()

    if text.startswith("```json") and text.endswith("```"):
        text = text[7:-3].strip()
    elif text.startswith("```") and text.endswith("```"):
        text = text[3:-3].strip()

    # Allow a short explanation before the JSON object.
    json_start = text.find("{")

    if json_start == -1:
        raise ValueError("Agent response contains no JSON object.")

    decoder = json.JSONDecoder()
    data, _ = decoder.raw_decode(text[json_start:])

    return model_type.model_validate(data)

class RetrievalExecutor(Executor):
    """Retrieve an agreement using the agent-selected MCP tool."""

    def __init__(self, agent, tools, telemetry: WorkflowTelemetry):
        super().__init__(id="retrieval")
        self.agent = agent
        self.tools = tools
        self.telemetry = telemetry

    @handler
    async def retrieve(
        self,
        filename: str,
        ctx: WorkflowContext[AgreementDocument],
    ) -> None:
        self.telemetry.start_stage("Agreement Retrieval")

        try:
            session = self.agent.create_session()

            response = await self.agent.run(
                f"""
                Retrieve the complete agreement named {filename}.

                Use the appropriate MCP tool.
                Do not summarize or modify the agreement.
                Return only the complete agreement text.
                """,
                session=session,
                tools=self.tools,
            )

            if response.user_input_requests:
                raise RuntimeError(
                    "Agreement retrieval requires tool approval."
                )

            if not response.text or not response.text.strip():
                raise RuntimeError(
                    "Agreement retrieval returned empty text."
                )

            document = AgreementDocument(
                filename=filename,
                content=response.text,
            )

            self.telemetry.finish_stage()
            await ctx.send_message(document)

        except Exception as error:
            if self.telemetry._active is not None:
                self.telemetry.finish_stage(error)
            raise


class ClauseExtractionExecutor(Executor):
    """Extract clauses and enforce skill loading and validation."""

    def __init__(self, agent, tools, telemetry: WorkflowTelemetry):
        super().__init__(id="clause_extraction")
        self.agent = agent
        self.tools = tools
        self.telemetry = telemetry

    @handler
    async def extract(
        self,
        document: AgreementDocument,
        ctx: WorkflowContext[ClauseExtractionHandoff],
    ) -> None:
        self.telemetry.start_stage(
            "Clause Extraction",
            expected_skill="clause-extraction",
        )

        try:
            session = self.agent.create_session()

            response = await self.agent.run(
                f"""
                Execute the Clause Extraction stage.

                First load the skill named "clause-extraction"
                using load_skill.

                Perform clause extraction according to the loaded skill.

                Return only valid JSON matching this structure:
                {{
                "clauses": [
                    {{
                    "section": "string",
                    "category": "string",
                    "original_text": "string",
                    "reason": "string"
                    }}
                ]
                }}

                Agreement filename:
                {document.filename}

                Original agreement:
                {document.content}
                """,
                session=session,
                tools=self.tools,
            )

            if response.user_input_requests:
                raise RuntimeError(
                    "Clause extraction requires tool approval."
                )

            if not response.text:
                raise RuntimeError(
                    "Clause extraction returned empty text."
                )

            result = parse_json_response(
                response.text,
                ClauseExtractionResult,
            )

            validate_clauses(document, result)

            # Verifies that the required skill was recorded.
            self.telemetry.finish_stage()

            # Preserve the original agreement and validated clauses.
            handoff = ClauseExtractionHandoff(
                agreement=document,
                clauses=result,
            )

            # Send the validated agreement and clauses to Financial Risk.
            await ctx.send_message(handoff)

        except Exception as error:
            if self.telemetry._active is not None:
                self.telemetry.finish_stage(error)
            raise


class FinancialRiskExecutor(Executor):
    """Analyze financial risks using the existing agent and MCP tools."""

    def __init__(self, agent, tools, telemetry: WorkflowTelemetry):
        super().__init__(id="financial_risk")
        self.agent = agent
        self.tools = tools
        self.telemetry = telemetry

    @handler
    async def analyze(
        self,
        handoff: ClauseExtractionHandoff,
        ctx: WorkflowContext[FinancialRiskHandoff],
    ) -> None:
        self.telemetry.start_stage(
            "Financial Risk",
            expected_skill="financial-risk",
        )

        try:
            session = self.agent.create_session()

            response = await self.agent.run(
                f"""
                Execute the Financial Risk Analysis stage.

                First load the skill named "financial-risk"
                using load_skill.

                Perform the analysis according to the loaded skill.
                Use the available MCP tools when required by the skill.

                Return only valid JSON matching this structure:
                {{
                "risks": [
                    {{
                    "section": "string",
                    "risk": "string",
                    "business_impact": "string",
                    "risk_level": "Low | Medium | High | Undetermined",
                    "recommended_action": "string"
                    }}
                ],
                "exposure": {{
                    "fees_paid_last_12_months": 0,
                    "estimated_loss": 0,
                    "liability_cap": 0,
                    "amount_above_cap": 0,
                    "currency": "string",
                    "hypothetical": true
                }},
                "exposure_explanation": "string"
                }}

                The numeric zeros above are schema placeholders,
                not values to use in the analysis.

                Extracted clauses:
                {handoff.clauses.model_dump_json(indent=2)}

                Original agreement:
                {handoff.agreement.content}
                """,
                session=session,
                tools=self.tools,
            )

            if response.user_input_requests:
                raise RuntimeError(
                    "Financial Risk requires tool approval."
                )

            if not response.text:
                raise RuntimeError(
                    "Financial Risk returned empty text."
                )

            result = parse_json_response(
                response.text,
                FinancialRiskResult,
            )
            
            validate_financial_risks(handoff.clauses, result)

            # Require an observed calculator invocation.
            active_trace = self.telemetry._active

            if active_trace is None:
                raise RuntimeError("Financial Risk telemetry is missing.")

            calculator_called = any(
                "calculate_financial_exposure" in tool_name
                for tool_name in active_trace.mcp_tools
            )

            if not calculator_called:
                raise RuntimeError(
                    "Financial Risk failed: required MCP calculator was not called."
                )

            handoff_to_compliance = FinancialRiskHandoff(
                agreement=handoff.agreement,
                clauses=handoff.clauses,
                financial_risks=result,
            )

            # Mark Financial Risk as completed before starting the next stage.
            self.telemetry.finish_stage()

            await ctx.send_message(handoff_to_compliance)

        except Exception as error:
            if self.telemetry._active is not None:
                self.telemetry.finish_stage(error)
            raise


class ComplianceAnalysisExecutor(Executor):
    """Analyze compliance gaps using the shared MAF agent."""

    def __init__(self, agent, tools, telemetry: WorkflowTelemetry):
        super().__init__(id="compliance_analysis")
        self.agent = agent
        self.tools = tools
        self.telemetry = telemetry

    @handler
    async def analyze(
        self,
        handoff: FinancialRiskHandoff,
        ctx: WorkflowContext[ComplianceAnalysisHandoff],
    ) -> None:
        self.telemetry.start_stage(
            "Compliance Analysis",
            expected_skill="compliance-analysis",
        )

        try:
            # Fresh session, same logical agent.
            session = self.agent.create_session()

            response = await self.agent.run(
                f"""
                Execute the Compliance Analysis stage.

                First load the skill named "compliance-analysis"
                using load_skill.

                Perform the analysis according to the loaded skill.

                Return only valid JSON matching this structure:
                {{
                "findings": [
                    {{
                    "section": null,
                    "concern": "string",
                    "supporting_text": null,
                    "potential_impact": "string",
                    "recommended_action": "string"
                    }}
                ],
                "overall_assessment": "string"
                }}

                Extracted clauses:
                {handoff.clauses.model_dump_json(indent=2)}

                Financial risk findings:
                {handoff.financial_risks.model_dump_json(indent=2)}

                Original agreement:
                {handoff.agreement.content}
                """,
                session=session,
                tools=self.tools,
            )

            if response.user_input_requests:
                raise RuntimeError(
                    "Compliance Analysis requires tool approval."
                )

            if not response.text or not response.text.strip():
                raise RuntimeError(
                    "Compliance Analysis returned empty text."
                )

            result = parse_json_response(
                response.text,
                ComplianceAnalysisResult,
            )

            validate_compliance(handoff.clauses, result)

            handoff_to_report = ComplianceAnalysisHandoff(
                agreement=handoff.agreement,
                clauses=handoff.clauses,
                financial_risks=handoff.financial_risks,
                compliance=result,
            )

            # Validate skill usage and close the stage once.
            self.telemetry.finish_stage()

            await ctx.send_message(handoff_to_report)

        except Exception as error:
            if self.telemetry._active is not None:
                self.telemetry.finish_stage(error)
            raise

class FinalReportExecutor(Executor):
    """Assemble validated stage outputs without another agent call."""

    def __init__(self, telemetry: WorkflowTelemetry):
        super().__init__(id="final_report")
        self.telemetry = telemetry

    @handler
    async def build_report(
        self,
        handoff: ComplianceAnalysisHandoff,
        ctx: WorkflowContext[None, AgreementAnalysisReport],
    ) -> None:
        self.telemetry.start_stage("Final Report")

        try:
            report = AgreementAnalysisReport(
                agreement=handoff.agreement,
                clauses=handoff.clauses,
                financial_risks=handoff.financial_risks,
                compliance=handoff.compliance,
            )

            self.telemetry.finish_stage()
            await ctx.yield_output(report)

        except Exception as error:
            if self.telemetry._active is not None:
                self.telemetry.finish_stage(error)
            raise
