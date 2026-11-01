# main.py
# Runs one Microsoft Agent Framework agent.
# The agent discovers two MCP tools and chooses when to call them.
# Three Agent Skills execute in a controlled sequential workflow.
# Fresh sessions isolate stages; Python state passes their outputs.

import asyncio
import sys
from pathlib import Path

from agent_framework import (
    MCPStdioTool,
    SkillsProvider,
    create_harness_agent,
    function_middleware,
)
from agent_framework.openai import OpenAIChatClient


@function_middleware
async def trace_skill_load(context, call_next):
    """Trace Agent Skill loading and MCP tool calls."""

    tool_name = context.function.name

    if tool_name == "load_skill":
        print(
            f"Tool: load_skill, "
            f"skill: {context.arguments.get('skill_name')}"
        )

    if "get_agreement" in tool_name:
        print(f"Agent MCP tool call: {tool_name}")

    if "calculate_financial_exposure" in tool_name:
        print(f"Agent MCP tool call: {tool_name}")

    await call_next()


async def retrieve_agreement(agent, tools):
    """Let the agent select an MCP tool to retrieve the agreement."""

    print("\n===== AGENT MCP RETRIEVAL =====")

    session = agent.create_session()

    response = await agent.run(
        """
        Retrieve the complete agreement named supplier_agreement.txt.

        Use the appropriate available MCP tool to retrieve it.
        Do not invent, summarize, or modify the agreement.
        Return the complete retrieved agreement text.
        """,
        session=session,
        tools=tools,
    )

    if response.user_input_requests:
        raise RuntimeError(
            "Agreement retrieval requires tool approval."
        )

    if not response.text or not response.text.strip():
        raise RuntimeError(
            "The agent returned no agreement text."
        )

    return response.text


async def run_stage(agent, stage_name, skill_name, task, tools):
    """Run one analysis stage with all discovered MCP tools available."""

    print(f"\n===== {stage_name} =====")

    session = agent.create_session()

    prompt = f"""
    You are executing the {stage_name} stage.

    First, load the skill named "{skill_name}" using load_skill.
    Apply its instructions to the task below.

    You may use the available MCP tools when relevant.
    Do not call tools unnecessarily.

    Perform ONLY this stage's task.
    Do not invent agreement terms or unsupported findings.

    Task:
    {task}
    """

    response = await agent.run(
        prompt,
        session=session,
        tools=tools,
    )

    if response.user_input_requests:
        raise RuntimeError(
            f"{stage_name} stopped because a tool needs approval."
        )

    if not response.text or not response.text.strip():
        raise RuntimeError(
            f"{stage_name} returned no output."
        )

    print(response.text)
    return response.text


async def main():
    """Retrieve an agreement and run three sequential analysis stages."""

    project_folder = Path(__file__).parent
    skills_folder = project_folder / "skills"
    server_path = project_folder / "mcp_server.py"

    # Create one agent for the entire workflow.
    agent = create_harness_agent(
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
        middleware=[trace_skill_load],
        auto_approval_rules=[
            SkillsProvider.read_only_tools_auto_approval_rule
        ],
    )

    # Keep the MCP connection open for the entire workflow.
    async with MCPStdioTool(
        name="agreement-tools",
        command=sys.executable,
        args=[str(server_path)],
        load_prompts=False,
    ) as mcp:

        # Dynamically discover all available MCP tools.
        # No hardcoded filtering by tool name.
        tools = mcp.functions

        print("\n===== AVAILABLE MCP TOOLS =====")
        for tool in tools:
            print(f"- {tool.name}")

        # STEP 1: Agent chooses a tool to retrieve the agreement.
        agreement = await retrieve_agreement(agent, tools)

        # Shared deterministic workflow state.
        state = {
            "agreement": agreement,
            "clauses": None,
            "financial_risks": None,
            "compliance_findings": None,
        }

        # STEP 2: Clause Extraction Skill.
        state["clauses"] = await run_stage(
            agent,
            "Clause Extraction",
            "clause-extraction",
            f"""
            Extract relevant contractual clauses.
            Preserve their original wording and section references.

            Agreement:
            {state["agreement"]}
            """,
            tools,
        )

        # STEP 3: Financial Risk Skill.
        state["financial_risks"] = await run_stage(
            agent,
            "Financial Risk",
            "financial-risk",
            f"""
            Analyze the extracted clauses for financial risks.
            Explain business impact and recommend actions.

            A financial exposure calculator is available.

            Call it only when BOTH required numerical inputs
            are available and supported by evidence:
            1. Fees paid during the previous 12 months.
            2. Estimated financial loss.

            Never invent financial amounts.

            If either input is missing, explain why financial
            exposure cannot be calculated.

            Clearly distinguish hypothetical calculations
            from actual financial exposure and legal recovery.

            Use "Undetermined" when risk severity cannot
            be justified.

            Extracted clauses:
            {state["clauses"]}

            Original agreement:
            {state["agreement"]}
            """,
            tools,
        )

        # STEP 4: Compliance Analysis Skill.
        state["compliance_findings"] = await run_stage(
            agent,
            "Compliance Analysis",
            "compliance-analysis",
            f"""
            Identify compliance concerns supported by the agreement.
            Explain which concerns require more information.
            Do not claim a compliance violation without evidence.

            Extracted clauses:
            {state["clauses"]}

            Financial findings:
            {state["financial_risks"]}

            Original agreement:
            {state["agreement"]}
            """,
            tools,
        )

    # STEP 5: Consolidate the report without another model call.
    print("\n===== FINAL AGREEMENT REPORT =====")

    for heading, key in [
        ("1. Contractual Clauses", "clauses"),
        ("2. Financial Risks", "financial_risks"),
        ("3. Compliance Findings", "compliance_findings"),
    ]:
        print(f"\n{heading}\n")
        print(state[key])


if __name__ == "__main__":
    asyncio.run(main())
