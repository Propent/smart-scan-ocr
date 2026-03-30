from docxtpl import DocxTemplate
import io
import os
import pypandoc
import tempfile
import logging

# Set up logging
logger = logging.getLogger(__name__)

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except OSError:
    logger.warning("WeasyPrint dependencies (GTK) not found. PDF conversion will be disabled locally.")
    WEASYPRINT_AVAILABLE = False
except ImportError:
    logger.warning("WeasyPrint not installed. PDF conversion will be disabled.")
    WEASYPRINT_AVAILABLE = False

class TemplateService:
    def fill_docx_template(self, template_bytes: bytes, context: dict) -> bytes:
        """
        Fills a .docx template with the provided context.
        Returns the generated document as bytes.
        """
        template_io = io.BytesIO(template_bytes)
        doc = DocxTemplate(template_io)
        
        # Context is a dictionary of key-value pairs to replace in the template
        doc.render(context)
        
        output_io = io.BytesIO()
        doc.save(output_io)
        return output_io.getvalue()

    def convert_docx_to_pdf(self, docx_bytes: bytes) -> bytes:
        """
        Converts .docx bytes to a high-quality searchable PDF.
        Uses Pandoc for structural conversion and WeasyPrint for PDF rendering.
        """
        if not WEASYPRINT_AVAILABLE:
            raise RuntimeError(
                "PDF conversion is not available on this system because GTK/WeasyPrint dependencies are missing. "
                "This feature works fully on the Render/Docker deployment."
            )

        # We need temporary files because Pandoc works best with file paths
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as temp_docx:
            temp_docx.write(docx_bytes)
            temp_docx_path = temp_docx.name

        try:
            # 1. Convert DOCX to HTML using Pandoc (preserves structure best)
            html_content = pypandoc.convert_file(temp_docx_path, 'html5', format='docx')
            
            # 2. Convert HTML to PDF using WeasyPrint
            pdf_io = io.BytesIO()
            HTML(string=html_content).write_pdf(pdf_io)
            return pdf_io.getvalue()
        finally:
            # Cleanup
            if os.path.exists(temp_docx_path):
                os.remove(temp_docx_path)

template_service = TemplateService()
