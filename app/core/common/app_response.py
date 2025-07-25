from typing import Generic, Optional, TypeVar, Self
from pydantic import AliasGenerator, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from app.core.database.base_model import Base

T = TypeVar("T")


class AppBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(to_camel), populate_by_name=True
    )

    def model_dump(self, **kwargs):
        if "by_alias" not in kwargs:
            kwargs["by_alias"] = True

        return super().model_dump(**kwargs)

    @classmethod
    def to_entity(cls, schema: Self) -> Base:
        print(f"Checking schema: {schema.__class__.__name__}")
        
        if not cls.Meta.orm_model:
            print("No ORM model configed in Meta")
            return None

        parsed = dict(schema)

        entity = cls.Meta.orm_model()

        for key, value in parsed.items():
            if isinstance(value, list) and len(value):
                if isinstance(value[0], BaseModel):
                    setattr(entity, key, [schema.to_entity(schema) for schema in value])
                else:
                    setattr(entity, key, [inner for inner in value])
            elif isinstance(value, BaseModel):
                setattr(entity, key, value.to_entity(value))
            else:
                setattr(entity, key, value)

        return entity


class AppResponse(AppBaseModel, Generic[T]):
    success: bool = Field(description="Is operation success", default=True)
    status_code: int = Field(description="status code", default=200)
    internal_code: Optional[int] = Field(description="Internal code", default=None)
    message: str = Field(description="Message back to client", default="done")
    data: Optional[T] = None
