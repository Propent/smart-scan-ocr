from docxtpl import DocxTemplate
import io
import os

class TemplateService:
    def fill_docx_template(self, template_bytes: bytes, context: dict) -> bytes:
        """
        Fills a .docx template with the provided context.
        Returns the generated document as bytes.
        """
        template_io = io.BytesIO(template_bytes)
        doc = DocxTemplate(template_io)
        
        # Context is a dictionary of key-value pairs to replace in the template
        # template placeholders like {{ name }}, {{ date }} etc.
        doc.render(context)
        
        output_io = io.BytesIO()
        doc.save(output_io)
        return output_io.getvalue()

template_service = TemplateService()
