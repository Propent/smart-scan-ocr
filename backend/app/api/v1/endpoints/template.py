from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Response
from app.services.template_service import template_service
import json

router = APIRouter()


@router.post("/generate")
async def generate_document(
    template_file: UploadFile = File(...),
    context: str = Form(...),  # Context as a JSON string
):
    """
    Generate a document from a .docx template and a context mapping.
    """
    filename: str = template_file.filename  # type: ignore[assignment]
    if filename and not filename.endswith(".docx"):
        raise HTTPException(
            status_code=400, detail="Only .docx templates are supported."
        )

    try:
        # Parse context JSON
        context_dict = json.loads(context)

        template_bytes = await template_file.read()
        generated_docx = template_service.fill_docx_template(
            template_bytes, context_dict
        )

        return Response(
            content=generated_docx,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename=generated_{template_file.filename}"
            },
        )
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in 'context' field.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
