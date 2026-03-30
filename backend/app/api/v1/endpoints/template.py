from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Response
from app.services.template_service import template_service
import json
from typing import Optional

router = APIRouter()


@router.post("/generate")
async def generate_document(
    template_file: UploadFile = File(...),
    context: str = Form(...),  # Context as a JSON string
    output_format: Optional[str] = Form("pdf"), # Default to pdf
):
    """
    Generate a document from a .docx template and a context mapping.
    Can return either filled .docx or high-quality converted .pdf.
    """
    filename: str = template_file.filename  # type: ignore[assignment]
    if filename and not filename.endswith(".docx"):
        raise HTTPException(
            status_code=400, detail="Only .docx templates are supported as input."
        )

    try:
        # Parse context JSON
        context_dict = json.loads(context)

        # 1. Fill the template (always results in docx)
        template_bytes = await template_file.read()
        generated_docx = template_service.fill_docx_template(
            template_bytes, context_dict
        )

        # 2. Convert if PDF requested
        if output_format and output_format.lower() == "pdf":
            final_content = template_service.convert_docx_to_pdf(generated_docx)
            media_type = "application/pdf"
            ext = "pdf"
        else:
            final_content = generated_docx
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ext = "docx"

        return Response(
            content=final_content,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename=generated_{template_file.filename.split('.')[0]}.{ext}"
            },
        )
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in 'context' field.")
    except Exception as e:
        # Pypandoc might raise errors if pandoc is missing on the system
        raise HTTPException(status_code=500, detail=f"Document generation failed: {str(e)}")
