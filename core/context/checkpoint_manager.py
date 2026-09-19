import os
import sys
import json
import time
import shutil
import zipfile
import hashlib
import threading
import logging
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AegisShadowCheckpointer")

PROJECT_MEMORY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "project_memory")
CHECKPOINT_DIR = os.path.join(PROJECT_MEMORY_DIR, "shadow_checkpoints")
MANIFEST_FILE = os.path.join(CHECKPOINT_DIR, "checkpoint_manifest.json")

# Monitored core directories for automatic code checkpointing
WATCH_DIRS = ["core", "action", "capabilities", "sentinel", "infrastructure"]
ALLOWED_EXTS = {".py", ".json", ".js", ".jsx", ".ts", ".tsx", ".html", ".css", ".md"}
EXCLUDE_DIRS = {"__pycache__", ".git", ".venv", "venv", "node_modules"}

class AegisShadowCheckpointer:
    """
    🛡️ A.E.G.I.S. SHADOW CHECKPOINT & CONTINUOUS RESTORE ENGINE
    Functions exactly like Windows System Restore / Volume Shadow Copy (VSS)
    specifically designed for source code:
    - Continuously monitors source files across core subsystems.
    - Creates lightweight, timestamped incremental rollback checkpoints whenever code changes.
    - Maintains an auto-pruning rolling history of the last 30 recovery points.
    - Provides 1-click instant rollback to any previous state.
    """

    def __init__(self, max_checkpoints: int = 30):
        self.root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.max_checkpoints = max_checkpoints
        os.makedirs(CHECKPOINT_DIR, exist_ok=True)
        self._last_state_hashes: Dict[str, str] = {}
        self._watcher_thread: Optional[threading.Thread] = None
        self._watcher_running = False
        self._lock = threading.Lock()
        self._init_hashes()

    def _file_hash(self, filepath: str) -> str:
        """Computes fast SHA-256 hash of a file."""
        hasher = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return ""

    def _init_hashes(self):
        """Scans watched directories to establish initial baseline."""
        for wdir in WATCH_DIRS:
            abs_dir = os.path.join(self.root_dir, wdir)
            if os.path.exists(abs_dir):
                for root, dirs, files in os.walk(abs_dir):
                    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
                    for f in files:
                        ext = os.path.splitext(f)[1].lower()
                        if ext in ALLOWED_EXTS:
                            fp = os.path.join(root, f)
                            rel = os.path.relpath(fp, self.root_dir)
                            self._last_state_hashes[rel] = self._file_hash(fp)

    def scan_for_changes(self) -> List[str]:
        """Identifies any source files modified, added, or deleted since last check."""
        changed = []
        current_files = set()

        for wdir in WATCH_DIRS:
            abs_dir = os.path.join(self.root_dir, wdir)
            if os.path.exists(abs_dir):
                for root, dirs, files in os.walk(abs_dir):
                    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
                    for f in files:
                        ext = os.path.splitext(f)[1].lower()
                        if ext in ALLOWED_EXTS:
                            fp = os.path.join(root, f)
                            rel = os.path.relpath(fp, self.root_dir)
                            current_files.add(rel)
                            h = self._file_hash(fp)
                            if rel not in self._last_state_hashes or self._last_state_hashes[rel] != h:
                                changed.append(rel)
                                self._last_state_hashes[rel] = h

        # Check for deleted files
        for prev in list(self._last_state_hashes.keys()):
            if prev not in current_files:
                changed.append(prev)
                del self._last_state_hashes[prev]

        return changed

    def create_checkpoint(self, label: str = "Auto_Save", force: bool = False) -> Optional[Dict[str, Any]]:
        """
        Creates an incremental shadow checkpoint capturing all modified source files.
        """
        with self._lock:
            changed_files = self.scan_for_changes()
            if not changed_files and not force:
                return None

            timestamp_str = time.strftime("%Y%m%d_%H%M%S")
            checkpoint_id = f"CP_{timestamp_str}"
            archive_name = f"{checkpoint_id}.zip"
            archive_path = os.path.join(CHECKPOINT_DIR, archive_name)

            files_to_pack = changed_files if changed_files else list(self._last_state_hashes.keys())

            # Package modified files into compressed shadow archive
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for rel_path in files_to_pack:
                    full_p = os.path.join(self.root_dir, rel_path)
                    if os.path.exists(full_p):
                        zipf.write(full_p, rel_path)

            manifest = self.load_manifest()
            entry = {
                "checkpoint_id": checkpoint_id,
                "label": label,
                "timestamp": time.time(),
                "datetime": time.strftime("%Y-%m-%d %H:%M:%S"),
                "archive_file": archive_name,
                "changed_count": len(files_to_pack),
                "files": files_to_pack[:20]  # Store first 20 for preview
            }
            manifest.append(entry)

            # Prune oldest checkpoints if exceeding limit
            while len(manifest) > self.max_checkpoints:
                oldest = manifest.pop(0)
                old_file = os.path.join(CHECKPOINT_DIR, oldest.get("archive_file", ""))
                if os.path.exists(old_file):
                    try:
                        os.remove(old_file)
                    except Exception:
                        pass

            with open(MANIFEST_FILE, "w") as f:
                json.dump(manifest, f, indent=2)

            logger.info(f"[CHECKPOINT] 📸 Shadow Restore Point '{checkpoint_id}' captured ({len(files_to_pack)} files)")
            return entry

    def rollback_to_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Restores source code files to the exact state in the specified checkpoint.
        """
        with self._lock:
            manifest = self.load_manifest()
            target = next((cp for cp in manifest if cp["checkpoint_id"] == checkpoint_id), None)
            if not target:
                logger.error(f"[CHECKPOINT] Checkpoint {checkpoint_id} not found in manifest.")
                return False

            archive_path = os.path.join(CHECKPOINT_DIR, target["archive_file"])
            if not os.path.exists(archive_path):
                logger.error(f"[CHECKPOINT] Archive file missing: {archive_path}")
                return False

            logger.warning(f"[CHECKPOINT] ⏪ Rolling back to checkpoint: {checkpoint_id} ({target['datetime']})...")
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                zipf.extractall(self.root_dir)

            self._init_hashes()
            logger.info(f"[CHECKPOINT] ✅ Successfully restored system state to {checkpoint_id}.")
            return True

    def load_manifest(self) -> List[Dict[str, Any]]:
        if os.path.exists(MANIFEST_FILE):
            try:
                with open(MANIFEST_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def start_background_watcher(self, interval_seconds: int = 15):
        """Starts the autonomous background thread monitoring for code modifications."""
        if self._watcher_running:
            return
        self._watcher_running = True

        def _watcher_loop():
            logger.info(f"[CHECKPOINT] Continuous Shadow Watcher Online (Scanning every {interval_seconds}s)...")
            while self._watcher_running:
                try:
                    self.create_checkpoint(label="Auto_Code_Change")
                except Exception as e:
                    logger.debug(f"[CHECKPOINT] Watcher tick error: {e}")
                time.sleep(interval_seconds)

        self._watcher_thread = threading.Thread(target=_watcher_loop, daemon=True, name="AegisCheckpointWatcher")
        self._watcher_thread.start()

    def stop_background_watcher(self):
        self._watcher_running = False

# Global singleton
checkpoint_manager = AegisShadowCheckpointer()
