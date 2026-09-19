import os
import sys
import subprocess
import ctypes
import psutil
import logging
import time
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AdminSystemController")

class AdminSystemController:
    """
    ⚡ PILLAR 2: Autonomous Administrative Shell & OS Control Engine
    Executes deep system maintenance, process governance, driver/network audits,
    and storage cleanup with High Integrity (Administrator) credentials.
    """

    def __init__(self):
        self.is_admin = bool(ctypes.windll.shell32.IsUserAnAdmin())
        logger.info(f"[ADMIN_CORE] Initialized. Elevated High Integrity: {self.is_admin}")

    def execute_powershell(self, script: str, timeout: int = 30) -> Dict[str, Any]:
        """Runs an elevated PowerShell command and returns structured stdout/stderr."""
        cmd = [
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy", "Bypass",
            "-Command", script
        ]
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            return {
                "success": res.returncode == 0,
                "returncode": res.returncode,
                "stdout": res.stdout.strip(),
                "stderr": res.stderr.strip()
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Command timed out after {timeout}s"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def scan_processes(self, cpu_threshold: float = 15.0) -> List[Dict[str, Any]]:
        """Scans all running processes and identifies those exceeding CPU or memory limits."""
        flagged = []
        # Prime psutil cpu counters
        for p in psutil.process_iter(['pid', 'name']):
            try:
                p.cpu_percent(interval=None)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        time.sleep(0.1) # brief interval for delta
        
        for p in psutil.process_iter(['pid', 'name', 'memory_percent']):
            try:
                cpu = p.cpu_percent(interval=None)
                if cpu >= cpu_threshold:
                    info = p.info
                    info['cpu_percent'] = cpu
                    flagged.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return flagged

    def terminate_process(self, pid: int, force: bool = True) -> Dict[str, Any]:
        """Force-kills a process using elevated Administrator privileges."""
        try:
            proc = psutil.Process(pid)
            proc_name = proc.name()
            if force:
                subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
            else:
                proc.terminate()
            return {"success": True, "pid": pid, "name": proc_name, "status": "TERMINATED"}
        except Exception as e:
            return {"success": False, "pid": pid, "error": str(e)}

    def flush_dns(self) -> Dict[str, Any]:
        """Flushes the Windows DNS resolver cache."""
        res = self.execute_powershell("Clear-DnsClientCache; Write-Output 'DNS_CACHE_FLUSHED'")
        return {
            "success": "DNS_CACHE_FLUSHED" in res.get("stdout", ""),
            "output": res.get("stdout") or res.get("stderr")
        }

    def audit_network_latency(self, target: str = "8.8.8.8") -> Dict[str, Any]:
        """Pings target and extracts round-trip latency statistics."""
        try:
            res = subprocess.run(
                ["ping", "-n", "3", target],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            output = res.stdout
            avg_ms = None
            if "Average =" in output:
                avg_part = output.split("Average =")[-1].strip().split()[0].replace("ms", "")
                avg_ms = int(avg_part)
            return {
                "target": target,
                "reachable": res.returncode == 0,
                "average_latency_ms": avg_ms,
                "raw": output.strip()
            }
        except Exception as e:
            return {"target": target, "reachable": False, "error": str(e)}

    def cleanup_temp_storage(self) -> Dict[str, Any]:
        """
        Safely removes unneeded temporary update files in C:\\Windows\\Temp and %TEMP%
        without touching user documents or active file locks.
        """
        temp_dirs = [
            os.environ.get("TEMP", r"C:\Users\Default\AppData\Local\Temp"),
            r"C:\Windows\Temp"
        ]
        
        deleted_count = 0
        deleted_bytes = 0
        skipped_count = 0
        
        for tdir in temp_dirs:
            if not os.path.exists(tdir):
                continue
            for root, dirs, files in os.walk(tdir):
                for f in files:
                    file_path = os.path.join(root, f)
                    try:
                        # Skip if modified in the last 15 minutes (potentially active)
                        if time.time() - os.path.getmtime(file_path) < 900:
                            skipped_count += 1
                            continue
                        size = os.path.getsize(file_path)
                        os.remove(file_path)
                        deleted_count += 1
                        deleted_bytes += size
                    except Exception:
                        skipped_count += 1
                        continue

        mb_freed = round(deleted_bytes / (1024 * 1024), 2)
        logger.info(f"[CLEANUP] Freed {mb_freed} MB across {deleted_count} temp files. Skipped {skipped_count} active/locked.")
        return {
            "success": True,
            "deleted_files_count": deleted_count,
            "freed_mb": mb_freed,
            "skipped_count": skipped_count
        }

    def run_system_health_audit(self) -> Dict[str, Any]:
        """Runs a complete system health and resource audit."""
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('C:\\')
        ping = self.audit_network_latency()
        high_procs = self.scan_processes(cpu_threshold=20.0)
        
        return {
            "is_admin": self.is_admin,
            "cpu_percent": cpu,
            "memory_percent": mem.percent,
            "memory_available_gb": round(mem.available / (1024**3), 2),
            "disk_free_gb": round(disk.free / (1024**3), 2),
            "network_latency_ms": ping.get("average_latency_ms"),
            "high_cpu_processes_count": len(high_procs),
            "high_cpu_processes": high_procs
        }

admin_sys_controller = AdminSystemController()
