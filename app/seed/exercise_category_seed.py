from sqlalchemy.orm import Session
from app.models import ExerciseCategory
from app.seed.category_seed import CategorySeed
from app.seed.base_seed import BaseSeed
from app.seed.constants import exercise_category_to_id, exercise_name_to_id, exercises_by_categories
from app.seed.exercise_seed import ExerciseSeed


class ExerciseCategoryMapSeed(BaseSeed):
    __model__ = ExerciseCategory

    def __init__(
        self,
        session: Session,
        exercise_seeder: ExerciseSeed,
        category_seeder: CategorySeed,
    ):
        self.exercise_seeder = exercise_seeder
        self.category_seeder = category_seeder
        super().__init__(session)

    def create_exercise_category(
        self, category_id: int, exercise_id: int
    ) -> ExerciseCategory | None:
        exercise_category = {
            "category_id": category_id,
            "exercise_id": exercise_id,
        }
        created_exercise_category = self.upsert_record(
            exercise_category, unique_fields=["exercise_id", "category_id"]
        )

        if not created_exercise_category:
            return None

        return created_exercise_category

    def create_many(
        self,
    ) -> list[ExerciseCategory]:
        records = []
        if self.seeded:
            return self.data

        self.category_seeder.create_many()
        self.session.commit()
        
        self.exercise_seeder.create_many()                
        self.session.commit()

        for exercise_category in exercises_by_categories.keys():
            exercise_list = exercises_by_categories[exercise_category]
            for exercise_name in exercise_list:
                exercise_id = exercise_name_to_id[exercise_name]
                category_id = exercise_category_to_id[exercise_category]
                item = self.create_exercise_category(category_id, exercise_id)
                if item is not None:
                    records.append(item)
                else:
                    print(f"Could not create exercise category for {exercise_name}")
                    continue

        self.session.commit()

        self.data = records
        self.seeded = True
        return records
