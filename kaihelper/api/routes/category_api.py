"""
Category endpoints: create, list
"""
from fastapi import APIRouter, HTTPException, Request
from kaihelper.contracts.category_dto import CategoryDTO

router = APIRouter()

@router.post("/")
def create_category(dto: CategoryDTO, request: Request):
    service = request.app.state.services.get_category_service()
    result = service.add_category(dto)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.message)
    return {"success": True, "message": result.message, "data": result.data}

@router.get("/")
def list_categories(request: Request):
    service = request.app.state.services.get_category_service()
    result = service.list_categories()
    if not result.success:
        raise HTTPException(status_code=404, detail=result.message)
    return {"success": True, "message": result.message, "data": result.data}
