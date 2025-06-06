import abc
from typing import Any, ClassVar, Generic, TypeVar
from sqlalchemy.dialects.postgresql import insert as pg_insert

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from ..core.database.base_model import Base
from faker import Faker

T = TypeVar("T", bound=Base)

class BaseSeed(abc.ABC, Generic[T]):
    __model__: ClassVar[T]

    @property
    def model(self) -> T:
        return self.__model__

    def __init__(self, session: Session):
        self.session = session
        self.faker = Faker()
        self.data: list[T] = []
        self.seeded = False

    def upsert_record(
        self,
        data: dict[str, Any],
        unique_fields: list[str] = ["id"],
    ) -> T:
        """
        Creates or updates a record in the database
        """
        try:
            if getattr(self.model, unique_fields[0]) is None:
                raise ValueError("Unique field is not valid")


            stmt = pg_insert(self.model).values(**data)

            stmt = stmt.on_conflict_do_nothing(
                index_elements=[*unique_fields],
            ).returning(self.model)

            created_record = self.session.scalar(stmt)
            
            if not created_record:
                print(f"Data already exists: {data}")
                return self.session.scalar(
                    self.session.query(self.model).filter_by(**data)
                )
            print(f"Inserted data: {data}")


            return created_record
        except SQLAlchemyError:
            self.session.rollback()
            return None
        
    @abc.abstractmethod
    def create_many(self, *args, **kwargs) -> list[T]:
        """
        Creates multiple records in the database
        """
        raise NotImplementedError()
