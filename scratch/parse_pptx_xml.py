import os
import zipfile
import xml.etree.ElementTree as ET

def extract_pptx_text(pptx_path):
    print(f"==================================================")
    print(f"FILE: {os.path.basename(pptx_path)}")
    print(f"==================================================")
    if not os.path.exists(pptx_path):
        print(f"File not found: {pptx_path}")
        return

    try:
        with zipfile.ZipFile(pptx_path, 'r') as z:
            slide_files = [f for f in z.namelist() if f.startswith('ppt/slides/slide') and f.endswith('.xml')]
            # sort slides numerically
            slide_files.sort(key=lambda x: int(''.join(filter(str.isdigit, os.path.basename(x))) or '0'))
            
            for sfile in slide_files:
                slide_num = ''.join(filter(str.isdigit, os.path.basename(sfile)))
                content = z.read(sfile)
                tree = ET.fromstring(content)
                
                # Extract text elements
                texts = []
                for elem in tree.iter():
                    if elem.tag.endswith('}t') and elem.text:
                        texts.append(elem.text.strip())
                
                if texts:
                    print(f"\n--- Slide {slide_num} ---")
                    print("\n".join(texts))
    except Exception as e:
        print(f"Error reading {pptx_path}: {e}")

if __name__ == "__main__":
    files = [
        r"c:\jarvis AI\jarvis\CogAgent Seminar Presentation.pptx",
        r"c:\jarvis AI\jarvis\CognitiveOS_Zeroth_FINAL_Official_Headings (1).pptx",
        r"c:\jarvis AI\jarvis\amrita_template (1).pptx"
    ]
    for f in files:
        extract_pptx_text(f)
