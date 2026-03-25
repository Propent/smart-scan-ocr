from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image
import io
import fitz  # PyMuPDF
import os

class PDFService:
    def create_pdf_from_ocr(self, original_bytes: bytes, ocr_results: list[dict]) -> bytes:
        """
        Creates a PDF with the original content and its extracted text.
        """
        output_io = io.BytesIO()
        c = canvas.Canvas(output_io, pagesize=A4)
        a4_width, a4_height = A4

        # If it's a PDF, we'll convert pages to images for the visual part of the scan
        if original_bytes.startswith(b'%PDF'):
            try:
                doc = fitz.open(stream=original_bytes, filetype="pdf")
                images = []
                for page in doc:
                    pix = page.get_pixmap()
                    img_data = pix.tobytes("png")
                    images.append(Image.open(io.BytesIO(img_data)))
                doc.close()
            except Exception as e:
                print(f"DEBUG: PDF conversion failed: {str(e)}")
                raise ValueError(f"Failed to process PDF file: {str(e)}")
        else:
            try:
                images = [Image.open(io.BytesIO(original_bytes))]
            except Exception as e:
                print(f"DEBUG: Image identification failed in PDF generation: {str(e)}")
                raise ValueError(f"Unsupported or invalid image format for PDF: {str(e)}")

        # Add visual pages
        for img in images:
            img_width, img_height = img.size
            scale = min(a4_width / img_width, a4_height / img_height)
            new_width = img_width * scale
            new_height = img_height * scale
            c.drawInlineImage(img, (a4_width - new_width) / 2, (a4_height - new_height) / 2, width=new_width, height=new_height)
            c.showPage()
        
        # Add text pages
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, a4_height - 50, "Extracted Text Results")
        
        c.setFont("Helvetica", 10)
        y_position = a4_height - 80
        
        for res in ocr_results:
            text = res['text']
            page_info = f" [Pg {res.get('page', 1)}]" if 'page' in res else ""
            full_text = text + page_info
            
            if y_position < 50:
                c.showPage()
                c.setFont("Helvetica", 10)
                y_position = a4_height - 50
            
            c.drawString(50, y_position, full_text)
            y_position -= 15
            
        c.save()
        return output_io.getvalue()

pdf_service = PDFService()
