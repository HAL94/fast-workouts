

from typing import Optional
from app.api.v1.schema.category import CategoryBase
from app.core.common.app_response import AppBaseModel


class MuscleGroupBase(AppBaseModel):
    id: Optional[int] = None
    muscle_target: str


class ExerciseBase(AppBaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    is_custom: Optional[bool] = False
    created_by: Optional[int] = None
    categories: Optional[list[CategoryBase]] = None
    muscle_groups: Optional[list[MuscleGroupBase]] = None
