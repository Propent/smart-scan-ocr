from PIL import Image
import fitz
import io
import os

def identify():
    path = 'uploads/failing_file.bin'
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return
        
    data = open(path, 'rb').read()
    print(f"File Size: {len(data)}")
    print(f"Header (hex): {data[:20].hex(' ')}")
    print(f"Header (ASCII): {data[:20]!r}")

    # Try PIL
    try:
        img = Image.open(io.BytesIO(data))
        print(f"SUCCESS (PIL): Format={img.format}, Size={img.size}, Mode={img.mode}")
    except Exception as e:
        print(f"FAILED (PIL): {e}")

    # Try PyMuPDF
    try:
        doc = fitz.open(stream=data)
        print(f"SUCCESS (Fitz): Pages={len(doc)}, Metadata={doc.metadata}")
    except Exception as e:
        print(f"FAILED (Fitz): {e}")

    # Try as Text (First 100 chars)
    try:
        print(f"Text Preview: {data[:100].decode('utf-8', errors='ignore')}")
    except:
        pass

if __name__ == "__main__":
    identify()
