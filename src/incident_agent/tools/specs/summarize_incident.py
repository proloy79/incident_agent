from ..models import ToolExecutionSpec

SUMMARIZE_INCIDENT_SPEC = ToolExecutionSpec(
    name="summarize_incident",
    arguments={        
        "title": "string",
        "signals": "string",
    },
    timeout_ms=200,
    max_retries=2,
    backoff_ms=50,
)