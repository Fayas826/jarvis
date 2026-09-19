import os
import json
import time
import tempfile
from typing import Any

def atomic_write(path: str, data: Any):
    """Write JSON atomically using a temp file + os.replace with Windows backoff retries."""
    dir_ = os.path.dirname(path) or "."
    os.makedirs(dir_, exist_ok=True)
    tmp_fd, tmp_path = tempfile.mkstemp(dir=dir_, suffix=".tmp")
    try:
        with os.fdopen(tmp_fd, "w") as f:
            json.dump(data, f, indent=2)
        
        # Retry loop for Windows file-locking race conditions
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                os.replace(tmp_path, path)
                break
            except PermissionError as pe:
                if attempt == max_attempts - 1:
                    raise pe
                time.sleep(0.05 * (attempt + 1))
    except Exception as e:
        from core.reliability.system_logger import system_logger
        system_logger.log('ERROR', 'task_state', f'Unhandled exception: {e}')
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
        raise

def safe_load(path: str, default: Any) -> Any:
    """Load JSON, falling back to default on any error."""
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        from core.reliability.system_logger import system_logger
        system_logger.log('ERROR', 'task_state', f'Unhandled exception: {e}')
        return default
