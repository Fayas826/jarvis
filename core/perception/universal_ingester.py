import os
import io

class UniversalIngester:
    def __init__(self):
        self.whisper_model = None

    def ingest_file(self, filepath):
        """
        Takes an absolute filepath and attempts to parse it into plain text or vision summaries.
        Returns the extracted text.
        """
        if not os.path.exists(filepath):
            return f"Error: File not found at {filepath}"

        ext = filepath.lower().split('.')[-1]
        print(f"[INGESTER] Ingesting {ext.upper()} file: {filepath}")

        try:
            if ext in ['txt', 'md', 'py', 'json', 'csv', 'js', 'html', 'css']:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            elif ext == 'pdf':
                return self._parse_pdf(filepath)
            elif ext in ['doc', 'docx']:
                return self._parse_docx(filepath)
            elif ext in ['mp3', 'wav', 'm4a', 'flac']:
                return self._parse_audio(filepath)
            elif ext in ['mp4', 'avi', 'mkv', 'mov']:
                return self._parse_video(filepath)
            else:
                return f"Error: Unsupported file extension .{ext}. JARVIS does not know how to parse this format yet."
        except Exception as e:
            return f"Error during ingestion: {str(e)}"

    def _parse_pdf(self, filepath):
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
            return text
        except ImportError:
            return "Error: pdfplumber is not installed."

    def _parse_docx(self, filepath):
        try:
            import docx
            doc = docx.Document(filepath)
            return "\n".join([para.text for para in doc.paragraphs])
        except ImportError:
            return "Error: python-docx is not installed."

    def _parse_audio(self, filepath):
        try:
            import whisper
            if self.whisper_model is None:
                print("[INGESTER] Booting Whisper Audio Model (this may take a moment)...")
                self.whisper_model = whisper.load_model("base")
            print("[INGESTER] Transcribing audio...")
            result = self.whisper_model.transcribe(filepath)
            return f"[AUDIO TRANSCRIPT]:\n{result['text']}"
        except ImportError:
            return "Error: openai-whisper is not installed."

    def _parse_video(self, filepath):
        try:
            import cv2
            import requests
            import base64
            
            print("[INGESTER] Analyzing Video Frames...")
            cap = cv2.VideoCapture(filepath)
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration_sec = total_frames / max(1, fps)
            
            # We will sample 3 frames: 25%, 50%, and 75% through the video
            sample_frames = [int(total_frames * 0.25), int(total_frames * 0.50), int(total_frames * 0.75)]
            frame_descriptions = []
            
            for f_idx in sample_frames:
                cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
                ret, frame = cap.read()
                if ret:
                    # Convert frame to base64 for LLaVA
                    _, buffer = cv2.imencode('.jpg', frame)
                    b64_img = base64.b64encode(buffer).decode('utf-8')
                    
                    # Ask LLaVA to describe the frame
                    resp = requests.post('http://localhost:11434/api/generate', json={
                        "model": "llava:latest",
                        "prompt": "Describe what is happening in this single video frame concisely.",
                        "images": [b64_img],
                        "stream": False
                    }, timeout=60)
                    if resp.status_code == 200:
                        frame_descriptions.append(resp.json().get('response', ''))
                        
            cap.release()
            
            final_report = f"[VIDEO REPORT] Duration: {duration_sec:.2f} seconds\n"
            final_report += "JARVIS Visual Frame Analysis:\n"
            for i, desc in enumerate(frame_descriptions):
                final_report += f"Frame {i+1}: {desc}\n"
            return final_report
            
        except Exception as e:
            return f"Error processing video: {str(e)}"

# Singleton
universal_ingester = UniversalIngester()
