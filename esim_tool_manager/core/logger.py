"""
Logging and Action Auditing System for eSim Automated Tool Manager
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

LOG_FILE_NAME = "esim_tool_manager.log"
ACTION_LOG_FILE_NAME = "esim_actions.jsonl"


class CustomFormatter(logging.Formatter):
    """Clean logging formatter with colored indicators where supported."""
    
    GREY = "\x1b[38;20m"
    GREEN = "\x1b[32;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"
    FORMAT = "%(asctime)s [%(levelname)s] %(message)s"

    FORMATS = {
        logging.DEBUG: GREY + FORMAT + RESET,
        logging.INFO: GREEN + FORMAT + RESET,
        logging.WARNING: YELLOW + FORMAT + RESET,
        logging.ERROR: RED + FORMAT + RESET,
        logging.CRITICAL: BOLD_RED + FORMAT + RESET
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.FORMAT)
        # Fallback to plain if terminal does not support ANSI or is redirected
        if not sys.stdout.isatty():
            log_fmt = self.FORMAT
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


class ActionAuditor:
    """Records structured audit records for UI and historical tracking."""
    
    def __init__(self, log_path: Optional[str] = None):
        self.log_path = log_path or os.path.abspath(ACTION_LOG_FILE_NAME)
        
    def record_action(self, action: str, tool: str, status: str, details: str = "", extra: Optional[Dict[str, Any]] = None):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "tool": tool,
            "status": status,
            "details": details,
            "extra": extra or {}
        }
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            sys.stderr.write(f"Failed to record action log: {e}\n")

    def get_recent_actions(self, limit: int = 50) -> List[Dict[str, Any]]:
        if not os.path.exists(self.log_path):
            return []
        records = []
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        records.append(json.loads(line))
            return records[-limit:]
        except Exception:
            return []


# Global instances
auditor = ActionAuditor()

def get_logger(name: str = "eSimToolManager", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)

        # File Handler (detailed)
        try:
            fh = logging.FileHandler(LOG_FILE_NAME, encoding="utf-8")
            fh.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            fh.setFormatter(file_formatter)
            logger.addHandler(fh)
        except Exception:
            pass

        # Stream Handler (console)
        sh = logging.StreamHandler(sys.stdout)
        sh.setLevel(level)
        sh.setFormatter(CustomFormatter())
        logger.addHandler(sh)

    return logger

logger = get_logger()
