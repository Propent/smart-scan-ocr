from fastapi import APIRouter, UploadFile, File, HTTPException, Response, BackgroundTasks
from app.services.ocr_service import ocr_service
from app.services.pdf_service import pdf_service
from app.services.template_service import template_service
from app.core.tasks import task_store
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

def run_ocr_task(task_id: str, file_bytes: bytes, filename: str):
    try:
        # 1. If it's a .docx, convert to PDF first
        if filename.lower().endswith(".docx"):
            task_store.update_task(task_id, progress=10, status="converting")
            file_bytes = template_service.convert_docx_to_pdf(file_bytes)
            # Update filename for the rest of the process
            filename = filename.rsplit(".", 1)[0] + ".pdf"

        # 2. Perform OCR extraction
        task_store.update_task(task_id, progress=20, status="processing")
        results = ocr_service.extract_text(
            file_bytes, 
            on_progress=lambda p: task_store.update_task(task_id, progress=20 + (p * 0.6))
        )
        
        # 3. Generate Searchable PDF
        task_store.update_task(task_id, progress=85, status="generating")
        pdf_bytes = pdf_service.create_pdf_from_ocr(file_bytes, results)
        
        # 4. Mark as complete
        task_store.update_task(
            task_id, 
            status="completed", 
            progress=100, 
            result=pdf_bytes,
            result_data=results
        )
    except Exception as e:
        logger.error(f"OCR Task failed: {str(e)}")
        task_store.update_task(task_id, status="failed", error=str(e))

@router.post("/scan-to-pdf-async")
async def scan_to_pdf_async(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Asynchronous version of scan-to-pdf. Returns a task ID for status polling.
    Now supports Images, PDFs, and .docx files.
    """
    contents = await file.read()
    task_id = task_store.create_task()
    
    background_tasks.add_task(run_ocr_task, task_id, contents, file.filename)
    
    return {"task_id": task_id}

@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """
    Check the status and progress of an OCR task.
    """
    task = task_store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "status": task["status"],
        "progress": task["progress"],
        "error": task["error"],
        "result_data": task.get("result_data")
    }

@router.get("/download/{task_id}")
async def download_result(task_id: str):
    """
    Download the resulting searchable PDF.
    """
    task = task_store.get_task(task_id)
    if not task or task["status"] != "completed":
        raise HTTPException(status_code=404, detail=f"Result not ready. State: {task['status'] if task else 'Unknown'}")
    
    return Response(
        content=task["result"],
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=ocr_result.pdf"
        },
    )
