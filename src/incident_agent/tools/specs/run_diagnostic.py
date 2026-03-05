from ..models import ToolExecutionSpec

RUN_DIAGNOSTIC_SPEC = ToolExecutionSpec(
    name="run_diagnostic",
    arguments={
        "host": "string",
        "check": "string",
    },
    timeout_ms=200,
    max_retries=2,
    backoff_ms=50,
)