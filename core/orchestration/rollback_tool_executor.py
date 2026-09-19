import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List

from core.orchestration.world_state_engine import world_state_engine

PROJECT_MEMORY_DIR = Path("project_memory")
PROJECT_MEMORY_DIR.mkdir(exist_ok=True)


class RollbackToolExecutor:
    """Creates reversible tool execution records and blocks unsafe operations by default."""

    def __init__(self, ledger_path: Path | None = None):
        self.ledger_path = ledger_path or PROJECT_MEMORY_DIR / "tool_execution_ledger.json"
        if not self.ledger_path.exists():
            self._write([])

    def _read(self) -> List[Dict[str, Any]]:
        try:
            return json.loads(self.ledger_path.read_text(encoding="utf-8"))
        except Exception as e:
            from core.reliability.system_logger import system_logger
            system_logger.log('ERROR', 'rollback_tool_executor', f'Unhandled exception: {e}')
            return []

    def _write(self, rows: List[Dict[str, Any]]):
        temp = self.ledger_path.with_suffix(".tmp")
        temp.write_text(json.dumps(rows[-500:], indent=2), encoding="utf-8")
        os.replace(temp, self.ledger_path)

    def prepare(self, tool: str, intent: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        payload = payload or {}
        risk = world_state_engine.classify_action_risk(intent, payload)
        rollback = self._rollback_plan(tool, payload)
        record = {
            "id": f"tool-{uuid.uuid4().hex[:12]}",
            "tool": tool,
            "intent": intent,
            "payload": payload,
            "risk": risk,
            "rollback_plan": rollback,
            "status": "needs_approval" if risk["level"] in {"HIGH", "CRITICAL"} else "prepared",
            "created_at": time.time(),
            "executed_at": None,
            "rolled_back_at": None,
        }
        rows = self._read()
        rows.append(record)
        self._write(rows)
        world_state_engine.record_event("TOOL_PREPARED", record, "tool_executor")
        return record

    def mark_executed(self, execution_id: str, result: Dict[str, Any] | None = None) -> Dict[str, Any]:
        rows = self._read()
        for row in rows:
            if row["id"] == execution_id:
                if row["status"] == "needs_approval":
                    return {"status": "blocked", "reason": "approval_required", "record": row}
                row["status"] = "executed"
                row["executed_at"] = time.time()
                row["result"] = result or {"status": "external_execution_recorded"}
                self._write(rows)
                world_state_engine.record_event("TOOL_EXECUTED", row, "tool_executor")
                return {"status": "executed", "record": row}
        return {"status": "not_found"}

    def rollback(self, execution_id: str) -> Dict[str, Any]:
        rows = self._read()
        for row in rows:
            if row["id"] == execution_id:
                row["status"] = "rollback_requested"
                row["rolled_back_at"] = time.time()
                self._write(rows)
                world_state_engine.record_event("TOOL_ROLLBACK_REQUESTED", row, "tool_executor")
                return {"status": "rollback_requested", "rollback_plan": row.get("rollback_plan"), "record": row}
        return {"status": "not_found"}

    def ledger(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._read()[-limit:]

    def _rollback_plan(self, tool: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if "file_path" in payload:
            return {"type": "restore_file_backup", "file_path": payload["file_path"]}
        if tool in {"os_command", "powershell", "shell"}:
            return {"type": "manual_review_required", "reason": "command side effects unknown"}
        return {"type": "no_op", "reason": "read_only_or_external_verification"}


rollback_tool_executor = RollbackToolExecutor()
