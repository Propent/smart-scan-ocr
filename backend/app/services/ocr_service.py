import pytesseract
import numpy as np
from PIL import Image
import io
import fitz  # PyMuPDF
import cv2
import os
import sys
import logging

# Standard logging configuration for FastAPI
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app.services.ocr")

class OCRService:
    def __init__(self, languages=['en']):
        if sys.platform == "win32":
            default_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            if os.path.exists(default_path):
                pytesseract.pytesseract.tesseract_cmd = default_path
        self.lang = "+".join(['eng' if l == 'en' else l for l in languages])

    def _preprocess_image(self, image_np: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

    def _recover_binary_stream(self, file_bytes: bytes) -> bytes:
        """
        Extreme recovery logic. Scans every byte offset for a valid signature.
        """
        magic_numbers = [
            b'%PDF',      # PDF
            b'\x89PNG',    # PNG
            b'\xff\xd8',  # JPEG
            b'RIFF',      # WebP
            b'GIF8',      # GIF
            b'PK\x03\x04',# Zip/Office
            b'II\x2a\x00',# TIFF
            b'MM\x00\x2a',# TIFF
            b'\x00\x00\x00\x18ftypheic', # HEIC
        ]
        
        # 1. Try a deep brute-force search in the first 4KB
        search_limit = min(len(file_bytes), 4096)
        for i in range(search_limit):
            window = file_bytes[i:i+20]
            for magic in magic_numbers:
                if window.startswith(magic):
                    logger.info(f"DEBUG: RECOVERY SUCCESS! Found {magic!r} at offset {i}")
                    return file_bytes[i:]
        
        # 2. If no magic found, return stripped version as last resort
        return file_bytes.lstrip(b'\x00\r\n ')

    def extract_text(self, file_bytes: bytes, on_progress=None) -> list[dict]:
        if not file_bytes or len(file_bytes) < 10:
            raise ValueError("Empty or invalid file provided")
            
        logger.info(f"DEBUG: File received. Size: {len(file_bytes)} bytes. Raw Header: {file_bytes[:20]!r}")

        # 1. Attempt standard extraction first (fast path)
        try:
            return self._extract_from_pdf(file_bytes, on_progress)
        except Exception:
            try:
                return self._extract_from_image(file_bytes, on_progress)
            except Exception:
                pass

        # 2. Extreme recovery path (slow path)
        logger.info("DEBUG: Standard identification failed. Entering Extreme Recovery Mode...")
        recovered_bytes = self._recover_binary_stream(file_bytes)
        
        try:
            return self._extract_from_pdf(recovered_bytes, on_progress)
        except Exception:
            try:
                return self._extract_from_image(recovered_bytes, on_progress)
            except Exception as e:
                # DIAGNOSTIC: Dump failing file
                try:
                    debug_path = os.path.join("uploads", "failing_file.bin")
                    os.makedirs("uploads", exist_ok=True)
                    with open(debug_path, "wb") as f:
                        f.write(file_bytes)
                    logger.error(f"DIAGNOSTIC: Entire failing file dumped to {debug_path} for inspection")
                except Exception:
                    pass
                    
                raise ValueError(
                    f"Document Engine Error: Unrecognized file format. "
                    f"Size: {len(file_bytes)}. Header: {file_bytes[:10]!r}. "
                    f"Please try a different file format (standard JPG/PNG/PDF)."
                )

    def _extract_from_image(self, image_bytes: bytes, on_progress=None) -> list[dict]:
        if on_progress: on_progress(10)
        
        # Try PIL then OpenCV
        try:
            pil_img = Image.open(io.BytesIO(image_bytes))
            if pil_img.mode != 'RGB':
                pil_img = pil_img.convert('RGB')
            image_np = np.array(pil_img)
            image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        except Exception:
            nparr = np.frombuffer(image_bytes, np.uint8)
            image_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if image_np is None:
                raise ValueError("Image decoding failed")
            
        processed_np = self._preprocess_image(image_np)
        
        if on_progress: on_progress(40)
        
        custom_config = r'--psm 11'
        data = pytesseract.image_to_data(processed_np, lang=self.lang, config=custom_config, output_type=pytesseract.Output.DICT)
        
        results = self._format_tesseract_data(data)
        
        if on_progress: on_progress(100)
        return results

    def _extract_from_pdf(self, pdf_bytes: bytes, on_progress=None) -> list[dict]:
        doc = fitz.open(stream=pdf_bytes)
        num_pages = len(doc)
        if num_pages == 0:
            raise ValueError("No pages found")
            
        all_results = []
        for i, page in enumerate(doc):
            pix = page.get_pixmap(dpi=300)
            img_data = pix.tobytes("png")
            nparr = np.frombuffer(img_data, np.uint8)
            image_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            processed_np = self._preprocess_image(image_np)
            
            custom_config = r'--psm 11'
            data = pytesseract.image_to_data(processed_np, lang=self.lang, config=custom_config, output_type=pytesseract.Output.DICT)
            page_results = self._format_tesseract_data(data)
            
            for res in page_results:
                res['page'] = i + 1
            all_results.extend(page_results)
            
            if on_progress:
                on_progress(int((i + 1) / num_pages * 100))
        
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
