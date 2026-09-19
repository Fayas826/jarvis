Set WshShell = CreateObject("WScript.Shell")
' 1. Silently start Python Backend Server & Win32 Kernel Engine
WshShell.Run "cmd /c python ""c:\jarvis AI\jarvis\core\perception\launch_stark_dashboard.py""", 0, False

' 2. Silently start Cloudflare HTTPS Tunnel
WshShell.Run "cmd /c npx --yes cloudflared tunnel --url http://localhost:8092", 0, False

' 3. Silently start Docker Desktop (if installed)
WshShell.Run "cmd /c ""C:\Program Files\Docker\Docker\Docker Desktop.exe""", 0, False
