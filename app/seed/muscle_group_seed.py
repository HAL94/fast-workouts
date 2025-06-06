from app.models import MuscleGroup
from app.seed.base_seed import BaseSeed
from app.seed.constants import all_unique_muscle_groups


class MuscleGroupSeed(BaseSeed):
    __model__ = MuscleGroup

    def create_muscle_group(self, muscle_group: str) -> dict:
        return {"muscle_target": muscle_group}

    def create_many(
        self
    ) -> list[MuscleGroup]:
        records = []
        if self.seeded:
            return self.data        
        for muscle_dict in all_unique_muscle_groups:
            muscle_group = self.upsert_record(
                data=self.create_muscle_group(muscle_group=muscle_dict.get("name")),
                unique_fields=["muscle_target"],
            )
            if muscle_group is not None:
                records.append(muscle_group)
        
        self.data = records
        self.seeded = True
        return records
