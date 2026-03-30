from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image
import io
import fitz  # PyMuPDF
import os

class PDFService:
    def create_pdf_from_ocr(self, original_bytes: bytes, ocr_results: list[dict]) -> bytes:
        """
        Creates a SEARCHABLE PDF with an invisible text layer overlaying the visual scan.
        """
        output_io = io.BytesIO()
        c = canvas.Canvas(output_io, pagesize=A4)
        a4_w, a4_h = A4

        # 1. Get visual pages (as high-res images for the PDF background)
        if original_bytes.startswith(b'%PDF'):
            doc = fitz.open(stream=original_bytes, filetype="pdf")
            images = []
            for page in doc:
                pix = page.get_pixmap(dpi=300) # Ensure high visual quality
                img_data = pix.tobytes("png")
                images.append(Image.open(io.BytesIO(img_data)))
            doc.close()
        else:
            images = [Image.open(io.BytesIO(original_bytes))]

        # 2. Add visual pages and their corresponding invisible text
        for i, img in enumerate(images):
            img_w, img_h = img.size
            scale_x = a4_w / img_w
            scale_y = a4_h / img_h
            
            # Draw the visual background (the "scan")
            c.drawInlineImage(img, 0, 0, width=a4_w, height=a4_h)
            
            # Overlay invisible text layer for this page
            page_num = i + 1
            page_text = [res for res in ocr_results if res.get('page', 1) == page_num]
            
            # Set font for the invisible layer
            c.setFont("Helvetica", 8)
            text_object = c.beginText()
            
            # We use a transparent fill for the text to make it invisible but selectable
            c.setFillAlpha(0.0) 
            
            for res in page_text:
                text = res['text']
                bbox = res['bbox'] # Format: [[tl_x, tl_y], [tr_x, tr_y], [br_x, br_y], [bl_x, bl_y]]
                
                # Use the top-left coordinate, scaled to A4 size
                # Note: ReportLab Y coordinate starts from bottom
                x = bbox[0][0] * scale_x
                y = a4_h - (bbox[0][1] * scale_y)
                
                c.drawString(x, y, text)
            
            c.showPage()
            
        c.save()
        return output_io.getvalue()

pdf_service = PDFService()
