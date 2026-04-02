import os

def execute_command(command):
    if "open youtube" in command:
        os.system("start https://youtube.com")
        return "Opening YouTube"

    elif "open google" in command:
        os.system("start https://google.com")
        return "Opening Google"

    elif "open notepad" in command:
        os.system("notepad")
        return "Opening Notepad"

    return None
