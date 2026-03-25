import sys
import os

# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.ocr_service import ocr_service
from app.services.pdf_service import pdf_service

def test_complex():
    input_path = 'example/input/complex_doc.pdf'
    output_path = 'example/output/complex_scanned.pdf'
    
    print(f"Reading {input_path}...")
    with open(input_path, 'rb') as f:
        file_bytes = f.read()
    
    print("Running multi-page OCR extraction...")
    ocr_results = ocr_service.extract_text(file_bytes)
    print(f"Total text blocks found: {len(ocr_results)}")
    
    print("Generating combined PDF output...")
    output_pdf = pdf_service.create_pdf_from_ocr(file_bytes, ocr_results)
    
    with open(output_path, 'wb') as f:
        f.write(output_pdf)
    
    print(f"Test Successful! Output saved to {output_path}")

if __name__ == "__main__":
    test_complex()
