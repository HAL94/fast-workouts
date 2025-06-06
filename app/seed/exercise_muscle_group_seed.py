from typing import Optional

from sqlalchemy.orm import Session
from app.models import ExerciseMuscleGroup
from app.seed.base_seed import BaseSeed
from app.seed.constants import exercise_name_to_id, muscle_group_to_id, muscle_groups
from app.seed.exercise_seed import ExerciseSeed
from app.seed.muscle_group_seed import MuscleGroupSeed


class ExerciseMuscleGroupSeed(BaseSeed):
    __model__ = ExerciseMuscleGroup

    def __init__(
        self,
        session: Session,
        exercise_seeder: ExerciseSeed,
        muscle_group_seeder: MuscleGroupSeed,
    ):
        self.exercise_seeder = exercise_seeder
        self.muscle_group_seeder = muscle_group_seeder
        super().__init__(session=session)

    def create_exercise_muscle_group(
        self, exercise_id: int, muscle_group_id: int, is_primary_muscle: bool
    ) -> ExerciseMuscleGroup | None:
        exercise_group_data = {
            "exercise_id": exercise_id,
            "muscle_group_id": muscle_group_id,
            "is_primary_muscle": is_primary_muscle,
        }
        return self.upsert_record(exercise_group_data, unique_fields=["exercise_id", "muscle_group_id"])
        

    def create_many(
        self, size: Optional[int] = len(muscle_groups)
    ) -> list[ExerciseMuscleGroup]:
        records = []
        if self.seeded:
            return self.data

        self.exercise_seeder.create_many()
        self.muscle_group_seeder.create_many()
        self.session.commit()

        for exercise_name in muscle_groups.keys():
            muscle_groups_per_exercise = muscle_groups[exercise_name]
            for muscle_group in muscle_groups_per_exercise:
                muscle_group_id = muscle_group_to_id[muscle_group]
                exercise_id = exercise_name_to_id[exercise_name]
                exercise_muscle_group_data = self.create_exercise_muscle_group(
                    exercise_id=exercise_id,
                    muscle_group_id=muscle_group_id,
                    is_primary_muscle=muscle_group == muscle_groups_per_exercise[0],
                )
                if exercise_muscle_group_data is not None:
                    records.append(exercise_muscle_group_data)

        self.session.commit()
        self.data = records
        self.seeded = True
        return records
