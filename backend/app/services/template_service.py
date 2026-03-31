from docxtpl import DocxTemplate
import io
import os
import pypandoc
from xhtml2pdf import pisa
import tempfile
import logging

# Set up logging
logger = logging.getLogger(__name__)

class TemplateService:
    def fill_docx_template(self, template_bytes: bytes, context: dict) -> bytes:
        """
        Fills a .docx template with the provided context.
        Returns the generated document as bytes.
        """
        template_io = io.BytesIO(template_bytes)
        doc = DocxTemplate(template_io)
        doc.render(context)
        
        output_io = io.BytesIO()
        doc.save(output_io)
        return output_io.getvalue()

    def convert_docx_to_pdf(self, docx_bytes: bytes) -> bytes:
        """
        Converts .docx bytes to a high-quality searchable PDF.
        Uses Pandoc for structural conversion and xhtml2pdf for pure-python rendering.
        This version works on Windows and Linux without extra system dependencies.
        """
        # 1. Save DOCX to temporary file for Pandoc
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as temp_docx:
            temp_docx.write(docx_bytes)
            temp_docx_path = temp_docx.name

        try:
            # 2. Convert DOCX to HTML using Pandoc
            html_content = pypandoc.convert_file(
                temp_docx_path, 
                'html5', 
                format='docx',
                extra_args=['--embed-resources', '--standalone']
            )

            # 3. CRITICAL: xhtml2pdf crashes on modern CSS like :not or :hover
            # We need to strip out CSS blocks that contain pseudo-selectors
            import re
            # Remove modern CSS that xhtml2pdf can't handle
            html_content = re.sub(r'[^}]*:(hover|not|focus|active|visited)[^{]*{[^}]*}', '', html_content)
            # Remove @media queries as well
            html_content = re.sub(r'@media[^{]*{[^}]*}}', '', html_content)
            
            # 4. Convert HTML to PDF using xhtml2pdf (Pure Python)
            pdf_io = io.BytesIO()
            pisa_status = pisa.CreatePDF(html_content, dest=pdf_io)
            
            if pisa_status.err:
                raise RuntimeError(f"PDF conversion failed: {pisa_status.err}")
                
            return pdf_io.getvalue()
        finally:
            # Cleanup
            if os.path.exists(temp_docx_path):
                os.remove(temp_docx_path)

template_service = TemplateService()
