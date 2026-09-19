import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from action.creative_engine import creative_engine

print("--- Testing PDF Generation ---")
pdf_result = creative_engine.generate_pdf(
    title="The Brilliant Sun", 
    content="The Sun is the star at the center of the Solar System. It is a massive, hot ball of plasma, inflated and heated by energy produced by nuclear fusion reactions at its core.", 
    filename="sun_report.pdf"
)
print(pdf_result)

print("\n--- Testing Image Generation (Will download SDXL if first time) ---")
img_result = creative_engine.generate_image(
    prompt="A beautiful, hyper-realistic image of the sun shining brightly in outer space, 8k resolution, cinematic lighting",
    filename="sun_image.png"
)
print(img_result)

print("\n--- Testing Video Generation (Will download SVD if first time) ---")
vid_result = creative_engine.generate_video(
    prompt="The sun rotating and shining",
    image_filepath="data/creative_output/sun_image.png",
    filename="sun_video.mp4"
)
print(vid_result)

print("\nALL TESTS COMPLETE.")
