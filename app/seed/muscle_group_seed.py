from typing import Optional
from app.models import MuscleGroup
from app.seed.base_seed import BaseSeed


class MuscleGroupSeed(BaseSeed):
    __model__ = MuscleGroup

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
                unique_fields=["muscle_target"],
            )
            if muscle_group is not None:
                records.append(muscle_group)
        self.data = records
        return records
