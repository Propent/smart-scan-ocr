from fastapi import APIRouter, UploadFile, File, HTTPException, Response, BackgroundTasks
from app.services.ocr_service import ocr_service
from app.services.pdf_service import pdf_service
from app.core.tasks import task_store
import io

router = APIRouter()


@router.post("/extract")
async def extract_text_from_file(file: UploadFile = File(...)):
    """
    Extract text from an uploaded file using EasyOCR.
    No restrictions on file type at the API level.
    """
    contents = await file.read()

    try:
        results = ocr_service.extract_text(contents)
        return {"filename": file.filename, "results": results}
    except Exception as e:
        # If OCR/Image opening fails because of format, return 400
        raise HTTPException(status_code=400, detail=f"Could not process file: {str(e)}")

@router.post("/scan-to-pdf")
async def scan_to_pdf(file: UploadFile = File(...)):
    """
    Take a file, run OCR, and return a PDF with image and text.
    No restrictions on file type at the API level.
    """
    contents = await file.read()

    try:
        # 1. OCR
        results = ocr_service.extract_text(contents)
        
        # 2. PDF generation
        pdf_bytes = pdf_service.create_pdf_from_ocr(contents, results)
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=scan_{file.filename}.pdf"
            },
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not process file: {str(e)}")

def run_ocr_task(task_id: str, file_contents: bytes, filename: str):
    try:
        def update_progress(p):
            task_store.update_task(task_id, progress=p)

        # 1. OCR with progress callback
        # _extract_from_pdf and _extract_from_image are already reporting up to ~90
        results = ocr_service.extract_text(file_contents, on_progress=update_progress)
        
        # 2. PDF generation (last 5-10%)
        task_store.update_task(task_id, progress=95)
        pdf_bytes = pdf_service.create_pdf_from_ocr(file_contents, results)
        
        # Mark as complete
        task_store.update_task(
            task_id, 
            status="completed", 
            progress=100, 
            result=pdf_bytes,
            result_data=results # Store the text results too
        )
    except Exception as e:
        task_store.update_task(task_id, status="failed", error=str(e))

@router.post("/scan-to-pdf-async")
async def scan_to_pdf_async(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Asynchronous version of scan-to-pdf. Returns a task ID for status polling.
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
    
    # Don't return the bytes in the status check
    return {
        "status": task["status"],
        "progress": task["progress"],
        "error": task["error"],
        "result_data": task.get("result_data")
    }

@router.get("/download/{task_id}")
async def download_task_result(task_id: str):
    """
    Download the generated PDF for a completed task.
    """
    task = task_store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"Task is in state: {task['status']}")
    
    return Response(
        content=task["result"],
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=ocr_result.pdf"
        },
    )
