from voice import speak, listen
from agent import run_agent

def run_jarvis():
    speak("Jarvis upgraded. I can now think and act.")

    while True:
        command = listen().lower()

        if command == "":
            continue

        if "exit" in command or "stop" in command:
            speak("Shutting down.")
            break

        result = run_agent(command)
        speak(str(result))

if __name__ == "__main__":
    run_jarvis()
