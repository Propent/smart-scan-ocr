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
                # We need the original page dimensions
                pix = page.get_pixmap(dpi=300)
                images.append({"bytes": pix.tobytes("png"), "w": page.rect.width, "h": page.rect.height})
            src_doc.close()
        else:
            # For images, get dimensions directly from the image file
            img_doc = fitz.open(stream=original_bytes)
            img_rect = img_doc[0].rect
            images = [{"bytes": original_bytes, "w": img_rect.width, "h": img_rect.height}]
            img_doc.close()

        # 2. Build PDF
        for i, img_data in enumerate(images):
            # Create page with EXACT same dimensions as the original (in points)
            page = doc.new_page(width=img_data["w"], height=img_data["h"])
            
            # Insert the image to fill the page
            page.insert_image(page.rect, stream=img_data["bytes"])
            
            # Filter OCR results for this page
            page_num = i + 1
            page_text_results = [res for res in ocr_results if res.get('page', 1) == page_num]
            
            for res in page_text_results:
                text = res['text']
                bbox = res['bbox'] # [[x, y], [x+w, y], [x+w, y+h], [x, y+h]]
                
                # These coordinates are now scaled correctly to the original image/PDF page
                x0, y0 = bbox[0][0], bbox[0][1]
                x1, y1 = bbox[2][0], bbox[2][1]
                
                # Calculate font size to match the box height
                # Helvetica height is roughly 0.7-0.8 of font size
                font_size = max(1, (y1 - y0) * 0.85)
                
                try:
                    # Insert text at the bottom-left baseline
                    # render_mode=3 makes it invisible but selectable/searchable
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
