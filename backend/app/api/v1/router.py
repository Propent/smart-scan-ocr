from fastapi import APIRouter
from app.api.v1.endpoints import ocr, template

api_router = APIRouter()
api_router.include_router(ocr.router, prefix="/ocr", tags=["ocr"])
api_router.include_router(template.router, prefix="/template", tags=["template"])
