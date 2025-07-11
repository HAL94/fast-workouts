

from fastapi import APIRouter, Depends

from app.api.v1.categories.service import CategoryService
from app.core.common.app_response import AppResponse
from app.dependencies.services import get_category_service


router: APIRouter = APIRouter(prefix="/categories")


@router.get("/")
async def get_all_categories(
    category_service: CategoryService = Depends(get_category_service),
):
    result = await category_service.get_all_categories()
    return AppResponse(data=result)


@router.get("/{category_id}")
async def get_category_by_id(
    category_id: int,
    category_service: CategoryService = Depends(get_category_service),

):
    result = await category_service.get_one_category(category_id=category_id)
    return AppResponse(data=result)


@router.get("/{category_id}/exercises")
async def get_exercises_by_category(
    category_id: int,
    category_service: CategoryService = Depends(get_category_service)
):
    result = await category_service.get_exercises_by_category(category_id=category_id)
    return AppResponse(data=result)
