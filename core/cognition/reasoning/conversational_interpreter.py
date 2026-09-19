"""
Phase 34.5 — Conversational Interpreter
Resolves pronouns, references, and corrections using ConversationalContext.

DESIGN:
- Local pattern matching handles common correction/reference patterns fast.
- LLM disambiguation is used only when local matching is insufficient.
- The interpreter is a PURE TEXT LAYER — it returns an enriched InterpretedIntent.
- It does NOT execute actions, approve actions, or bypass safety.

SAFETY NOTE:
- Screen content / application text is marked as UNTRUSTED.
- Only explicit user utterances are treated as instructions.
- The interpreter does NOT have access to the Safety Kernel.
"""

import re
import time
import dataclasses
from typing import Optional, List, Dict, Any

from core.cognition.memory.context_memory import ConversationalContext, conversational_context


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclasses.dataclass
class InterpretedIntent:
    """Enriched representation of a user utterance after context resolution."""
    raw_utterance: str
    resolved_utterance: str          # after pronoun/reference resolution
    intent_type: str                 # COMMAND | CORRECTION | QUERY | AMBIGUOUS
    is_correction: bool = False
    correction_target: Optional[str] = None   # what the user wants changed
    referenced_entity: Optional[str] = None   # "it", "that", "the other one"
    confidence: float = 1.0
    resolution_method: str = "none"  # "pattern" | "context_lookup" | "llm" | "none"
    context_used: List[str] = dataclasses.field(default_factory=list)
    trusted: bool = True             # False if utterance originates from screen text


# ---------------------------------------------------------------------------
# Correction pattern library
# ---------------------------------------------------------------------------

_CORRECTION_PATTERNS = [
    # "No, ..."  /  "No wait, ..."  /  "Actually, ..."
    re.compile(r"^(no[,\s]|no wait[,\s]|actually[,\s]|wait[,\s])", re.IGNORECASE),
    # "That's wrong" / "That was wrong"
    re.compile(r"that'?s? (wrong|not right|incorrect|the wrong)", re.IGNORECASE),
    # "I meant ..." / "I mean ..."
    re.compile(r"^i ?meant?\s", re.IGNORECASE),
    # "Not that one" / "Not that" / "Not this"
    re.compile(r"^not (that|this|the (other|one|left|right|top|bottom))", re.IGNORECASE),
    # "Go back" / "Undo that" / "Cancel that"
    re.compile(r"^(go back|undo that|cancel that|revert|try again|start over)", re.IGNORECASE),
]

_REFERENCE_MAP = {
    # pronouns/demonstratives → entity type hints
    r"\bit\b": "previous_target",
    r"\bthat\b": "previous_target",
    r"\bthis\b": "current_element",
    r"\bthere\b": "previous_location",
    r"\bthe other one\b": "alternate_candidate",
    r"\bthe same\b": "previous_action",
    r"\bdo that again\b": "repeat_last",
    r"\bthere\b": "previous_location",
    r"\bsave it\b": "save_previous_target",
    r"\bopen it\b": "open_previous_target",
    r"\bclick it\b": "click_previous_target",
}

# Phrases that signal the utterance is referencing screen text — treat as UNTRUSTED
_SCREEN_TEXT_TRUST_SIGNALS = [
    re.compile(r"(the page says|screen shows|it says|the website says|the popup says)", re.IGNORECASE),
]


# ---------------------------------------------------------------------------
# Interpreter
# ---------------------------------------------------------------------------

