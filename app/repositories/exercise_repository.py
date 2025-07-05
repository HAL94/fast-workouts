

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.api.v1.exercises.schema import ExerciseByMuscleResponse
from app.api.v1.schema.exercise import ExerciseBase
from app.core.database.base_repo import BaseRepo
from app.models import Exercise, ExerciseMuscleGroup


class ExerciseRepository(BaseRepo[Exercise, ExerciseBase]):
    __dbmodel__ = Exercise
    __model__ = ExerciseBase

    async def get_exercies_by_muscle(self, muscle_group_id: int) -> list[ExerciseBase]:
        stmt = select(Exercise).join(
            ExerciseMuscleGroup, ExerciseMuscleGroup.exercise_id == Exercise.id
        ).where(
            ExerciseMuscleGroup.muscle_group_id == muscle_group_id
        ).options(
            selectinload(Exercise.categories)
        )
        result = await self.session.scalars(stmt)

        return [ExerciseByMuscleResponse.model_validate(item, from_attributes=True) for item in result.all()]
