
"""
workflow.py

Native Microsoft Agent Framework orchestration.

Runs agreement retrieval and clause extraction using one
shared agent, dynamically discovered MCP tools, and
workflow-level telemetry.
"""

import asyncio
import sys
from pathlib import Path

from agent_framework import MCPStdioTool, WorkflowBuilder

from app.agent_factory import create_agreement_agent
from app.executors import (
    RetrievalExecutor,
    ClauseExtractionExecutor,
    FinancialRiskExecutor,
    ComplianceAnalysisExecutor,
    FinalReportExecutor,
)
from app.telemetry import WorkflowTelemetry


async def main():
    """Run the MAF workflow with telemetry enabled."""

    project_folder = Path(__file__).resolve().parent.parent
    server_path = project_folder / "mcp_server.py"

    # One telemetry collector for the entire workflow.
    telemetry = WorkflowTelemetry()

    # Exactly one MAF agent for all workflow stages.
    agent = create_agreement_agent(project_folder, telemetry)

    try:
        # Keep the MCP connection open throughout execution.
        async with MCPStdioTool(
            name="agreement-tools",
            command=sys.executable,
            args=[str(server_path)],
            load_prompts=False,
        ) as mcp:

            tools = mcp.functions

            print("\n===== AVAILABLE MCP TOOLS =====")
            for tool in tools:
                print(f"- {tool.name}")

            retrieval = RetrievalExecutor(agent, tools, telemetry)
            extraction = ClauseExtractionExecutor(agent, tools, telemetry)
            financial = FinancialRiskExecutor(agent, tools, telemetry)
            compliance = ComplianceAnalysisExecutor(agent, tools, telemetry)
            final_report = FinalReportExecutor(telemetry)

            workflow = (
                WorkflowBuilder(start_executor=retrieval)
                .add_edge(retrieval, extraction)
                .add_edge(extraction, financial)
                .add_edge(financial, compliance)
                .add_edge(compliance, final_report)
                .build()
            )

            print("\n===== STARTING MAF WORKFLOW =====")

            events = await workflow.run("supplier_agreement.txt")

            for event in events:
                if event.type == "output":
                    print("\n===== FINAL AGREEMENT ANALYSIS REPORT =====")
                    print(event.data)

    finally:
        # Print traces even when the workflow fails.
        telemetry.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
