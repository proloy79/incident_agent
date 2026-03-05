from .memory import MemoryText, Memory
from .observation  import Observation
from .planner import LLMPlanner, render_plan
import json
import logging


class IncidentAgent:
    def __init__(self, mcp_client):  
        self.logger = logging.getLogger(self.__class__.__name__)
        self.client=mcp_client
        self.memory = Memory()
        self.planner = LLMPlanner()

    async def handle_incident(self, observation: Observation):
        self.logger.info(f"Incident Agent called with prompt : {observation.text}\n")
        memory_snippet = self.memory.retrieve_topk(query=observation.text, k=1)
        plan = self.planner.plan(observation.text, memory_snippet)

        self.logger.info(f"Plan returned by llm is: \n{render_plan(plan["steps"])}\n")
        
        #self.logger.info('---------------------------------------------------')
        self.logger.info('Running through the PlanSteps returned by LLMPlanner')
        #self.logger.info('---------------------------------------------------')
        
        if "errors" in plan and plan["errors"]:            
            self.logger.info(
                "\n"
                "---------------------------------------------------\n"
                f"Payload:\n{json.dumps(step.input_schema, indent=4)}\n"
                f"Error:\n{json.dumps(plan["errors"], indent=4)}\n"
                "---------------------------------------------------"
            )            
            return  # or raise, or fallback
        
        stepNo=0
        
        
        for step in plan["steps"]:
                
            if step.call_type != "tool_call":
                continue
            
            stepNo+=1
            
            result = await self.client.call_tool(step.tool_name, step.input_schema)
                    
            for text in self._result_as_text(step.tool_name, step.input_schema, result):
                self.memory.add(text)
                self.logger.info(
                    "\n"
                    "---------------------------------------------------\n"
                    f"Step {stepNo}: {step.tool_name}\n"
                    f"Payload:\n{step.input_schema}\n"
                    f"Result:\n{text}\n"
                    "---------------------------------------------------"
                )                
            
        #self.logger.debug(f"Memory snapshot: {self.memory.to_json()}")
        
    def _diagnostic_as_text(self, host: str, check: str, result: dict) -> str:
        status = result.get("result", {}).get("result", {}).get("status", "unknown")
        stdout = result.get("result", {}).get("result", {}).get("data", {}).get("stdout", "")
        return f"[diagnostic] host={host}, check={check} → status={status}, details={stdout}"
        
    def _incident_summaryc_as_text(self, title: str, signals: list) -> MemoryText:
        sigs = ", ".join(signals)
        return f"[summary] {title} → signals: {sigs}"

    def _runbook_as_text(self, title: str, steps: list, confidence: float) -> str:
        step_text = " -> ".join(steps)
        return f"[runbook] {title} → {step_text} (confidence={confidence:.2f})"

    def _result_as_text(self, tool_name, arguments: dict, result: dict):   
        results = []
        if tool_name == "run_diagnostic":
            results.append(
                self._diagnostic_as_text(
                    host=arguments.get("host"),
                    check=arguments.get("check"),
                    result=result
                )
            )
    
        elif tool_name == "summarize_incident":
            results.append(
                self._incident_summaryc_as_text(
                    title=arguments.get("title"),
                    signals=arguments.get("signals", [])
                )
            )
    
        elif tool_name == "retrieve_runbook":            
            runbooks = result.get("result",{}).get("runbooks", [])
            #self.logger.debug(f"runbooks------------------{runbooks}")
            for rb in runbooks:
                results.append(
                    self._runbook_as_text(
                        title=rb.get("title"),
                        steps=rb.get("steps", []),
                        confidence=rb.get("confidence", 0.0)
                    )
                )
        return results