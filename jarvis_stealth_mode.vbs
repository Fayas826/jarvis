Set objShell = WScript.CreateObject("WScript.Shell")
' Run the python script using pythonw (windowless)
objShell.Run "pythonw ""c:\jarvis AI\jarvis\core\perception\audio_surveillance_swarm.py""", 0, False
WScript.Quit
