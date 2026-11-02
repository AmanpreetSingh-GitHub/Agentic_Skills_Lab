"""
agent_factory.py

Creates the single Microsoft Agent Framework agent and connects its middleware events to workflow telemetry.
"""

from pathlib import Path

from agent_framework import (
    SkillsProvider,
    create_harness_agent,
    function_middleware,
)
from agent_framework.openai import OpenAIChatClient

from app.telemetry import WorkflowTelemetry

def create_tracing_middleware(telemetry: WorkflowTelemetry):

    @function_middleware
    async def trace_tool_call(context, call_next):
        tool_name = context.function.name

        await call_next()

        if tool_name == "load_skill":
            skill_name = context.arguments.get("skill_name")

            if skill_name:
                telemetry.record_skill(skill_name)

            print(f"Tool: load_skill, skill: {skill_name}")

        elif "get_agreement" in tool_name:
            telemetry.record_mcp_tool(tool_name)
            print(f"Agent MCP tool call: {tool_name}")
        
        elif "calculate_financial_exposure" in tool_name:
            telemetry.record_mcp_tool(tool_name)
            telemetry.calculator_result = context.result

            print(f"Agent MCP tool call: {tool_name}")

    return trace_tool_call

def create_agreement_agent(
    project_folder: Path,
    telemetry: WorkflowTelemetry,
):
    """Create one MAF agent with skills and telemetry middleware."""

    skills_folder = project_folder / "skills"

    telemetry.calculator_result = None

    return create_harness_agent(
        client=OpenAIChatClient(),
        agent_instructions="""
        You are an enterprise agreement analysis agent.

        Follow the requested stage and load its named skill.
        Use only the agreement and stage inputs provided.
        Never invent clauses or contractual facts.
        Clearly distinguish evidence from assumptions.

        Select MCP tools based on the current task.
        Do not call a tool unless it is relevant.
        Never invent financial amounts for calculations.
        """,
        disable_mode=True,
        disable_web_search=True,
        skills_paths=skills_folder,
        middleware=[create_tracing_middleware(telemetry)],
        auto_approval_rules=[
            SkillsProvider.read_only_tools_auto_approval_rule
        ],
    )
