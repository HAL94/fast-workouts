from app.models import Exercise
from app.seed.base_seed import BaseSeed
from app.seed.constants import exercises_list


class ExerciseSeed(BaseSeed):
    __model__ = Exercise

    def create_exercise(self, exercise_name: str) -> Exercise | None:
        exercise_data = {"name": exercise_name, "description": "details"}
        item = self.upsert_record(data=exercise_data, unique_fields=["name"])
        return item

    def create_many(self) -> list[Exercise]:
        records = []
        if self.seeded:
            return self.data
        for exercise_dict in exercises_list:
            exercise_record = self.create_exercise(exercise_name=exercise_dict.get("name"))
            if exercise_record is not None:
                records.append(exercise_record)
        self.data = records
        self.seeded = True
        return records
