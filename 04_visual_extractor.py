import os
import time
import fitz  # PyMuPDF
from google import genai
from dotenv import load_dotenv
from PIL import Image

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Paths
PDF_PATH = r"C:\AI\data\raw\gao_report.pdf"
IMAGE_DIR = r"C:\AI\data\processed\images"
OUTPUT_DIR = r"C:\AI\outputs"

os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_page_vision(page_num):
    output_path = os.path.join(OUTPUT_DIR, f"Page_{page_num}_CLEAN.md")
    if os.path.exists(output_path):
        return

    # Capture at a "Quota-Friendly" resolution (1.5x instead of 2.0x)
    img_path = os.path.join(IMAGE_DIR, f"page_{page_num}_snap.png")
    doc = fitz.open(PDF_PATH)
    page = doc.load_page(page_num - 1)
    pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5)) 
    pix.save(img_path)
    doc.close()

    success = False
    # We will try the most stable model first
    current_model = 'gemini-2.5-flash' 

    while not success:
        try:
            print(f"--- Digitizing Page {page_num} using {current_model} ---")
            img = Image.open(img_path)
            
            response = client.models.generate_content(
                model=current_model, 
                contents=["Extract this cost table into Markdown. Exact numbers only.", img]
            )

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            
            print(f"✅ Success on Page {page_num}")
            success = True
            time.sleep(10) # 10s gap to prevent 'burst' detection

        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg:
                print("⚠️ Daily or Minute Limit Hit. Trying one backup model...")
                # Switch models to try and tap into a different quota bucket
                current_model = 'gemini-1.5-flash-8b' if current_model == 'gemini-1.5-flash' else 'gemini-2.0-flash'
                time.sleep(30) 
            else:
                print(f"❌ Error: {e}")
                break

if __name__ == "__main__":
    # Try Pages 42-45
    for p in range(42, 46):
        extract_page_vision(p)