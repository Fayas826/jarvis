import os
from fpdf import FPDF

class CreativeEngine:
    def __init__(self):
        self.sd_pipeline = None
        self.svd_pipeline = None
        self.output_dir = "data/creative_output"
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_pdf(self, title, content, filename="output.pdf"):
        """Generates a PDF file with the given text content."""
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            # Title
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt=title, ln=True, align='C')
            pdf.ln(10)
            
            # Content
            pdf.set_font("Arial", size=12)
            # Encode/decode to ignore unprintable unicode chars in basic fpdf
            safe_content = content.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 10, txt=safe_content)
            
            filepath = os.path.join(self.output_dir, filename)
            if not filepath.endswith(".pdf"):
                filepath += ".pdf"
                
            pdf.output(filepath)
            return f"Successfully generated PDF at {filepath}"
        except Exception as e:
            return f"Failed to generate PDF: {str(e)}"

    def generate_image(self, prompt, filename="image.png"):
        """Generates an image using Stable Diffusion XL Turbo."""
        try:
            import torch
            from diffusers import AutoPipelineForText2Image
            
            if self.sd_pipeline is None:
                print("[CREATIVE_ENGINE] Booting Stable Diffusion XL Turbo (Initial load may take a minute)...")
                # Using SDXL Turbo for fast consumer GPU generation
                self.sd_pipeline = AutoPipelineForText2Image.from_pretrained(
                    "stabilityai/sdxl-turbo", torch_dtype=torch.float16, variant="fp16"
                )
                self.sd_pipeline.to("cuda")
                
            print(f"[CREATIVE_ENGINE] Generating image for prompt: '{prompt}'")
            # SDXL Turbo can do 1-4 step inference
            image = self.sd_pipeline(prompt=prompt, num_inference_steps=2, guidance_scale=0.0).images[0]
            
            filepath = os.path.join(self.output_dir, filename)
            if not filepath.endswith(".png"):
                filepath += ".png"
            image.save(filepath)
            
            return f"Successfully generated Image at {filepath}"
        except ImportError:
            return "Failed to generate image: Required libraries (diffusers, torch) are missing or not installed properly."
        except Exception as e:
            return f"Failed to generate Image: {str(e)}"

    def generate_video(self, prompt, image_filepath=None, filename="video.mp4"):
        """Generates a video using a text-to-video or image-to-video model."""
        try:
            import torch
            from diffusers import StableVideoDiffusionPipeline
            from diffusers.utils import load_image, export_to_video
            
            if self.svd_pipeline is None:
                print("[CREATIVE_ENGINE] Booting Stable Video Diffusion (WARNING: Extremely heavy on GPU VRAM)...")
                self.svd_pipeline = StableVideoDiffusionPipeline.from_pretrained(
                    "stabilityai/stable-video-diffusion-img2vid-xt", torch_dtype=torch.float16, variant="fp16"
                )
                # Offload to CPU to save VRAM if needed, or use cuda
                self.svd_pipeline.enable_model_cpu_offload()

            print(f"[CREATIVE_ENGINE] Generating video...")
            
            # SVD requires an initial image to animate. If none provided, we create a black one or use a default.
            if not image_filepath or not os.path.exists(image_filepath):
                return "Failed to generate video: Stable Video Diffusion requires an initial input image filepath to animate."
                
            image = load_image(image_filepath)
            image = image.resize((1024, 576))

            frames = self.svd_pipeline(image, decode_chunk_size=8, generator=torch.manual_seed(42)).frames[0]
            
            filepath = os.path.join(self.output_dir, filename)
            if not filepath.endswith(".mp4"):
                filepath += ".mp4"
                
            export_to_video(frames, filepath, fps=7)
            
            return f"Successfully generated Video at {filepath}"
        except ImportError:
            return "Failed to generate video: Required libraries (diffusers, torch) are missing."
        except Exception as e:
            return f"Failed to generate Video. Note that video generation requires >16GB VRAM. Error: {str(e)}"

creative_engine = CreativeEngine()
