"""
Receipt endpoints: upload and process receipt image via GPT-4o
"""
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form
from kaihelper.utils.image_normalizer import to_jpeg_bytes

router = APIRouter()


@router.post("/upload")
async def upload_receipt(user_id: int = Form(...), file: UploadFile = File(...), request: Request = None):
    """
    Upload a receipt image, process it through GPT-4o Vision, 
    extract items, and map them into groceries and expenses.
    """
    service = request.app.state.services.get_receipt_service()
    #image_bytes = await file.read()
    #result = service.process_receipt(user_id, image_bytes)

    image_raw = await file.read()
    
    try:
        image_bytes = to_jpeg_bytes(image_raw)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {e}")

    result = service.process_receipt(user_id, image_bytes)

    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)

    return {
        "success": True,
        "message": result.message,
        "data": result.data
    }
