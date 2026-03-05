import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(level=logging.INFO)

    log_file = log_dir / "incident_agent.log"
    root = logging.getLogger("IncidentAgent")
    root.setLevel(logging.DEBUG) 
    
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    
    handler = RotatingFileHandler(
        log_file,
        maxBytes=5_000_000,   # 5 MB
        backupCount=5
    )    
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)    
    root.addHandler(handler)

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    root.addHandler(console)

    root.propagate = False


