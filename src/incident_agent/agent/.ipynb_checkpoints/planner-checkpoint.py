from __future__ import annotations

from dataclasses import dataclass  # Lightweight records.
from typing import Dict, List  # Type hints for clarity.
import logging

@dataclass
class PlanStep:
    """One actionable step produced by the planner."""

    tool_name: str  # Name of the tool to invoke (e.g., "calculator").
    call_type: str
    input_schema: Dict[str, str]  # Key → hint (e.g., {"expression": "str"}).
    notes: str  # Short human note (≤ 12 words).
    
class LLMPlanner:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        #short term memory to store every tool call result for this particular incident to avoid repeating same steps
        # self.episodic = [] 

    def plan(self, incident_text: str, memory_snippet) -> Dict[str, Any]:
        """
        Get the plan from LLM, validate and return
        """        
        plan = self._fake_llm_plan(incident_text)            
        problems=self._validate_plan(plan["steps"])
        
        if problems:            
            return {
                "steps": [],
                "errors": problems
            } 
        #self.logger.info(f"in planner  ---------- {render_plan(plan["steps"])}")
        return plan

    def _fake_llm_plan(self, prompt: str) -> List[PlanStep]:
        """Return a short plan; stands in for a real LLM call.
    
        The prompt is ignored here; we return a fixed, well-formed plan to show the
        interface clearly.
        """
        host=''
        prompt_l = prompt.lower()

        if "host a" in prompt_l:
            host = "A"
        elif "host b" in prompt_l:
            host = "B"

            
        return {"steps" : [
            PlanStep(
                tool_name="run_diagnostic",
                call_type="tool_call",
                input_schema={"host": host, "check": "cpu_usage"},
                notes=f"Get CPU metrics for host {host}",
            ),
            PlanStep(
                tool_name="run_diagnostic",
                call_type="tool_call",
                input_schema={"host": host, "check": "top_processes"},
                notes="Identify top CPU-consuming processes",
            ),
            PlanStep(
                tool_name="retrieve_runbook",
                call_type="tool_call",
                input_schema={"query": f"cpu spike on host {host}", "top_k": 3},
                notes="Fetch relevant runbook steps for CPU spike scenarios",
            ),
            PlanStep(
                tool_name="summarize_incident",
                call_type="tool_call",
                input_schema={
                    "title": f"CPU spike on host {host}",
                    "signals": [
                        "cpu_usage",
                        "top_processes",
                        "runbook_guidance"
                    ]
                },
                notes="Summarize the findings",
            ),
        ]}
    
    
    def _validate_plan(self, steps: List[PlanStep]) -> List[str]:
        """Validate required fields and brief notes.
    
        Returns a list of problems; empty means the plan is acceptable.
        """
    
        problems: List[str] = []  # Collected validation issues.
        if not (1 <= len(steps) <= 5):  # Keep plans short and readable.
            problems.append("plan must have 1..5 steps")
        for i, s in enumerate(steps, start=1):
            if not s.tool_name:
                problems.append(f"step {i}: missing tool_name")
            if not s.input_schema:
                problems.append(f"step {i}: missing input_schema")
            if len(s.notes.split()) > 12:
                problems.append(f"step {i}: notes too long")
        return problems
    
    @staticmethod
    def render_plan(steps: List[PlanStep]) -> str:
        """Return a numbered plan for display/logging."""
    
        lines: List[str] = []  # Output buffer.
        for i, s in enumerate(steps, start=1):
            schema_keys = list(s.input_schema.keys())  # Ordered view for display.
            # Human-readable line.
            line = f"{i}. {s.tool_name} | schema={schema_keys} | {s.notes}"
            lines.append(line)  # Accumulate.
        return "\n".join(lines)  # Single printable block.

render_plan = LLMPlanner.render_plan