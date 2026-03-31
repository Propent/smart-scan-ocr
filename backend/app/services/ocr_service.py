import pytesseract
import numpy as np
from PIL import Image, ImageEnhance
import io
import fitz  # PyMuPDF
import cv2
import os
import sys
import logging

# Standard logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app.services.ocr")

class OCRService:
    def __init__(self, languages=['en']):
        if sys.platform == "win32":
            default_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            if os.path.exists(default_path):
                pytesseract.pytesseract.tesseract_cmd = default_path
        self.lang = "+".join(['eng' if l == 'en' else l for l in languages])

    def _preprocess(self, image_np: np.ndarray, mode='standard') -> tuple[np.ndarray, float]:
        """
        Production-grade image preprocessing.
        Returns: (processed_image, scale_factor)
        """
        # 1. Convert to Grayscale
        if len(image_np.shape) == 3:
            gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
        else:
            gray = image_np

        # 2. Rescale (Tesseract performs best when height is ~30-50 pixels per char)
        h, w = gray.shape
        scale = 1.0
        if w < 1500:
            scale = 2000 / w
            gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

        if mode == 'sharpened':
            # 3. Enhance Sharpness and Contrast
            pil_img = Image.fromarray(gray)
            pil_img = ImageEnhance.Contrast(pil_img).enhance(2.0)
            pil_img = ImageEnhance.Sharpness(pil_img).enhance(2.5)
            gray = np.array(pil_img)

        # 4. Adaptive Thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )

        return thresh, scale

    def _extract_single_attempt(self, img_np: np.ndarray, config: str, scale: float) -> list[dict]:
        data = pytesseract.image_to_data(img_np, lang=self.lang, config=config, output_type=pytesseract.Output.DICT)
        return self._format_tesseract_data(data, scale)

    def _recover_binary_stream(self, file_bytes: bytes) -> bytes:
        magic_numbers = [b'%PDF', b'\x89PNG', b'\xff\xd8', b'RIFF', b'PK\x03\x04']
        for magic in magic_numbers:
            idx = file_bytes.find(magic, 0, 4096)
            if idx != -1: return file_bytes[idx:]
        return file_bytes.lstrip(b'\x00\r\n ')

    def extract_text(self, file_bytes: bytes, on_progress=None) -> list[dict]:
        if not file_bytes or len(file_bytes) < 10: raise ValueError("Invalid file")
        cleaned_bytes = self._recover_binary_stream(file_bytes)
        if cleaned_bytes.startswith(b'%PDF'):
            return self._extract_from_pdf(cleaned_bytes, on_progress)
        else:
            return self._extract_from_image(cleaned_bytes, on_progress)

    def _extract_from_image(self, image_bytes: bytes, on_progress=None) -> list[dict]:
        if on_progress: on_progress(10)
        try:
            pil_img = Image.open(io.BytesIO(image_bytes))
            if pil_img.mode != 'RGB': pil_img = pil_img.convert('RGB')
            image_np = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        except Exception:
            nparr = np.frombuffer(image_bytes, np.uint8)
            image_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if image_np is None: raise ValueError("Decoding failed")

        if on_progress: on_progress(20)

        # Attempt 1: Standard Preprocessing
        prep_std, scale_std = self._preprocess(image_np, mode='standard')
        res_std = self._extract_single_attempt(prep_std, '--psm 11', scale_std)
        conf_std = sum([r['confidence'] for r in res_std]) / len(res_std) if res_std else 0

        # Attempt 2: High Sharpening (if std failed or low confidence)
        if conf_std < 0.7:
            prep_sharp, scale_sharp = self._preprocess(image_np, mode='sharpened')
            res_sharp = self._extract_single_attempt(prep_sharp, '--psm 11', scale_sharp)
            conf_sharp = sum([r['confidence'] for r in res_sharp]) / len(res_sharp) if res_sharp else 0
            
            if conf_sharp > conf_std:
                if on_progress: on_progress(100)
                return res_sharp

        if on_progress: on_progress(100)
        return res_std

    def _extract_from_pdf(self, pdf_bytes: bytes, on_progress=None) -> list[dict]:
        doc = fitz.open(stream=pdf_bytes)
        all_results = []
        for i, page in enumerate(doc):
            pix = page.get_pixmap(dpi=300)
            img_data = pix.tobytes("png")
            # PDF pages are extracted at 300 DPI, so we need to scale boxes back to PDF points
            # fitz pixmap width/height vs page width/height
            scale_x = pix.width / page.rect.width
            scale_y = pix.height / page.rect.height
            
            # Treat each page as an image
            page_results = self._extract_from_image(img_data)
            
            # Adjust coordinates back to PDF points
            for res in page_results:
                res['page'] = i + 1
                for point in res['bbox']:
                    point[0] /= scale_x
                    point[1] /= scale_y
            
            all_results.extend(page_results)
            if on_progress: on_progress(int((i + 1) / len(doc) * 100))
        doc.close()
        return all_results

    def _format_tesseract_data(self, data, scale: float) -> list[dict]:
        output = []
        for i in range(len(data['text'])):
            text = data['text'][i].strip()
            if text and float(data['conf'][i]) > 15:
                # Scale coordinates back to original image space
                x, y, w, h = data['left'][i] / scale, data['top'][i] / scale, data['width'][i] / scale, data['height'][i] / scale
                output.append({
                    "text": text,
                    "confidence": float(data['conf'][i]) / 100.0,
                    "bbox": [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]
                })
        return output

ocr_service = OCRService()
