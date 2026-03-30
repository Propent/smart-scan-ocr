import easyocr
import numpy as np
from PIL import Image
import io
import fitz  # PyMuPDF
import os
import cv2

class OCRService:
    def __init__(self, languages=['en']):
        # Initialize reader
        self.reader = easyocr.Reader(languages, gpu=False)

    def _preprocess_image(self, image_np: np.ndarray) -> np.ndarray:
        """
        Advanced preprocessing pipeline to handle noisy, tilted, or poorly lit documents.
        """
        # 1. Convert to Grayscale
        gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        
        # 2. Denoising (Removes 'salt and pepper' noise)
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        
        # 3. Deskewing (Straighten the document)
        try:
            coords = np.column_stack(np.where(denoised < 127))
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
                
            if abs(angle) > 0.5: # Only rotate if there's a meaningful tilt
                (h, w) = denoised.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                denoised = cv2.warpAffine(denoised, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        except Exception:
            pass # Skip deskew if it fails for very sparse images

        # 4. Adaptive Thresholding (Fixes uneven lighting/shadows)
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Convert back to RGB for EasyOCR
        return cv2.cvtColor(thresh, cv2.COLOR_GRAY2RGB)

    def extract_text(self, file_bytes: bytes, on_progress=None) -> list[dict]:
        """
        Extracts text from image or PDF bytes.
        """
        if not file_bytes:
            raise ValueError("Empty file provided")
            
        if file_bytes.startswith(b'%PDF'):
            return self._extract_from_pdf(file_bytes, on_progress)
        else:
            try:
                return self._extract_from_image(file_bytes, on_progress)
            except Exception as e:
                raise ValueError(f"Unsupported or invalid file format: {str(e)}")

    def _extract_from_image(self, image_bytes: bytes, on_progress=None) -> list[dict]:
        if on_progress:
            on_progress(10)
        
        nparr = np.frombuffer(image_bytes, np.uint8)
        image_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        processed_np = self._preprocess_image(image_np)
        
        if on_progress:
            on_progress(30)
            
        results = self.reader.readtext(
            processed_np, 
            paragraph=True,
            x_ths=1.0, 
            y_ths=0.5,
            mag_ratio=2.0
        )
        
        results.sort(key=lambda r: (r[0][0][1], r[0][0][0]))
        
        if on_progress:
            on_progress(90)
        return self._format_results_paragraph(results)

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
            
            results = self.reader.readtext(
                processed_np,
                paragraph=True,
                x_ths=1.0,
                y_ths=0.5,
                mag_ratio=2.0
            )
            
            results.sort(key=lambda r: (r[0][0][1], r[0][0][0]))
            
            page_results = self._format_results_paragraph(results)
            for res in page_results:
                res['page'] = i + 1
            all_results.extend(page_results)
            
            if on_progress:
                progress = 5 + int((i + 1) / num_pages * 85)
                on_progress(progress)
        
        doc.close()
        return all_results

    def _format_results_paragraph(self, results) -> list[dict]:
        output = []
        for (bbox, text) in results:
            output.append({
                "text": text,
                "confidence": 1.0,
                "bbox": [list(map(int, point)) for point in bbox]
            })
        return output

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
