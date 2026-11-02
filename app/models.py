"""
models.py

Structured data contracts for the Agentic Skills Lab workflow.

These Pydantic models define the information passed between agreement retrieval, clause extraction, financial risk analysis, compliance analysis, and final reporting.

The contracts are independent of the agent implementation.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

class WorkflowModel(BaseModel):
    """Base contract that rejects unexpected fields."""
    model_config = ConfigDict(extra="forbid")

class AgreementDocument(WorkflowModel):
    """Agreement retrieved through the MCP server."""
    filename: str = Field(min_length=1)
    content: str = Field(min_length=1)

class ContractClause(WorkflowModel):
    """One extracted contractual clause."""
    section: str = Field(min_length=1)
    category: str = Field(min_length=1)
    original_text: str = Field(min_length=1)
    reason: str = Field(min_length=1)

class ClauseExtractionResult(WorkflowModel):
    """Structured output from the Clause Extraction skill."""
    clauses: list[ContractClause] = Field(min_length=1)

class FinancialRisk(WorkflowModel):
    """One financial risk associated with a contractual clause."""
    section: str = Field(min_length=1)
    risk: str = Field(min_length=1)
    business_impact: str = Field(min_length=1)
    risk_level: Literal[
        "Low",
        "Medium",
        "High",
        "Undetermined",
    ]
    recommended_action: str = Field(min_length=1)

class FinancialExposure(WorkflowModel):
    """Illustrative exposure calculated using the MCP tool."""
    fees_paid_last_12_months: float = Field(ge=0)
    estimated_loss: float = Field(ge=0)
    liability_cap: float = Field(ge=0)
    amount_above_cap: float = Field(ge=0)
    currency: str = Field(min_length=1)
    hypothetical: bool

class FinancialRiskResult(WorkflowModel):
    """Structured output from the Financial Risk skill."""
    risks: list[FinancialRisk]
    exposure: FinancialExposure | None = None
    exposure_explanation: str = Field(min_length=1)

class ComplianceFinding(WorkflowModel):
    """One evidence-based compliance concern."""
    section: str | None = None
    concern: str = Field(min_length=1)
    supporting_text: str | None = None
    potential_impact: str = Field(min_length=1)
    recommended_action: str = Field(min_length=1)

class ComplianceAnalysisResult(WorkflowModel):
    """Structured output from the Compliance Analysis skill."""
    findings: list[ComplianceFinding]
    overall_assessment: str = Field(min_length=1)

class AgreementAnalysisReport(WorkflowModel):
    """Validated final result of the sequential workflow."""
    agreement: AgreementDocument
    clauses: ClauseExtractionResult
    financial_risks: FinancialRiskResult
    compliance: ComplianceAnalysisResult


class ClauseExtractionHandoff(BaseModel):
    """
    Structured handoff from Clause Extraction to Financial Risk.
    Preserves both the original retrieved agreement and the validated extracted clauses.
    """
    model_config = ConfigDict(extra="forbid")

    agreement: AgreementDocument
    clauses: ClauseExtractionResult


class FinancialRiskHandoff(BaseModel):
    """
    Structured handoff from Financial Risk to Compliance Analysis.
    Preserves the original agreement, validated clauses,     and financial risk findings.
    """
    model_config = ConfigDict(extra="forbid")

    agreement: AgreementDocument
    clauses: ClauseExtractionResult
    financial_risks: FinancialRiskResult

class ComplianceAnalysisHandoff(WorkflowModel):
    """
    Structured handoff from Compliance Analysis to Final Report. Preserves all validated outputs from earlier stages.
    """
    agreement: AgreementDocument
    clauses: ClauseExtractionResult
    financial_risks: FinancialRiskResult
    compliance: ComplianceAnalysisResult
