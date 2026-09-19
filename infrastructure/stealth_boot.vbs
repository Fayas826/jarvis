Set WshShell = CreateObject("WScript.Shell")
' Run the Python daemon script invisibly (0 means hidden window)
WshShell.Run "python ""C:\jarvis AI\jarvis\infrastructure\jarvis_daemon.py""", 0
Set WshShell = Nothing
