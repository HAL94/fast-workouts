from typing import Type, Optional, Any
from pydantic import BaseModel, create_model


def create_renamed_model(
    base_model: Type[BaseModel],
    rename_mapping: dict[str, str],
    exclude: Optional[list[str]] = [],
) -> Type[BaseModel]:
    """
    Creates a new Pydantic model with fields renamed according to the provided mapping.

    Args:
        base_model: The Pydantic model to use as a base.
        rename_mapping: A dictionary where keys are original field names and values are
                        the new desired field names.

    Returns:
        A new Pydantic model class with the fields renamed.
    """
    new_fields: dict[str, tuple[Any, Any]] = {}
    for old_name, field_info in base_model.model_fields.items():
        if old_name in exclude:
            continue

        new_name = rename_mapping.get(old_name, old_name)
        new_fields[new_name] = (field_info.annotation, field_info.default)

    # Use pydantic.create_model to generate the new class
    renamed_model = create_model(
        f"{base_model.__name__}Renamed", **new_fields, __base__=BaseModel
    )
    return renamed_model
