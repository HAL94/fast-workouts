from datetime import datetime
from typing import override
from sqlalchemy import DateTime, inspect
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column("id", autoincrement=True, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now())

    def dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    @classmethod
    def relations(cls):
        return inspect(cls).relationships.items()

    @classmethod
    def columns(cls):
        return {_column.name for _column in inspect(cls).c}

    @classmethod
    def table(cls):
        return cls.__table__
    
    @override
    def __repr__(self) -> str:
        return str(self.dict())
