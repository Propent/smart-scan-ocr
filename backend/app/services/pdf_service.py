import fitz  # PyMuPDF
import io

class PDFService:
    def create_pdf_from_ocr(self, original_bytes: bytes, ocr_results: list[dict]) -> bytes:
        """
        Creates a SEARCHABLE PDF using native image dimensions for perfect text alignment.
        """
        doc = fitz.open()

        # 1. Prepare visual pages
        if original_bytes.startswith(b'%PDF'):
            src_doc = fitz.open(stream=original_bytes, filetype="pdf")
            images = []
            for page in src_doc:
                pix = page.get_pixmap(dpi=300)
                images.append({"bytes": pix.tobytes("png"), "w": pix.width, "h": pix.height})
            src_doc.close()
        else:
            # For images, get dimensions directly
            img_doc = fitz.open(stream=original_bytes)
            img_page = img_doc[0]
            images = [{"bytes": original_bytes, "w": img_page.rect.width, "h": img_page.rect.height}]
            img_doc.close()

        # 2. Build PDF
        for i, img_data in enumerate(images):
            # Create page with EXACT same dimensions as the image
            page = doc.new_page(width=img_data["w"], height=img_data["h"])
            
            # Insert the image to fill the page
            page.insert_image(page.rect, stream=img_data["bytes"])
            
            # Filter OCR results for this page
            page_num = i + 1
            page_text_results = [res for res in ocr_results if res.get('page', 1) == page_num]
            
            for res in page_text_results:
                text = res['text']
                bbox = res['bbox'] # [[x, y], [x+w, y], [x+w, y+h], [x, y+h]]
                
                # Native coordinates (no scaling needed now)
                x0, y0 = bbox[0][0], bbox[0][1]
                x1, y1 = bbox[2][0], bbox[2][1]
                
                # Rectangle for the text
                rect = fitz.Rect(x0, y0, x1, y1)
                
                # Calculate font size to fill the height of the box
                font_size = max(1, rect.height * 0.8)
                
                try:
                    # Insert text at the bottom-left of the OCR box
                    # render_mode=3 makes it invisible but searchable
                    page.insert_text(
                        fitz.Point(x0, y1), 
                        text,
                        fontsize=font_size,
                        fontname="helv",
                        render_mode=3
                    )
                except Exception:
                    continue

        return doc.tobytes()

pdf_service = PDFService()
