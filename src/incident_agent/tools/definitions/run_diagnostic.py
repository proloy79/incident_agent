from ..handlers import run_diagnostic_handler
from ..models import ToolMetadata, ToolDefinition

RUN_DIAGNOSTIC_DEF = ToolDefinition(
    metadata=ToolMetadata(
        name="run_diagnostic",
        description="Execute a diagnostic command on a target host.",
        expected_latency_ms=500,
        cost_units=3,
        risk_level="high",
        side_effects="executes-commands",
    ),
    input_schema={
        "type": "object",
        "properties": {
            "check": {"type": "string"},
            "host": {"type": "string"},
        },
        "required": ["command", "host"],
    },
    output_schema={
        "type": "object",
        "properties": {
            "stdout": {"type": "string"},
            "stderr": {"type": "string"},
            "exit_code": {"type": "integer"},
        },
        "required": ["stdout", "stderr", "exit_code"],
    },
    handler=run_diagnostic_handler
)