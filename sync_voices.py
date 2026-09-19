import os

# Tell Python exactly where the Windows eSpeak library is located
os.environ["PHONEMIZER_ESPEAK_LIBRARY"] = r"C:\Program Files\eSpeak NG\libespeak-ng.dll"
os.environ["PHONEMIZER_ESPEAK_PATH"] = r"C:\Program Files\eSpeak NG"
os.environ["PATH"] = r"C:\Program Files\eSpeak NG;" + os.environ.get("PATH", "")

from TTS.api import TTS

print("Generating 3-second cloning sample for XTTS...")

tts = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False).to("cpu")

# Generate the sample audio from the VITS engine
target_path = os.path.join(os.path.dirname(__file__), "perception", "voice", "my_voice.wav")
text = "Hello sir. I am currently synchronizing my vocal profiles to ensure maximum clarity across both offline engines."

tts.tts_to_file(
    text=text, 
    speaker="p273", # Using the default deep male voice
    file_path=target_path
)

print(f"\nSuccessfully generated {target_path}!")
print("XTTS Clone mode will now sound exactly like the fast VITS mode.")
