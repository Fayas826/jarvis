Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd.exe /c taskkill /f /im cmd.exe", 0, True
WshShell.Run "cmd.exe /c taskkill /f /im conhost.exe", 0, True
WshShell.Run "cmd.exe /c taskkill /f /im python.exe", 0, True
WshShell.Run "cmd.exe /c taskkill /f /im node.exe", 0, True
WshShell.Run "cmd.exe /c schtasks /delete /tn ""JarvisPersistence"" /f", 0, True
WshShell.Run "cmd.exe /c schtasks /create /sc onlogon /tn ""JarvisPersistence"" /tr ""wscript.exe C:\Users\Asus\jarvis_silent_starter.vbs"" /f", 0, True
WshShell.Run "wscript.exe ""C:\Users\Asus\jarvis_silent_starter.vbs""", 0, False
MsgBox "O.M.E.G.A. Environment Recovery Protocol Complete. Please restart your terminal.", 64, "JARVIS O.M.E.G.A."
