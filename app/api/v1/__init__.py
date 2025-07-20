

from fastapi import APIRouter
from .auth.router import router as auth_router
from .workouts.router import router as workouts_router
from .exercises.router import router as exercise_router
from .muscle_groups.router import router as muscle_group_router
from .categories.router import router as category_router
from .sessions.router import router as session_router


router = APIRouter(prefix="/v1")

router.include_router(auth_router)
router.include_router(workouts_router)
router.include_router(exercise_router)
router.include_router(muscle_group_router)
router.include_router(category_router)
router.include_router(session_router)