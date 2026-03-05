from ..models import ToolExecutionSpec

RETRIEVE_RUNBOOK_SPEC = ToolExecutionSpec(
    name="retrieve_runbook",
    arguments={
        "query": "string",
        "top_k": "string",
    },
    timeout_ms=200,
    max_retries=2,
    backoff_ms=50,
)