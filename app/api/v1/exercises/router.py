
from fastapi import APIRouter, Depends, Query

from app.api.v1.exercises.schema import ExerciseListReadPagination
from app.api.v1.exercises.services.exercise_service import ExerciseService
from app.core.common.app_response import AppResponse
from app.dependencies.services import get_exercise_service


router: APIRouter = APIRouter(prefix="/exercises")

@router.get("/")
async def get_exercises(
    pagination: ExerciseListReadPagination = Query(...),
    exercise_service: ExerciseService = Depends(get_exercise_service)
):
    result = await exercise_service.get_many_exercises(pagination=pagination)
    return AppResponse(data=result)

@router.get("/{muscle_group_id}")
async def get_exercises_by_muscle(muscle_group_id: int, exercise_service: ExerciseService = Depends(get_exercise_service)):
    result = await exercise_service.get_exercies_by_muscle(muscle_group_id=muscle_group_id)
    return AppResponse(data=result)
