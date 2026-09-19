"""
Phase 34 Track 3 — Memory & Conversational Context Evolution (MODULARIZED)
============================================================

This file has been modularized to prevent the "God Object" anti-pattern.
All core memory classes have been separated into the `evolved/` package.
This file now serves as a backward-compatibility facade.
"""

from .evolved import (
    EpisodicTaskHistory,
    EntityRegistry,
    SessionMemory,
    MemoryConflictResolver,
    ConflictResolution,
    PrivacyGuard,
    EvolvingConversationalContext,
    privacy_guard,
    conflict_resolver,
    episodic_history,
    entity_registry,
    session_memory,
    evolving_context,
)
