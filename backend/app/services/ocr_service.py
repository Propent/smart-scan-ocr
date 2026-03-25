import easyocr
import numpy as np
from PIL import Image
import io
import fitz  # PyMuPDF
import os

class OCRService:
    def __init__(self, languages=['en']):
        # Initialize reader
        self.reader = easyocr.Reader(languages, gpu=False)

    def extract_text(self, file_bytes: bytes, on_progress=None) -> list[dict]:
        """
        Extracts text from image or PDF bytes.
        """
        if not file_bytes:
            raise ValueError("Empty file provided")
            
        print(f"DEBUG: Processing file of size {len(file_bytes)} bytes")
        print(f"DEBUG: First 10 bytes: {file_bytes[:10]!r}")

        # Try to detect if it's a PDF by looking at the header
        if file_bytes.startswith(b'%PDF'):
            return self._extract_from_pdf(file_bytes, on_progress)
        else:
            try:
                return self._extract_from_image(file_bytes, on_progress)
            except Exception as e:
                print(f"DEBUG: Image identification failed: {str(e)}")
                raise ValueError(f"Unsupported or invalid file format: {str(e)}")

    def _extract_from_image(self, image_bytes: bytes, on_progress=None) -> list[dict]:
        if on_progress:
            on_progress(10)
        image = Image.open(io.BytesIO(image_bytes))
        image_np = np.array(image.convert('RGB'))
        if on_progress:
            on_progress(30)
        results = self.reader.readtext(image_np)
        if on_progress:
            on_progress(90)
        return self._format_results(results)

    def _extract_from_pdf(self, pdf_bytes: bytes, on_progress=None) -> list[dict]:
        # Convert PDF pages to images using PyMuPDF (fitz)
        if on_progress:
            on_progress(5)
            
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        num_pages = len(doc)
        all_results = []
        
        for i, page in enumerate(doc):
            pix = page.get_pixmap()
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data))
            
            image_np = np.array(image.convert('RGB'))
            results = self.reader.readtext(image_np)
            page_results = self._format_results(results)
            # Add page info to results
            for res in page_results:
                res['page'] = i + 1
            all_results.extend(page_results)
            
            if on_progress:
                # Distribute 90% of progress over pages (leaving 10% for PDF generation)
                progress = 5 + int((i + 1) / num_pages * 85)
                on_progress(progress)
        
        doc.close()
        return all_results

    def _format_results(self, results) -> list[dict]:
        output = []
        for (bbox, text, prob) in results:
            output.append({
                "text": text,
                "confidence": float(prob),
                "bbox": [list(map(int, point)) for point in bbox]
            })
        return output

ocr_service = OCRService()
