import json
import os
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class SwarmMessageBoard:
    """
    The Artifactory-style Proxy Cache for the Jarvis Agent Swarms.
    Isolated agents use this cache to establish Capability Chains and communicate globally.
    """
    def __init__(self, board_file="c:\\jarvis AI\\jarvis\\scratch\\swarm_cache.json"):
        self.board_file = board_file
        if not os.path.exists(self.board_file):
            with open(self.board_file, 'w') as f:
                json.dump([], f)
                
    def _read_with_retry(self):
        for _ in range(5):
            try:
                with open(self.board_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError, OSError):
                time.sleep(0.05)
        return []

    def _write_with_retry(self, data):
        for _ in range(5):
            try:
                with open(self.board_file, 'w') as f:
                    json.dump(data, f, indent=4)
                return True
            except OSError:
                time.sleep(0.05)
        return False

    def post_message(self, sender: str, topic: str, payload: dict):
        """Agents post messages (like vulnerabilities or errors) to the shared cache."""
        messages = self._read_with_retry()
            
        message = {
            "timestamp": time.time(),
            "sender": sender,
            "topic": topic,
            "payload": payload,
            "status": "UNREAD"
        }
        messages.append(message)
        
        self._write_with_retry(messages)
            
        logging.info(f"📡 [Message Board] New message from {sender} on topic '{topic}'")
        return True
        
    def poll_messages(self, topic: str):
        """Agents poll for unread messages on a specific topic."""
        messages = self._read_with_retry()
            
        unread = [m for m in messages if m["topic"] == topic and m["status"] == "UNREAD"]
        
        if unread:
            # Mark as read
            for m in messages:
                if m in unread:
                    m["status"] = "READ"
                    
            self._write_with_retry(messages)
                
        return unread

if __name__ == "__main__":
    # Test the message board locally
    board = SwarmMessageBoard()
    board.post_message("TestAgent", "test_topic", {"error": "syntax error"})
    print(board.poll_messages("test_topic"))
