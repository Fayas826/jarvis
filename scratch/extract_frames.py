import os
import subprocess
import cv2

video_path = r'c:\jarvis AI\jarvis\scratch\pattern_record.mp4'
out_dir = r'c:\jarvis AI\jarvis\scratch\pattern_frames'
os.makedirs(out_dir, exist_ok=True)

try:
    import imageio.v3 as iio
    frames = iio.imread(video_path, plugin="pyav")
    print(f"Total video frames: {len(frames)}")
    saved = 0
    for idx in range(0, len(frames), 5):
        fn = os.path.join(out_dir, f"frame_{saved:03d}.png")
        cv2.imwrite(fn, cv2.cvtColor(frames[idx], cv2.COLOR_RGB2BGR))
        saved += 1
    print(f"Successfully saved {saved} frames to {out_dir}")
except Exception as e:
    print(f"Error reading frames: {e}")
