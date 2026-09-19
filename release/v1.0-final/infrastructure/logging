import logging
import logging.handlers
import json
import time
import os
import queue
import threading
import gzip
from datetime import datetime

# 🧿 O.M.E.G.A. SYSTEM_LOGGER_V2 (Async Rotating)
# Unified non-blocking structured logging.

LOG_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(LOG_DIR, "omega_system.log")

def gzip_rotator(source, dest):
    """Compresses the log file after rotation."""
    with open(source, "rb") as f_in:
        with gzip.open(f"{dest}.gz", "wb") as f_out:
            f_out.writelines(f_in)
    os.remove(source)

class OmegaLogger:
    def __init__(self):
        self.logger = logging.getLogger("OMEGA")
        self.logger.setLevel(logging.INFO)
        
        # 1. Base Rotating Handler (Daily rotation, keep 7 days)
        # We use TimedRotatingFileHandler for daily, and size limit in a wrapper if needed.
        # Here we use TimedRotatingFileHandler.
        trfh = logging.handlers.TimedRotatingFileHandler(
            LOG_FILE, when="D", interval=1, backupCount=7, encoding="utf-8"
        )
        trfh.rotator = gzip_rotator
        
        # 2. Async Queue Setup
        self.log_queue = queue.Queue(-1) # Infinite queue
        queue_handler = logging.handlers.QueueHandler(self.log_queue)
        
        # 3. Listener to offload I/O
        self.listener = logging.handlers.QueueListener(self.log_queue, trfh)
        self.listener.start()
        
        self.logger.addHandler(queue_handler)

    def log(self, level, component, event, metadata=None):
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "component": component,
            "event": event,
            "metadata": metadata or {}
        }
        # Non-blocking enqueue
        self.logger.info(json.dumps(payload))
        
        # Console output (optional, keeping it for visibility)
        color = "\033[94m" # Blue
        if level == "ERROR": color = "\033[91m"
        elif level == "WARNING": color = "\033[93m"
        elif level == "SUCCESS": color = "\033[92m"
        print(f"{color}[{level}] [{component}] {event}\033[0m")

    def stop(self):
        """Ensures all logs are flushed before shutdown."""
        self.listener.stop()

system_logger = OmegaLogger()
