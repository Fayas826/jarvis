import time
from typing import Dict, Any, List, Optional
from core.orchestration.lifecycle_record import TaskLifecycleRecord
from core.orchestration.persistence import atomic_write, safe_load

def write_episodic_memory(record: Optional[TaskLifecycleRecord], episodic_path: str):
    """Append a summary episode to the persistent episodic memory store."""
    if not record:
        return
    episodes = safe_load(episodic_path, [])
    # Deduplicate by plan_id
    episodes = [e for e in episodes if e.get("plan_id") != record.plan_id]
    episode = {
        "plan_id": record.plan_id,
        "objective": record.objective,
        "intent": record.intent,
        "final_status": record.status,
        "node_count": len(record.nodes),
        "completed_nodes": sum(1 for n in record.nodes.values() if n.get("status") == "COMPLETED"),
        "failed_nodes": sum(1 for n in record.nodes.values() if n.get("status") == "FAILED"),
        "tool_history_count": len(record.tool_history),
        "error_count": len(record.error_history),
        "recovery_count": len(record.recovery_history),
        "created_at": record.created_at,
        "completed_at": time.time(),
    }
    episodes.append(episode)
    # Keep last 200 episodes
    if len(episodes) > 200:
        episodes = episodes[-200:]
    atomic_write(episodic_path, episodes)
    print(f"[EPISODIC_MEMORY] Episode recorded: {record.plan_id}")

def retrieve_episodic_history(episodic_path: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieve most recent episodes for use in future planning/routing."""
    episodes = safe_load(episodic_path, [])
    return episodes[-limit:]

def find_similar_episodes(episodic_path: str, objective: str, limit: int = 3) -> List[Dict[str, Any]]:
    """Find past episodes with similar objectives (simple keyword match)."""
    episodes = safe_load(episodic_path, [])
    keywords = set(objective.lower().split())
    scored = []
    for ep in episodes:
        ep_words = set(ep.get("objective", "").lower().split())
        overlap = len(keywords & ep_words)
        if overlap > 0:
            scored.append((overlap, ep))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [ep for _, ep in scored[:limit]]
