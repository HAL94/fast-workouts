from typing import Optional
from app.models import MuscleGroup
from app.seed.base_seed import BaseSeed


class MuscleGroupSeed(BaseSeed):
    __model__ = MuscleGroup

    # muscle_groups = {
    #     "Squat": [
    #         "Quadriceps",
    #         "Hamstrings",
    #         "Glutes",
    #         "Adductors",
    #         "Calves",
    #         "Lower Back",
    #         "Core",
    #     ],
    #     "Deadlift": [
    #         "Hamstrings",
    #         "Glutes",
    #         "Lower Back",
    #         "Trapezius",
    #         "Forearms",
    #         "Core",
    #         "Quadriceps",
    #     ],
    #     "Bench Press": ["Pectoralis Major", "Anterior Deltoids", "Triceps"],
    #     "Overhead Press (Shoulder Press)": [
    #         "Anterior Deltoids",
    #         "Lateral Deltoids",
    #         "Triceps",
    #         "Upper Trapezius",
    #         "Core",
    #     ],
    #     "Bent-Over Row": [
    #         "Latissimus Dorsi",
    #         "Rhomboids",
    #         "Trapezius",
    #         "Posterior Deltoids",
    #         "Biceps",
    #         "Forearms",
    #     ],
    #     "Pull-up/Chin-up": [
    #         "Latissimus Dorsi",
    #         "Biceps",
    #         "Forearms",
    #         "Rhomboids",
    #         "Trapezius",
    #     ],
    #     "Lunges": ["Quadriceps", "Hamstrings", "Glutes", "Calves", "Core"],
    #     "Leg Press": ["Quadriceps", "Hamstrings", "Glutes", "Calves"],
    #     "Leg Curl": ["Hamstrings"],
    #     "Leg Extension": ["Quadriceps"],
    #     "Calf Raises": ["Gastrocnemius", "Soleus"],
    #     "Bicep Curl": ["Biceps", "Brachialis", "Brachioradialis"],
    #     "Tricep Extension": ["Triceps"],
    #     "Lateral Raise": ["Lateral Deltoids"],
    #     "Front Raise": ["Anterior Deltoids"],
    #     "Rear Delt Fly": ["Posterior Deltoids", "Rhomboids", "Trapezius"],
    #     "Shrugs": ["Trapezius"],
    #     "Plank": [
    #         "Rectus Abdominis",
    #         "Obliques",
    #         "Transverse Abdominis",
    #         "Lower Back",
    #         "Shoulders",
    #         "Glutes",
    #     ],
    #     "Crunches/Sit-ups": ["Rectus Abdominis", "Obliques"],
    #     "Russian Twists": ["Obliques", "Rectus Abdominis", "Transverse Abdominis"],
    #     "Good Mornings": ["Hamstrings", "Glutes", "Lower Back"],
    #     "Face Pulls": ["Posterior Deltoids", "Rhomboids", "Trapezius", "Rotator Cuff"],
    #     "Glute Bridge/Hip Thrust": ["Glutes", "Hamstrings"],
    #     "Dumbbell Row": [
    #         "Latissimus Dorsi",
    #         "Rhomboids",
    #         "Trapezius",
    #         "Posterior Deltoids",
    #         "Biceps",
    #         "Forearms",
    #     ],
    # }

    all_unique_muscle_groups = [
        "Adductors",
        "Anterior Deltoids",
        "Biceps",
        "Brachialis",
        "Brachioradialis",
        "Calves",
        "Core",
        "Forearms",
        "Gastrocnemius",
        "Glutes",
        "Hamstrings",
        "Latissimus Dorsi",
        "Lateral Deltoids",
        "Lower Back",
        "Obliques",
        "Pectoralis Major",
        "Posterior Deltoids",
        "Quadriceps",
        "Rectus Abdominis",
        "Rhomboids",
        "Rotator Cuff",
        "Shoulders",
        "Soleus",
        "Transverse Abdominis",
        "Trapezius",
        "Triceps",
        "Upper Trapezius",
    ]

    def _create_muscle_group(self, muscle_group: str) -> dict:
        return {"muscle_target": muscle_group}

    def create_many(self, size: Optional[int] = 27) -> list[MuscleGroup]:
        records = []
        partial_list = self.all_unique_muscle_groups[:size]
        for muscle_name in partial_list:
            muscle_group = self.upsert_record(
                data=self._create_muscle_group(muscle_group=muscle_name),
                unique_field="muscle_target",
            )
            records.append(muscle_group)

        return records
