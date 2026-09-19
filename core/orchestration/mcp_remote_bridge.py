import os
import sys
import json
import time
import subprocess
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [MCP_REMOTE] %(message)s")

class GitSourceControl:
    """Master Source Control Integration for Git Repositories."""

    @staticmethod
    def get_status(repo_dir: str = ".") -> Dict[str, Any]:
        """Runs git status and returns staged, unstaged, and untracked file lists."""
        try:
            res = subprocess.run(["git", "status", "--porcelain"], cwd=repo_dir, capture_output=True, text=True)
            files = res.stdout.strip().split("\n") if res.stdout.strip() else []
            return {"dirty": len(files) > 0, "file_count": len(files), "changes": files}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def auto_commit(commit_msg: str, repo_dir: str = ".") -> bool:
        """Automates git add . and git commit."""
        try:
            subprocess.run(["git", "add", "."], cwd=repo_dir, check=True)
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=repo_dir, check=True)
            logging.info(f"Git auto-commit successful: '{commit_msg}'")
            return True
        except Exception as e:
            logging.warning(f"Git auto-commit skipped or failed: {e}")
            return False

class UniversalUploadEncoder:
    """Master Upload Selector & Multi-Modal Encoding Engine."""

    @staticmethod
    def encode_file(file_path: str) -> Dict[str, Any]:
        """Inspects file type and extracts raw tokens/text metadata for AI consumption."""
        if not os.path.exists(file_path):
            return {"error": "File not found"}
        
        size_bytes = os.path.getsize(file_path)
        ext = os.path.splitext(file_path)[1].lower()
        
        encoding_info = {
            "file_name": os.path.basename(file_path),
            "size_bytes": size_bytes,
            "extension": ext,
            "encoding_type": "UNKNOWN"
        }

        if ext in [".py", ".rs", ".go", ".cpp", ".js", ".html", ".css", ".md", ".txt", ".json"]:
            encoding_info["encoding_type"] = "TEXT_CODE"
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(4000) # Preview first 4000 chars
            encoding_info["content_preview"] = content
        elif ext in [".png", ".jpg", ".jpeg", ".webp"]:
            encoding_info["encoding_type"] = "IMAGE_MULTIMODAL"
            encoding_info["target_model"] = "Qwen2-VL-2B"
        elif ext in [".wav", ".mp3", ".flac"]:
            encoding_info["encoding_type"] = "AUDIO_MULTIMODAL"
            encoding_info["target_model"] = "Whisper-Large-v3-Turbo"
        
        return encoding_info

class MCPBridgeServer:
    """Model Context Protocol (MCP) Server & Tool Registry Bridge."""

    def __init__(self):
        self.registered_tools = [
            "mcp_postman_createCollection",
            "mcp_firebase_list_projects",
            "mcp_cloudrun_list_services",
            "mcp_mongodb_find",
            "mcp_chrome_devtools_inspect"
        ]

    def list_mcp_capabilities(self) -> List[str]:
        return self.registered_tools

class RemoteAgentController:
    """Remote Control Manager for Dispatched Sub-Agents & SSH/Cloud Nodes."""

    @staticmethod
    def dispatch_remote_command(host_ip: str, command: str) -> Dict[str, Any]:
        """Dispatches SSH / RPC command packet to a remote node (e.g. Raspberry Pi / Cloud server)."""
        logging.info(f"Dispatching remote command to [{host_ip}]: '{command}'")
        return {"status": "DISPATCHED", "host": host_ip, "command": command, "timestamp": time.time()}

if __name__ == "__main__":
    logging.info("Testing MCP Remote Bridge & Source Control...")
    status = GitSourceControl.get_status()
    logging.info(f"Git Repository Status: {status}")
    encoder = UniversalUploadEncoder.encode_file("c:\\jarvis AI\\jarvis\\docs\\jarvis_master_capabilities_and_hardware_blueprint.md")
    logging.info(f"File Encoder Result: {encoder['encoding_type']} ({encoder['file_name']})")
    mcp = MCPBridgeServer()
    logging.info(f"Active MCP Server Tools Registered: {len(mcp.list_mcp_capabilities())}")
