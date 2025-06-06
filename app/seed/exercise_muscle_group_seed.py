from typing import Optional

from sqlalchemy.orm import Session
from app.models import Exercise, ExerciseMuscleGroup, MuscleGroup
from app.seed.base_seed import BaseSeed
from app.seed.exercise_seed import ExerciseSeed
from app.seed.muscle_group_seed import MuscleGroupSeed


class ExerciseMuscleGroupSeed(BaseSeed):
    __model__ = ExerciseMuscleGroup

    muscle_groups = {
        "Squat": [
            "Quadriceps",
            "Hamstrings",
            "Glutes",
            "Adductors",
            "Calves",
            "Lower Back",
            "Core",
        ],
        "Deadlift": [
            "Hamstrings",
            "Glutes",
            "Lower Back",
            "Trapezius",
            "Forearms",
            "Core",
            "Quadriceps",
        ],
        "Bench Press": ["Pectoralis Major", "Anterior Deltoids", "Triceps"],
        "Overhead Press (Shoulder Press)": [
            "Anterior Deltoids",
            "Lateral Deltoids",
            "Triceps",
            "Upper Trapezius",
            "Core",
        ],
        "Bent-Over Row": [
            "Latissimus Dorsi",
            "Rhomboids",
            "Trapezius",
            "Posterior Deltoids",
            "Biceps",
            "Forearms",
        ],
        "Pull-up/Chin-up": [
            "Latissimus Dorsi",
            "Biceps",
            "Forearms",
            "Rhomboids",
            "Trapezius",
        ],
        "Lunges": ["Quadriceps", "Hamstrings", "Glutes", "Calves", "Core"],
        "Leg Press": ["Quadriceps", "Hamstrings", "Glutes", "Calves"],
        "Leg Curl": ["Hamstrings"],
        "Leg Extension": ["Quadriceps"],
        "Calf Raises": ["Gastrocnemius", "Soleus"],
        "Bicep Curl": ["Biceps", "Brachialis", "Brachioradialis"],
        "Tricep Extension": ["Triceps"],
        "Lateral Raise": ["Lateral Deltoids"],
        "Front Raise": ["Anterior Deltoids"],
        "Rear Delt Fly": ["Posterior Deltoids", "Rhomboids", "Trapezius"],
        "Shrugs": ["Trapezius"],
        "Plank": [
            "Rectus Abdominis",
            "Obliques",
            "Transverse Abdominis",
            "Lower Back",
            "Shoulders",
            "Glutes",
        ],
        "Crunches/Sit-ups": ["Rectus Abdominis", "Obliques"],
        "Russian Twists": ["Obliques", "Rectus Abdominis", "Transverse Abdominis"],
        "Good Mornings": ["Hamstrings", "Glutes", "Lower Back"],
        "Face Pulls": ["Posterior Deltoids", "Rhomboids", "Trapezius", "Rotator Cuff"],
        "Glute Bridge/Hip Thrust": ["Glutes", "Hamstrings"],
        "Dumbbell Row": [
            "Latissimus Dorsi",
            "Rhomboids",
            "Trapezius",
            "Posterior Deltoids",
            "Biceps",
            "Forearms",
        ],
    }

    def __init__(
        self,
        session: Session,
        exercise_seeder: ExerciseSeed,
        muscle_group_seeder: MuscleGroupSeed,
    ):
        self.exercise_seeder = exercise_seeder
        self.muscle_group_seeder = muscle_group_seeder
        super().__init__(session=session)

    def _create_exercise_muscle_group(
        self, exercise: Exercise, muscle_group: MuscleGroup, is_primary_muscle: bool
    ) -> dict:
        return {
            "exercise_id": exercise.id,
            "muscle_group_id": muscle_group.id,
            "is_primary_muscle": is_primary_muscle,
        }

    def create_many(
        self, size: Optional[int] = len(muscle_groups)
    ) -> list[ExerciseMuscleGroup]:
        records = []
        if self.seeded:
            return self.data
        seeded_exercises = self.exercise_seeder.create_many()
        seeded_muscle_groups = self.muscle_group_seeder.create_many()
        for exercise in seeded_exercises:
            if exercise is None:
                continue
            
            muscle_groups_for_exercise = self.muscle_groups[exercise.name]
            matching_muscle_groups = [
                mg
                for mg in seeded_muscle_groups
                if mg.muscle_target in muscle_groups_for_exercise
            ]
            for matched_muscle in matching_muscle_groups:
                exercise_muscle_group_data = self._create_exercise_muscle_group(
                    exercise=exercise,
                    muscle_group=matched_muscle,
                    is_primary_muscle=matched_muscle.muscle_target
                    == muscle_groups_for_exercise[0],
                )
                result = self.upsert_record(
                    data=exercise_muscle_group_data,
                    unique_fields=["exercise_id", "muscle_group_id"],
                )
                if result is not None:
                    records.append(result)
        self.data = records
        self.seeded = True
        return records
