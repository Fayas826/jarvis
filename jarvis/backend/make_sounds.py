import wave
import struct
import math
import os

sounds_dir = r"c:\jarvis AI\jarvis\frontend\public\sounds"
os.makedirs(sounds_dir, exist_ok=True)

def create_wav(filename, duration, sample_rate=44100, func=None):
    n_samples = int(duration * sample_rate)
    with wave.open(os.path.join(sounds_dir, filename), 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for i in range(n_samples):
            t = float(i) / sample_rate
            val = func(t, duration)
            # clamp and write
            val = max(-1.0, min(1.0, val))
            data = struct.pack('<h', int(val * 32767))
            wav_file.writeframesraw(data)

# 1. Activate sound (Reactor) - Rising hum/buzz
def activate_sound(t, d):
    # frequency sweeps from 50 to 500
    freq = 50 + 450 * (t / d)
    val = math.sin(2 * math.pi * freq * t)
    # add harsh harmonic
    val += 0.5 * math.sin(2 * math.pi * (freq * 2) * t)
    # fade out at the end
    envelope = 1.0 - (t / d)**2
    return val * envelope * 0.5

# 2. Scan sound (HUD) - Rapid sonar bleeps
def scan_sound(t, d):
    # High pitched ping
    freq = 1200
    val = math.sin(2 * math.pi * freq * t)
    # LFO to make it pulse fast
    lfo = math.sin(2 * math.pi * 15 * t) > 0
    envelope = math.exp(-3 * (t / d))
    return val * envelope * (0.8 if lfo else 0)

# 3. Click sound (Grid) - Short crisp chirp
def click_sound(t, d):
    freq = 800 - 600 * (t / d) # dropping frequency
    val = math.sin(2 * math.pi * freq * t)
    envelope = math.exp(-20 * (t / d))
    return val * envelope

print("Generating sounds...")
create_wav("activate.wav", 1.2, func=activate_sound)
create_wav("scan.wav", 0.5, func=scan_sound)
create_wav("click.wav", 0.15, func=click_sound)
print("Done!")
