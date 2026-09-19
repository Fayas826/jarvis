import time
import asyncio
import logging
import webbrowser
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from core.orchestration.swarm_message_board import SwarmMessageBoard
from core.orchestration.computer_use_agent import computer_use_agent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class VoiceToActionRouter:
    """
    Architect Tier - Voice Command Router
    Listens to the Swarm Message Board for VOICE_COMMAND payloads.
    Translates natural language text (e.g., "open youtube") into basic OS actions,
    and delegates complex tasks (e.g. "search book my show") to the VLM Computer Use Agent.
    """
    
    def __init__(self):
        self.board = SwarmMessageBoard()
        self.known_websites = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "github": "https://www.github.com",
            "chatgpt": "https://chat.openai.com",
            "netflix": "https://www.netflix.com"
        }
        logging.info("🧠 [Brain] Voice-to-Action Router is ONLINE.")

    async def parse_intent(self, transcript: str):
        """Basic Natural Language Processing to extract Intent and Target"""
        transcript_lower = transcript.lower()
        
        # 1. Level 1 Automation: Check for basic "Open Website" intent
        if ("open" in transcript_lower or "go to" in transcript_lower) and len(transcript_lower.split()) <= 4:
            for site_name, url in self.known_websites.items():
                if site_name in transcript_lower:
                    logging.info(f"🧠 [Brain] NLP Parsed Intent: OPEN_WEBSITE | Target: {url}")
                    self.execute_open_website(url)
                    return
            
            # If site not in dict but user says "open X"
            words = transcript_lower.split()
            try:
                idx = words.index("open")
                target = words[idx+1]
                url = f"https://www.{target}.com"
                logging.info(f"🧠 [Brain] NLP Parsed Unknown Intent: OPEN_WEBSITE | Guessed Target: {url}")
                self.execute_open_website(url)
                return
            except Exception as e:
                from core.reliability.system_logger import system_logger
                system_logger.log('ERROR', 'voice_to_action_router', f'Unhandled exception: {e}')
                pass
                
        # 2. Level 3 Automation: Deep VLM Browser Control
        logging.info(f"🧠 [Brain] Complex command detected: '{transcript}'")
        logging.info("🧠 [Brain] Delegating to VLM Computer Use Agent for Deep Browser Control...")
        
        try:
            result = await computer_use_agent.execute_task(transcript)
            if result.get("status") == "SUCCESS":
                logging.info("✅ [Brain] Computer Use Agent successfully completed the task.")
            else:
                logging.error(f"❌ [Brain] Computer Use Agent failed: {result.get('reason', 'Unknown error')}")
        except Exception as e:
            logging.error(f"❌ [Brain] Computer Use Agent crash: {e}")


    def execute_open_website(self, url: str):
        """Physically triggers the OS to open the browser."""
        logging.info(f"🤖 [Action Executor] Physically opening browser to {url}...")
        webbrowser.open(url)
        logging.info("🤖 [Action Executor] Browser launch successful.")

    async def run_async(self):
        logging.info("🧠 [Brain] Waiting for VOICE_COMMANDs from the Audio Swarm...")
        while True:
            # Poll the message board for UNREAD AUDIO_TRIGGER messages
            unread_msgs = self.board.poll_messages("AUDIO_TRIGGER")
            
            for msg in unread_msgs:
                if msg.get("payload", {}).get("event") == "VOICE_WAKE_WORD":
                    transcript = msg.get("payload", {}).get("transcript", "")
                    logging.info(f"📥 [Brain] Received Audio Payload: '{transcript}'")
                    await self.parse_intent(transcript)
                        
            await asyncio.sleep(1)

if __name__ == "__main__":
    router = VoiceToActionRouter()
    try:
        asyncio.run(router.run_async())
    except KeyboardInterrupt:
        logging.info("🧠 [Brain] Shutting down Voice-to-Action Router.")
