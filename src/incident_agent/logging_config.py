import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os

class ColorFormatter(logging.Formatter):
    RED = "\033[31m"
    YELLOW = "\033[33m"
    RESET = "\033[0m"

    def format(self, record):
        message = super().format(record)

        if record.levelno >= logging.ERROR:
            return f"{self.RED}{message}{self.RESET}"
        elif record.levelno == logging.WARNING:
            return f"{self.YELLOW}{message}{self.RESET}"
        return message

def get_log_dir() -> Path:
    # 1. Allow override via environment variable
    env_path = os.getenv("INCIDENT_AGENT_LOG_DIR")
    if env_path:
        path = Path(env_path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    # 2. Default: project_root/logs/
    project_root = Path(__file__).resolve().parents[2]
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    return log_dir

   
def setup_logging():
    log_dir = get_log_dir()
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / "incident_agent.log"

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    logger.propagate = False


    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5_000_000,
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    color_formatter = ColorFormatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(color_formatter)
    logger.addHandler(console_handler)

    noisy_libs = [
        "websockets",
        "asyncio",
        "urllib3",
        "httpx",
        "aiohttp",
    ]
    for lib in noisy_libs:
        logging.getLogger(lib).setLevel(logging.ERROR)

