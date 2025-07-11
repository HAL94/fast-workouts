

from app.api.v1.schema.category import CategoryBase
from app.core.database.base_repo import BaseRepo
from app.models import Category


class CategoryRepository(BaseRepo[Category, CategoryBase]):
    __dbmodel__ = Category
    __model__ = CategoryBase
