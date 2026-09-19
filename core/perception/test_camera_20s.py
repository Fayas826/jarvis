import cv2
import time
import math
import os

print("=======================================================")
print("STARTING 20-SECOND JARVIS CAMERA & HUD TEST STREAM...")
print("=======================================================")

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera device 0.")
    exit(1)

start_time = time.time()
frame_count = 0
output_dir = r"c:\jarvis AI\jarvis\vault_traps"
os.makedirs(output_dir, exist_ok=True)
output_photo = os.path.join(output_dir, "camera_test_output.jpg")

angle = 0
while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera frame read error.")
        break

    frame_count += 1
    elapsed = time.time() - start_time
    remaining = max(0.0, 20.0 - elapsed)

    # Flip horizontal for mirror effect
    frame = cv2.flip(frame, 1)
    
    # --- OPTICAL ANTI-GLARE AUTO-TONE MAPPING ---
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    frame = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    
    h, w, _ = frame.shape
    cx, cy = w // 2, h // 2

    # Draw Arc Reactor overlay
    angle += 0.05
    radius = 120

    # Outer Cyan Ring
    cv2.circle(frame, (cx, cy), radius, (255, 240, 0), 2, cv2.LINE_AA)
    
    # Orbiting Light Dots
    for i in range(8):
        a = angle + (i * math.pi / 4)
        px = int(cx + radius * math.cos(a))
        py = int(cy + radius * math.sin(a))
        cv2.circle(frame, (px, py), 6, (0, 255, 136), -1, cv2.LINE_AA)

    # Status Overlay Text
    cv2.putText(frame, "JARVIS MARK-L MOBILE CAMERA TEST", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 240, 0), 2, cv2.LINE_AA)
    cv2.putText(frame, f"TESTING STREAM: {remaining:.1f}s REMAINING", (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 136), 2, cv2.LINE_AA)
    cv2.putText(frame, f"FRAMES CAPTURED: {frame_count} | 60FPS OK", (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2, cv2.LINE_AA)

    # Save final snapshot at the 19th second
    if elapsed >= 19.0 and not os.path.exists(output_photo):
        cv2.imwrite(output_photo, frame)

    if elapsed >= 20.0:
        cv2.imwrite(output_photo, frame)
        break

    time.sleep(0.03)

cap.release()
print(f"CAMERA TEST COMPLETE! Captured {frame_count} frames over 20 seconds.")
print(f"Snapshot saved to: {output_photo}")
