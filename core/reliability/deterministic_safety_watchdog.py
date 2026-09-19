import os
import sys
import re
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [SAFETY_WATCHDOG] %(message)s")

class DeterministicSafetyWatchdog:
    """
    MindfulAI & CognitiveOS Deterministic Pre-Model Safety Gatekeeper.
    Intercepts risky OS/shell execution, destructive file operations, system corruption,
    and crisis/threat inputs BEFORE sending to LLMs or execution engines.
    """

    DESTRUCTIVE_COMMAND_PATTERNS = [
        r"\brmdir\s+/[sS]\s+/[qQ]\b",
        r"\bdel\s+/[fF]\s+/[sS]\s+/[qQ]\b",
        r"\bformat\s+[c-zC-Z]:\b",
        r"\brm\s+-rf\s+/\b",
        r"\bdrop\s+database\b",
        r"\bdrop\s+table\b",
        r"\breg\s+delete\b",
        r"\bshutdown\s+/[sStT]\b",
        r"\bRemove-Item\s+.*-Recurse\s+-Force\b",
        r"\bdiskpart\b",
        r"\bwbadmin\s+delete\b"
    ]

    CRISIS_THREAT_PATTERNS = [
        r"\bsuicide\b",
        r"\bkill myself\b",
        r"\bself harm\b",
        r"\bend my life\b",
        r"\bhurt myself\b"
    ]

    def __init__(self):
        self.compiled_destructive = [re.compile(p, re.IGNORECASE) for p in self.DESTRUCTIVE_COMMAND_PATTERNS]
        self.compiled_crisis = [re.compile(p, re.IGNORECASE) for p in self.CRISIS_THREAT_PATTERNS]
        logging.info("Deterministic Safety Watchdog initialized. Rule-based gatekeeper active.")

    def inspect_command(self, raw_input):
        """
        Inspects user input or agent action prior to model/execution processing.
        Returns (is_safe, category, reason_or_interception_msg)
        """
        text = str(raw_input).strip()

        # Check crisis / threat first
        for pat in self.compiled_crisis:
            if pat.search(text):
                logging.warning(f"SAFETY INTERCEPTION: Crisis/Threat pattern detected in: '{text}'")
                return False, "CRISIS_INTERCEPTION", (
                    "JARVIS SAFETY SENTINEL: Your safety is the highest priority. If you or someone you know is struggling or in distress, "
                    "help is available. Please contact a crisis hotline (call or text 988 in USA/Canada, or 91-9152987821 in India)."
                )

        # Check destructive OS commands
        for pat in self.compiled_destructive:
            if pat.search(text):
                logging.warning(f"SAFETY INTERCEPTION: Destructive command blocked: '{text}'")
                return False, "DESTRUCTIVE_COMMAND_BLOCKED", (
                    "JARVIS SAFETY WATCHDOG: Blocked potentially destructive system command. "
                    "Action requires explicit administrator hardware key confirmation."
                )

        return True, "SAFE", "Command verified safe for execution."

if __name__ == "__main__":
    watchdog = DeterministicSafetyWatchdog()
    print(watchdog.inspect_command("del /f /s /q c:\\windows"))
    print(watchdog.inspect_command("open chrome browser"))
