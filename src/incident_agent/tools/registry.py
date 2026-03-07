from .tool_executor import ToolExecutor
from .models import ToolDefinition, ToolExecutionSpec
from .tool_executor import CircuitBreaker

class ToolDefinitionRegistry:
    def __init__(self):
        self._definitions = {}

    def register(self, name: str, definition: ToolDefinition):
        self._definitions[name] = definition

    def all_definitions(self):
        return list(self._definitions.values())

    def get(self, name: str):
        return self._definitions[name]

class ToolSpecRegistry:
    def __init__(self):
        self._run_specs = {}

    def register(self, name: str, spec: ToolExecutionSpec):
        self._run_specs[name] = spec
    
    def get(self, name: str):
        return self._run_specs[name]
        
class ToolExecutionRegistry:
    def __init__(self, definition_registry: ToolDefinitionRegistry, run_spec: ToolSpecRegistry, mcp_client):
        self.mcp_client = mcp_client
        self.tool_executors = {
            name: ToolExecutor(
                definition=definition,
                spec=run_spec.get(name),
                breaker=CircuitBreaker(),
                mcp_client=mcp_client,
            )
            for name, definition in definition_registry._definitions.items()
        }

    def execute(self, tool_name: str, args: dict):
        return self.tool_executors[tool_name].call_tool(args)