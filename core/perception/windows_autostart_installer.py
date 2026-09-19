import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [AUTOSTART_INSTALLER] %(message)s")

class WindowsAutostartInstaller:
    """Configures JARVIS Universal Daemon to launch invisibly on Windows boot."""

    @staticmethod
    def install_startup_vbs() -> bool:
        try:
            startup_dir = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
            vbs_path = os.path.join(startup_dir, "jarvis_universal_daemon.vbs")
            pythonw_path = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
            if not os.path.exists(pythonw_path):
                pythonw_path = sys.executable

            script_path = r"c:\jarvis AI\jarvis\core\perception\jarvis_universal_daemon.py"

            # VBS script runs pythonw.exe completely hidden (0 window style)
            vbs_content = f'Set WshShell = CreateObject("WScript.Shell")\n' \
                          f'WshShell.Run "\"{pythonw_path}\" \"{script_path}\"", 0, False\n'

            with open(vbs_path, "w", encoding="utf-8") as f:
                f.write(vbs_content)

            logging.info(f"JARVIS Invisible Autostart installed to Windows Startup folder:")
            logging.info(f"VBS Path: {vbs_path}")
            return True
        except Exception as e:
            logging.error(f"Autostart installation error: {e}")
            return False

if __name__ == "__main__":
    res = WindowsAutostartInstaller.install_startup_vbs()
    print(f"\nJARVIS Autostart Status: {'SUCCESS' if res else 'FAILED'}")
