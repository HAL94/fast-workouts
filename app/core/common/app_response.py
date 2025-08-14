from typing import Generic, Optional, TypeVar, Self, Type
from pydantic import AliasGenerator, BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from app.core.database.base_model import Base
from sqlalchemy import inspect
from fastapi import HTTPException

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
    def update_entity(cls, schema: Self, entity: Base) -> Base:
        print(f"Checking schema: {schema.__class__.__name__}")
        if not cls.Meta.orm_model:
            print("No ORM model configed in Meta")
            raise ValueError(
                f"No ORM model configured for this pydantic class: {cls.__name__}"
            )

        dumped = dict(schema)

        if "id" not in dumped.keys():
            raise ValueError("Id is required for an update")

        def get_subentity_parent_fk_name(
            subentity_model: Type[Base], parent_model: Type[Base]
        ) -> Optional[str]:
            # print(f"subentity_model: {subentity_model}")
            for _, relationship in inspect(subentity_model).relationships.items():
                # print(
                #     f"Relations for entity: {relationship.entity.class_} {parent_model.__class__}"
                # )
                if relationship.entity.class_ is parent_model.__class__:
                    # print("Here it is matched!!")
                    # Found the relationship, get the local foreign key column name
                    fk_column = relationship.local_remote_pairs[0][0]
                    fk_name = fk_column.name
                    # print(f"fk_name: {fk_name}")
                    return fk_name
            return None

        for key, value in dumped.items():
            # print(f"Checking key, value for: {key} - {value}")
            if isinstance(value, list) and len(value) > 0:
                if isinstance(value[0], BaseModel):
                    # print(f"list found, key is: {key}")
                    # subentity = None
                    if value is not None and value[0].Meta.orm_model is not None:
                        # print(f"accessing submodel key: {key}")
                        # subentity = getattr(entity, key)
                        # print(f"Got subentity: {subentity}")
                        # set_subentity_parent_id_name(subentity=subentity[0])

                        parent_relation_attr: list[Base] = getattr(entity, key)
                        existing_children_by_id = {
                            child.id: child for child in parent_relation_attr
                        }
                        for schema in value:
                            child_entity = existing_children_by_id.get(schema.id)
                            if not child_entity:
                                raise HTTPException(
                                    status_code=400,
                                    detail=f"Integrity Error: passed an unknown id to relation: {schema.id}",
                                )

                            fk_name = get_subentity_parent_fk_name(
                                subentity_model=schema.Meta.orm_model,
                                parent_model=entity,
                            )

                            if fk_name:
                                setattr(child_entity, fk_name, entity.id)
                                setattr(schema, fk_name, entity.id)
                                schema.update_entity(schema=schema, entity=child_entity)

            elif isinstance(value, AppBaseModel) and value.Meta.orm_model:
                setattr(
                    entity, key, value.update_entity(value, entity=getattr(entity, key))
                )

            elif (
                hasattr(entity, key)
                and value is not None
                and value != getattr(entity, key)
            ):
                setattr(entity, key, value)

        return entity

    @classmethod
    def create_entity(cls, schema: Self) -> Base:
        print(f"Checking schema: {schema.__class__.__name__}")

        if not cls.Meta.orm_model:
            raise ValueError(
                f"No ORM model configed in Meta for schema: {schema.__class__.__name__}"
            )

        parsed = dict(schema)

        entity = cls.Meta.orm_model()

        for key, value in parsed.items():
            if isinstance(value, list) and len(value):
                if isinstance(value[0], AppBaseModel):
                    setattr(
                        entity, key, [schema.create_entity(schema) for schema in value]
                    )
                else:
                    setattr(entity, key, [inner for inner in value])
            elif isinstance(value, AppBaseModel):
                setattr(entity, key, value.create_entity(value))
            elif value is not None:
                setattr(entity, key, value)

        return entity


class AppResponse(AppBaseModel, Generic[T]):
    success: bool = Field(description="Is operation success", default=True)
    status_code: int = Field(description="status code", default=200)
    internal_code: Optional[int] = Field(description="Internal code", default=None)
    message: str = Field(description="Message back to client", default="done")
    data: Optional[T] = None
