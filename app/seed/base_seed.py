import abc
from typing import Any, ClassVar, Generic, Optional, TypeVar
from sqlalchemy.dialects.postgresql import insert as pg_insert

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

    def upsert_record(
        self, data: dict[str, Any], unique_field: str = "id"
    ) -> T:
        """
        Creates or updates a record in the database
        """
        
        if getattr(self.model, unique_field) is None:
            raise ValueError("Unique field is not valid")
            
        
        print(f"Received data: {data}")
        
        stmt = pg_insert(self.model).values(**data)

        stmt = stmt.on_conflict_do_nothing(
            index_elements=[getattr(self.model, unique_field)],
        ).returning(self.model)

        created_record = self.session.scalar(stmt)
        
        if not created_record:
            return self.session.scalar(
                self.session.query(self.model).filter_by(**data)
            )

        self.session.commit()

        return created_record

    @abc.abstractmethod
    def create_many(self, size: Optional[int] = 5, *args, **kwargs) -> list[T]:
        """
        Creates multiple records in the database
        """
        raise NotImplementedError()
