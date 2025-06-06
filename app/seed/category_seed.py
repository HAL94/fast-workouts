from app.models import Category
from app.seed.base_seed import BaseSeed
from app.seed.constants import exercise_categories


class CategorySeed(BaseSeed):
    __model__ = Category

    def create_exercise_category(self, name: str) -> Category | None:
        exercise_category = {"name": name}
        item = self.upsert_record(exercise_category, unique_fields=["name"])
        return item

    def create_many(
        self,
    ) -> list[Category]:
        records = []
        if self.seeded:
            return self.data

        for exercise_category in exercise_categories:
            item = self.create_exercise_category(exercise_category.get("name"))
            if item is not None:
                records.append(item)

        self.data = records
        self.seeded = True
        return records
