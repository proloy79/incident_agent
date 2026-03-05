import time
import logging

_logger=logging.getLogger()

async def retrieve_runbook_handler(payload: dict) -> dict:
    query = payload.get("query")
    top_k = payload.get("top_k")

    # Fake runbook database
    RUNBOOKS = [
        {
            "title": "Database outage",
            "steps": ["Check logs", "Restart DB", "Verify replication"],
            "confidence": 0.92,
        },
        {
            "title": "High CPU on webserver",
            "steps": ["Inspect top", "Restart service", "Check load balancer"],
            "confidence": 0.88,
        },
    ]

    # For now, return top_k items regardless of query
    return {"runbooks": RUNBOOKS[:top_k]}

async def run_diagnostic_handler(payload: dict) -> dict:
    latency = round(time.perf_counter() % 0.02, 4)
    return {
        "status": "ok",
        "data": {
            "command": payload.get("command"),
            "host": payload.get("host"),
            "stdout": "All pods healthy",
        },
        "metrics": {"latency_ms": latency * 1000},
    }
    


async def summarize_incident_handler(payload: dict) -> dict:
    alert_id = payload.get("alert_id")
    evidence = payload.get("evidence", [])

    if any("cpu" in e.lower() for e in evidence):
        severity = "high"
    elif any("warning" in e.lower() for e in evidence):
        severity = "medium"
    else:
        severity = "low"

    if any("cpu" in e.lower() for e in evidence):
        likely_cause = "High CPU usage detected"
    elif any("memory" in e.lower() for e in evidence):
        likely_cause = "Memory pressure or leak"
    else:
        likely_cause = "Insufficient evidence to determine cause"

    # generate summary
    if evidence:
        summary = (
            f"Incident {alert_id} shows {len(evidence)} evidence items. "
            f"Initial assessment suggests a {severity}-severity issue. "
            f"Likely cause: {likely_cause}."
        )
    else:
        summary = (
            f"Incident {alert_id} has no evidence provided. "
            "Unable to determine severity or likely cause."
        )
    #_logger.debug(likely_cause)
    return {
        "summary": summary,
        "severity": severity,
        "likely_cause": likely_cause,
    }