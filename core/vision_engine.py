import cv2
import mediapipe as mp
import time

class JarvisVisionEngine:
    def __init__(self):
        print("[VISION ENGINE] Booting Optical Sensors...")
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.cap = cv2.VideoCapture(0) # 0 is the default laptop webcam
        
    def start_tracking(self):
        print("[VISION ENGINE] Optical Sensors Online. Tracking Hands...")
        previous_x = 0
        
        while self.cap.isOpened():
            success, img = self.cap.read()
            if not success:
                print("[ERROR] Camera failed to initialize.")
                break

            # Flip the image horizontally for a later selfie-view display
            img = cv2.flip(img, 1)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Process the image and find hands
            results = self.hands.process(img_rgb)
            
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw the skeleton on the hand
                    self.mp_draw.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    
                    # Basic Swipe Detection (Tracking the Index Finger Tip)
                    index_finger_x = hand_landmarks.landmark[8].x
                    
                    # If finger moves significantly to the right/left in a short time
                    movement = index_finger_x - previous_x
                    if movement > 0.2:
                        print("[JARVIS UI ACTION] ⬅️ SWIPE RIGHT DETECTED (Opening Chat Box)")
                    elif movement < -0.2:
                        print("[JARVIS UI ACTION] ➡️ SWIPE LEFT DETECTED (Closing Chat Box)")
                        
                    previous_x = index_finger_x

            # Show the JARVIS Vision feed window
            cv2.putText(img, "JARVIS OPTICAL SENSOR [ACTIVE]", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 204), 2)
            cv2.imshow("JARVIS Vision Engine", img)
            
            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        self.shutdown()

    def shutdown(self):
        print("[VISION ENGINE] Shutting down Optical Sensors.")
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    vision = JarvisVisionEngine()
    vision.start_tracking()
