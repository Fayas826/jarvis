import uuid

from .episodic import EpisodicTaskHistory
from .entity import EntityRegistry
from .session import SessionMemory
from .conflict import MemoryConflictResolver, ConflictResolution
from .privacy import PrivacyGuard
from .conversational import EvolvingConversationalContext

_default_session_id = uuid.uuid4().hex

privacy_guard = PrivacyGuard()
conflict_resolver = MemoryConflictResolver()
episodic_history = EpisodicTaskHistory(session_id=_default_session_id)
entity_registry = EntityRegistry(session_id=_default_session_id)
session_memory = SessionMemory(session_id=_default_session_id)
evolving_context = EvolvingConversationalContext(
    privacy_guard=privacy_guard,
    conflict_resolver=conflict_resolver,
)

__all__ = [
    "EpisodicTaskHistory",
    "EntityRegistry",
    "SessionMemory",
    "MemoryConflictResolver",
    "ConflictResolution",
    "PrivacyGuard",
    "EvolvingConversationalContext",
    "privacy_guard",
    "conflict_resolver",
    "episodic_history",
    "entity_registry",
    "session_memory",
    "evolving_context",
]
