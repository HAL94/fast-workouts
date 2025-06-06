from typing import Optional

from app.models import User
from app.seed.base_seed import BaseSeed
from app.utils.create_hash_pw import create_hashed_pw


class UserSeed(BaseSeed):
    __model__ = User

    def _create_hashed_password(self, password: str) -> str:
        return create_hashed_pw(password)

    def create_user(self) -> dict:
        return {
            "full_name": self.faker.name(),
            "email": self.faker.email(),
            "age": self.faker.random_int(min=18, max=80),
            "hashed_password": self._create_hashed_password("123456"),
        }

    def create_many(self, size: Optional[int] = 5) -> list[User]:
        records = []
        for _ in range(size):
            user_record = self.upsert_record(
                self.create_user(), unique_fields=["email"]
            )
            if user_record is not None:
                records.append(user_record)
        self.data = records
        self.seeded = True
        return records
