

from fastapi import APIRouter
from .auth.router import router as auth_router
from .workouts.router import router as workouts_router
from .exercise_plans.router import router as exercise_plans_router

router = APIRouter(prefix="/v1")

router.include_router(auth_router)
router.include_router(workouts_router)
router.include_router(exercise_plans_router)