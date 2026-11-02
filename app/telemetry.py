"""
telemetry.py

Lightweight execution tracing and skill verification for Agentic Skills Lab.

Records:
- Skill loading
- MCP tool calls
- Stage duration
- Stage success or failure
"""

from dataclasses import dataclass, field
from time import perf_counter

@dataclass
class StageTrace:
    """Execution details for one workflow stage."""
    stage: str
    expected_skill: str | None = None
    loaded_skills: list[str] = field(default_factory=list)
    mcp_tools: list[str] = field(default_factory=list)
    duration_ms: float = 0.0
    success: bool = False
    error: str | None = None

class WorkflowTelemetry:
    """Collect and verify execution traces across stages."""
    def __init__(self) -> None:
        self.stages: list[StageTrace] = []
        self._active: StageTrace | None = None
        self._started_at: float | None = None

    def start_stage(
        self,
        stage: str,
        expected_skill: str | None = None,
    ) -> None:
        """Begin tracing a workflow stage."""

        if self._active is not None:
            raise RuntimeError(
                f"Stage '{self._active.stage}' is still active."
            )

        self._active = StageTrace(
            stage=stage,
            expected_skill=expected_skill,
        )
        self._started_at = perf_counter()

    def record_skill(self, skill_name: str) -> None:
        """Record a skill loading event."""

        if self._active is not None:
            self._active.loaded_skills.append(skill_name)

    def record_mcp_tool(self, tool_name: str) -> None:
        """Record an MCP tool invocation."""

        if self._active is not None:
            self._active.mcp_tools.append(tool_name)

    def finish_stage(self, error: Exception | None = None) -> None:
        """Finish a stage and verify its expected skill."""

        if self._active is None or self._started_at is None:
            raise RuntimeError("No active stage to finish.")

        trace = self._active
        trace.duration_ms = round(
            (perf_counter() - self._started_at) * 1000,
            2,
        )

        if error is not None:
            trace.error = str(error)

        elif (
            trace.expected_skill is not None
            and trace.expected_skill not in trace.loaded_skills
        ):
            trace.error = (
                f"Expected skill '{trace.expected_skill}' "
                "was not loaded."
            )

        else:
            trace.success = True

        self.stages.append(trace)
        self._active = None
        self._started_at = None

        if trace.error is not None:
            raise RuntimeError(
                f"Stage '{trace.stage}' failed: {trace.error}"
            )

    def print_summary(self) -> None:
        """Print a compact execution summary."""

        print("\n===== WORKFLOW EXECUTION SUMMARY =====")

        for trace in self.stages:
            status = "PASS" if trace.success else "FAIL"

            print(
                f"{trace.stage}: {status} "
                f"({trace.duration_ms:.2f} ms)"
            )
            print(f"  Skills: {trace.loaded_skills}")
            print(f"  MCP tools: {trace.mcp_tools}")

            if trace.error:
                print(f"  Error: {trace.error}")