class ConversationalInterpreter:
    """
    Resolves user utterances against conversational context.

    Phase 34.5 capabilities:
    A. Correction detection
    B. Pronoun/reference resolution
    C. Context-aware command expansion
    D. Trusted vs. untrusted source distinction
    E. LLM-assisted disambiguation (graceful fallback)
    """

    def __init__(self, context: ConversationalContext):
        self._ctx = context

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def interpret(self, raw_utterance: str) -> InterpretedIntent:
        """Synchronous interpretation using pattern matching only.

        For complex cases where LLM disambiguation is needed, callers should
        use `interpret_async`.
        """
        start = time.time()
        utterance = raw_utterance.strip()

        # ---- Trust check ----
        trusted = self._is_trusted(utterance)

        # ---- Correction detection ----
        is_correction, correction_target = self._detect_correction(utterance)

        # ---- Reference resolution ----
        resolved, referenced_entity, resolution_method, ctx_used = self._resolve_references(
            utterance, is_correction
        )

        # ---- Intent classification ----
        intent_type = self._classify_intent(utterance, is_correction)

        # ---- Confidence ----
        confidence = self._score_confidence(
            is_correction, resolution_method, referenced_entity, ctx_used
        )

        result = InterpretedIntent(
            raw_utterance=raw_utterance,
            resolved_utterance=resolved,
            intent_type=intent_type,
            is_correction=is_correction,
            correction_target=correction_target,
            referenced_entity=referenced_entity,
            confidence=confidence,
            resolution_method=resolution_method,
            context_used=ctx_used,
            trusted=trusted,
        )

        elapsed = (time.time() - start) * 1000
        print(
            f"[CONV_INTERPRETER] '{raw_utterance[:60]}' -> type={intent_type}, "
            f"correction={is_correction}, confidence={confidence:.2f}, "
            f"method={resolution_method}, latency={elapsed:.1f}ms"
        )
        return result

    async def interpret_async(self, raw_utterance: str) -> InterpretedIntent:
        """Pattern-first interpretation, LLM fallback for ambiguous cases."""
        intent = self.interpret(raw_utterance)
        if intent.intent_type == "AMBIGUOUS" and intent.confidence < 0.60:
            intent = await self._llm_disambiguate(intent)
        return intent

    # ------------------------------------------------------------------
    # Correction detection
    # ------------------------------------------------------------------

    def _detect_correction(self, utterance: str):
        for pat in _CORRECTION_PATTERNS:
            m = pat.search(utterance)
            if m:
                # What are they correcting? Strip the correction prefix
                remainder = utterance[m.end():].strip().strip(",").strip()
                return True, remainder or None
        return False, None

    # ------------------------------------------------------------------
    # Reference resolution
    # ------------------------------------------------------------------

    def _resolve_references(self, utterance: str, is_correction: bool):
        recent = self._ctx.get_recent(5)
        ctx_used = []
        referenced_entity = None
        resolved = utterance
        method = "none"

        # Check for known reference patterns
        for pattern_str, entity_type in _REFERENCE_MAP.items():
            if re.search(pattern_str, utterance, re.IGNORECASE):
                referenced_entity = entity_type

                # Try to resolve against recent context
                resolution = self._lookup_entity_in_context(entity_type, recent)
                if resolution:
                    # Replace the vague reference with the concrete entity
                    resolved = re.sub(
                        pattern_str, resolution, utterance, flags=re.IGNORECASE
                    )
                    ctx_used.append(resolution)
                    method = "context_lookup"
                else:
                    method = "pattern"
                break

        if method == "none" and not is_correction:
            method = "none"

        return resolved, referenced_entity, method, ctx_used

    def _lookup_entity_in_context(self, entity_type: str, turns: list) -> Optional[str]:
        """Look backwards through recent turns for a concrete entity to substitute."""
        # Reverse to find most recent first
        for turn in reversed(turns):
            if turn["role"] not in ("user", "assistant"):
                continue
            content = turn["content"]
            # For target-type references: look for nouns previously mentioned
            if entity_type in ("previous_target", "current_element"):
                # Find capitalized nouns or quoted strings
                m = re.search(r'"([^"]+)"', content)
                if m:
                    return m.group(1)
                m = re.search(r"'([^']+)'", content)
                if m:
                    return m.group(1)
            if entity_type == "previous_action":
                # Return the last assistant turn's action summary
                if turn["role"] == "assistant":
                    return content[:60]
            if entity_type == "repeat_last":
                if turn["role"] == "user":
                    return content
        return None

    # ------------------------------------------------------------------
    # Intent classification
    # ------------------------------------------------------------------

    def _classify_intent(self, utterance: str, is_correction: bool) -> str:
        if is_correction:
            return "CORRECTION"
        if re.search(r"\b(what|who|where|when|why|how|is|are|can|does)\b", utterance, re.IGNORECASE):
            if "?" in utterance or utterance.split()[0].lower() in ("what", "who", "where", "when", "why", "how"):
                return "QUERY"
        if re.search(r"\b(open|click|type|search|go|navigate|find|save|close|move|drag|scroll|press|launch)\b",
                     utterance, re.IGNORECASE):
            return "COMMAND"
        return "AMBIGUOUS"

    # ------------------------------------------------------------------
    # Trust check — screen content vs. user instruction
    # ------------------------------------------------------------------

    def _is_trusted(self, utterance: str) -> bool:
        """Returns False if the utterance appears to describe screen text, not a user command."""
        for pat in _SCREEN_TEXT_TRUST_SIGNALS:
            if pat.search(utterance):
                return False
        return True

    # ------------------------------------------------------------------
    # Confidence scoring
    # ------------------------------------------------------------------

    def _score_confidence(self, is_correction: bool, method: str,
                          referenced_entity: Optional[str], ctx_used: List[str]) -> float:
        score = 1.0
        if referenced_entity and method == "pattern":
            score -= 0.25  # reference detected but not resolved
        elif referenced_entity and method == "context_lookup" and ctx_used:
            score -= 0.05  # resolved, small uncertainty
        if is_correction and method == "none":
            score -= 0.10
        return max(0.0, min(1.0, score))

    # ------------------------------------------------------------------
    # LLM disambiguation (async, graceful fallback)
    # ------------------------------------------------------------------

    async def _llm_disambiguate(self, intent: InterpretedIntent) -> InterpretedIntent:
        """Ask the LLM to clarify an ambiguous utterance using conversation history."""
        try:
            from core.cognition.reasoning.brain import brain
            ctx_str = self._ctx.get_context_string(5)
            prompt = (
                "You are a conversational intent resolver. "
                "Given the conversation history and the current user utterance, "
                "return a single JSON object:\n"
                '{"resolved": "<clarified instruction>", "intent_type": "COMMAND|CORRECTION|QUERY", '
                '"confidence": 0.0}\n\n'
                f"HISTORY:\n{ctx_str}\n\n"
                f"CURRENT: {intent.raw_utterance}\n\n"
                "Return ONLY valid JSON."
            )
            res = await brain.get_ai_response(prompt)
            payload = res.get("response") or res.get("payload") or {}
            if isinstance(payload, dict) and "resolved" in payload:
                intent.resolved_utterance = payload["resolved"]
                intent.intent_type = payload.get("intent_type", intent.intent_type)
                intent.confidence = float(payload.get("confidence", 0.70))
                intent.resolution_method = "llm"
        except Exception as e:
            print(f"[CONV_INTERPRETER] LLM disambiguation failed (non-fatal): {e}")
        return intent


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

conversational_interpreter = ConversationalInterpreter(conversational_context)
