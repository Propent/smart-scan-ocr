import pytesseract
import numpy as np
from PIL import Image
import io
import fitz  # PyMuPDF
import cv2

class OCRService:
    def __init__(self, languages=['en']):
        # Tesseract language string (e.g., 'eng' for English)
        self.lang = "+".join(['eng' if l == 'en' else l for l in languages])

    def _preprocess_image(self, image_np: np.ndarray) -> np.ndarray:
        """
        Preprocessing for Tesseract.
        """
        gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        # Tesseract often works better with simple thresholding or just grayscale
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

    def extract_text(self, file_bytes: bytes, on_progress=None) -> list[dict]:
        if not file_bytes:
            raise ValueError("Empty file provided")
            
        if file_bytes.startswith(b'%PDF'):
            return self._extract_from_pdf(file_bytes, on_progress)
        else:
            return self._extract_from_image(file_bytes, on_progress)

    def _extract_from_image(self, image_bytes: bytes, on_progress=None) -> list[dict]:
        if on_progress: on_progress(10)
        
        nparr = np.frombuffer(image_bytes, np.uint8)
        image_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        processed_np = self._preprocess_image(image_np)
        
        if on_progress: on_progress(40)
        
        # Get data including bounding boxes
        data = pytesseract.image_to_data(processed_np, lang=self.lang, output_type=pytesseract.Output.DICT)
        
        results = self._format_tesseract_data(data)
        
        if on_progress: on_progress(100)
        return results

    def _extract_from_pdf(self, pdf_bytes: bytes, on_progress=None) -> list[dict]:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        num_pages = len(doc)
        all_results = []
        
        for i, page in enumerate(doc):
            pix = page.get_pixmap(dpi=300)
            img_data = pix.tobytes("png")
            
            nparr = np.frombuffer(img_data, np.uint8)
            image_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            processed_np = self._preprocess_image(image_np)
            
            data = pytesseract.image_to_data(processed_np, lang=self.lang, output_type=pytesseract.Output.DICT)
            page_results = self._format_tesseract_data(data)
            
            for res in page_results:
                res['page'] = i + 1
            all_results.extend(page_results)
            
            if on_progress:
                progress = int((i + 1) / num_pages * 100)
                on_progress(progress)
        
        doc.close()
        return all_results

    def _format_tesseract_data(self, data) -> list[dict]:
        output = []
        n_boxes = len(data['text'])
        for i in range(n_boxes):
            text = data['text'][i].strip()
            if text:
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                output.append({
                    "text": text,
                    "confidence": float(data['conf'][i]) / 100.0,
                    "bbox": [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]
                })
        return output

ocr_service = OCRService()
