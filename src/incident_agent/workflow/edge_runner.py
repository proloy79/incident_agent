# AI Agents & Automation
# (c) Dr. Yves J. Hilpisch
# AI-Powered by GPT-5
"""Chapter 10: tiny edge loop with sandboxed state and budgets.

Local, deterministic loop; demonstrates ephemeral sandbox and audit log.
"""
from __future__ import annotations  # Future-proof typing.

import json  # Write a compact audit file.
import os  # Join paths.
import tempfile  # Ephemeral sandbox directory.
import time  # CPU guard.
from typing import Any, Dict, List  # Type hints.
import logging
from .observation import Observation
from .orchestrator import Orchestrator

class EdgeRunner:
    def __init__(self, mcp_client):
        self.orchestrator=Orchestrator(mcp_client)
        self.logger = logging.getLogger(self.__class__.__name__)

        
    async def execute(self, observation: Observation, max_turns: int = 3,  cpu_ms: int = 50):
        self.logger.info(f"EdgeRunner called with prompt : {observation.text}\n")
        
        notes: List[Dict[str, Any]] = []  # Collect audit entries.
        cpu_start = time.process_time()  # Start CPU timer.
        
        with tempfile.TemporaryDirectory() as tmp:  # Sandboxed folder.
            audit = os.path.join(tmp, "audit.jsonl")  # Audit path.
            state: Dict[str, Any] = {"goal": observation.text}  # Minimal state.
            for turn in range(1, max_turns + 1):  # Budgeted loop.
                # CPU guard: stop if over CPU budget.
                if int((time.process_time() - cpu_start) * 1000) > cpu_ms:
                    notes.append(
                        {"turn": turn, "action": "stop", "status": "cpu_budget"}
                    )
                    break  # Stop loop.
                
                result = await self.orchestrator.handle_incident(observation)                

                notes.append(
                    {"turn": turn, "action": observation.text, "status": "ok", "result": result}
                )
            # Persist compact audit file.
            with open(audit, "w", encoding="utf-8") as f:
                for n in notes:
                    self.logger.info(self._format_note(n))
                    f.write(json.dumps(n) + "\n")  # JSON lines.
            return {"notes": notes, "audit_path": audit}  # Return outcome.

    def _format_note(self, note: dict) -> str:
        result = note.get("result")
    
        # If result is a list, print each item on its own line
        if isinstance(result, list):
            result_text = "\n".join(f"{item}" for item in result)
        else:
            result_text = f"  {result}"
    
        return (
            "\n"
            "---------------------------------------------------\n"
            f"Turn: {note.get('turn')}\n"
            f"Action: {note.get('action')}\n"
            f"Status: {note.get('status')}\n"
            f"{result_text}\n"
            "---------------------------------------------------"
        )