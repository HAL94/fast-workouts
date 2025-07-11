from typing import Any, ClassVar, Generic, Optional, TypeVar

from sqlalchemy.orm.strategy_options import _AbstractLoad
from pydantic import BaseModel
from sqlalchemy import func, delete, insert, select, update
from sqlalchemy.exc import IntegrityError, ProgrammingError
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.sql.elements import ColumnElement

from app.core.common.app_response import AppBaseModel

from .base_model import Base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import InstrumentedAttribute

from app.core.exceptions import AlreadyExistException, NotFoundException

DbModel = TypeVar("T", bound=Base)  # type: ignore
PydanticModel = TypeVar("M", bound=BaseModel)


class PaginatedResponse(AppBaseModel, Generic[PydanticModel]):
    result: list[PydanticModel]
    total_count: int
    page: int
    size: int


class BaseRepo(Generic[DbModel, PydanticModel]):
    __dbmodel__: ClassVar[DbModel]
    __model__: ClassVar[PydanticModel]

    def __init__(self, session: AsyncSession):
        self.session = session

    @property
    def _model(self) -> PydanticModel:
        return self.__model__

    @property
    def _dbmodel(self) -> DbModel:
        return self.__dbmodel__

    async def create(
        self, data: BaseModel, return_model: Optional[BaseModel | PydanticModel] = None, commit: bool = True
    ) -> PydanticModel:
        """
        Accepts a Pydantic model as data, creates a new record in the database, and returns the record as pydantic model.

        Args:
            data (BaseModel): Pydantic model

        Returns:
            result as PydanticModel
        """
        session = self.session
        created_db_model = await session.scalar(
            insert(self._dbmodel)
            .values(data.model_dump(exclude_none=True, exclude_unset=True, by_alias=False))
            .returning(self._dbmodel)
        )
        if commit:
            await session.commit()

        if not return_model:
            return_model = self._model

        return return_model(**created_db_model.dict())

    async def create_many(
        self,
        data: list[BaseModel],
        return_model: Optional[BaseModel | PydanticModel] = None,
        batch_size: int = 1000,
        commit: bool = True,
    ) -> list[PydanticModel]:
        """
        Create multiple records in the database.

        Args:
            data: List of Pydantic models to create
            return_model: Optional model class for return type
            batch_size: Number of records to insert per batch (default: 1000)

        Returns:
            List of created records as Pydantic models

        Raises:
            DuplicateEntryError: If any record violates unique constraints
            ValueError: If data list is empty

        Example:
            users_data = [
                UserCreate(name="John", email="john@example.com"),
                UserCreate(name="Jane", email="jane@example.com"),
                UserCreate(name="Bob", email="bob@example.com")
            ]
            created_users = await user_repo.create_many(users_data)
        """
        if not data:
            raise ValueError("Data list cannot be empty")

        session = self.session
        return_model = return_model or self._model
        all_created_records = []

        try:
            # Process in batches to avoid memory issues with large datasets
            for i in range(0, len(data), batch_size):
                batch = data[i: i + batch_size]
                batch_values = [item.model_dump(
                    exclude_none=True, by_alias=False) for item in batch]

                # Use bulk insert with RETURNING to get created records
                created_records = await session.scalars(
                    insert(self._dbmodel).values(
                        batch_values).returning(self._dbmodel)
                )

                # Convert to list and extend main results
                batch_results = created_records.all()
                all_created_records.extend(batch_results)

            if commit:
                await session.commit()

            return [return_model(**record.dict()) for record in all_created_records]

        except IntegrityError as e:
            await session.rollback()
            raise AlreadyExistException(
                f"One or more records violate unique constraints: {str(e)}"
            ) from e

    async def upsert_one(
        self,
        data: BaseModel,
        index_elements: list[str] | None = None,
        return_model: Optional[BaseModel | PydanticModel] = None,
    ) -> PydanticModel:
        """
        Insert a single record or update it if it already exists (upsert).

        Args:
            data: Pydantic model containing the data to upsert
            index_elements: List of column names to use for conflict detection.
                        Defaults to ['id'] if not provided.
            return_model: Optional model class for return type

        Returns:
            The created or updated record as a Pydantic model

        Example:
            # Basic upsert using default 'id' field
            user_data = UserModel(id=1, name="John Updated", email="john@example.com")
            user = await user_repo.upsert_one(user_data)

            # Upsert using email as unique identifier
            user_data = UserModel(name="Jane", email="jane@example.com", role="admin")
            user = await user_repo.upsert_one(
                data=user_data,
                index_elements=["email"]
            )

            # Upsert using composite key
            setting_data = SettingModel(user_id=1, key="theme", value="dark")
            setting = await user_repo.upsert_one(
                data=setting_data,
                index_elements=["user_id", "key"]
            )
        """
        if not index_elements:
            index_elements = ["id"]

        session = self.session
        data_dict = data.model_dump(exclude_none=True, by_alias=False)

        # Validate that all index elements exist in the data
        data_keys = set(data_dict.keys())
        index_keys = set(index_elements)
        missing_keys = index_keys - data_keys

        if missing_keys:
            raise ValueError(
                f"Data must include all index elements. Missing: {missing_keys}"
            )

        # Check if all data keys are index elements (would make update impossible)
        if len(data_keys - index_keys) == 0:
            raise ValueError(
                "Index elements match all data fields, upsert is invalid.")

        try:
            # Use PostgreSQL's INSERT ... ON CONFLICT DO UPDATE
            stmt = pg_insert(self._dbmodel).values(data_dict)

            # Build the update clause - update all fields except index elements
            updated_columns = {
                key: getattr(stmt.excluded, key)
                for key in data_dict.keys()
                if key not in index_elements
            }

            # Add updated_at timestamp if column exists
            if "updated_at" in self._dbmodel.columns():
                updated_columns["updated_at"] = func.now()

            stmt = stmt.on_conflict_do_update(
                index_elements=index_elements, set_=updated_columns
            )

            # Execute and get the result
            result = await session.scalar(stmt.returning(self._dbmodel))

            await session.commit()

            return_model = return_model or self._model
            return return_model(**result.dict())

        except Exception as e:
            await session.rollback()
            raise ValueError(f"Upsert operation failed: {str(e)}") from e

    async def upsert_many(
        self,
        data: list[BaseModel],
        index_elements: list[InstrumentedAttribute | str] | None = None,
        return_model: Optional[list[BaseModel | PydanticModel]] = None,
    ):
        """
        Performs a bulk upsert operation on the database table.

        This function inserts or updates multiple rows in the database based on the provided data.
        If a row with the specified index elements already exists, it updates the row; otherwise, it inserts a new row.

        Args:
            data: A list of BaseModel instances representing the data to be upserted.
            index_elements: A list of InstrumentedAttribute or string column names used to determine conflicts.
                            Defaults to the primary key 'id' if not provided.
            return_model: An optional BaseModel instance to use for returning the results.
                        Defaults to the model associated with the repository if not provided.

        Returns:
            A list of PydanticModel instances representing the upserted or updated rows.

        Example:
            >>> await repository.upsert_many(
            ...     data=[MyModel(id=1, name='Updated Name'), MyModel(id=2, name='New Name')],
            ...     index_elements=['id'],
            ...     return_model=MyPydanticModel
            ... )
            [MyPydanticModel(...), MyPydanticModel(...)]
        """
        try:
            if not index_elements:
                index_elements = [self._dbmodel.id]

            index_elements = [
                col.name if isinstance(
                    col, InstrumentedAttribute) else str(col)
                for col in index_elements
            ]

            model_columns = self._dbmodel.columns()

            session = self.session

            data_values = [item.model_dump(
                exclude_none=True, by_alias=False) for item in data]
            data_model_fields = data[0].model_fields

            data_keys = set(data_model_fields.keys())
            index_keys = set(index_elements)

            # if all keys in data match with index_elements, then the operation is invalid
            # because there are not distinctions that could be used for the on conflict clause.
            if len(data_keys - index_keys) == 0:
                raise ValueError(
                    "Index elements match all model fields, upsert is invalid."
                )

            #  if no key in index_elements exists in data, then the operation is invalid
            missing_keys = index_keys - data_keys
            if missing_keys:
                raise ValueError(
                    f"Data passed must include the indexed_elements to handle conflicts. Missing: {missing_keys}"
                )

            stmt = pg_insert(self._dbmodel).values(data_values)

            updated_columns = {
                key: getattr(stmt.excluded, key)
                # Use the first data object's keys
                for key in data_values[0].keys()
                if key not in index_elements  # Ensure index elements are not updated
            }

            if "updated_at" in model_columns:
                updated_columns["updated_at"] = func.now()

            stmt = stmt.on_conflict_do_update(
                index_elements=index_elements, set_=updated_columns
            )

            updated_or_created_data = await session.scalars(
                stmt.returning(self._dbmodel),
                execution_options={"populate_existing": True},
            )

            await session.commit()

            return_model = return_model or self._model

            result = updated_or_created_data.all()

            return [return_model(**item.dict()) for item in result]
        except ProgrammingError:
            raise ValueError(
                "there is no unique or exclusion constraint matching the ON CONFLICT specification. Background on this error at: https://sqlalche.me/e/20/f405)"
            )

    async def get_one(
        self,
        val: Any,
        field: InstrumentedAttribute | str | None = None,
        where_clause: list[ColumnElement[bool]] = None,
        options: list[_AbstractLoad] = None,
        return_model: Optional[BaseModel | PydanticModel] = None,
    ) -> PydanticModel:
        """
        Retrieves a single record from the database matching the given criteria.

        Args:
            val: The value to search for.
            field: The InstrumentedAttribute representing the column to search in. Defaults to the model's primary key.
            where_clause: An optional list of additional SQLAlchemy where clauses to apply.
            return_model: An optional BaseModel or PydanticModel to use for returning the result. Defaults to the repository's model.

        Returns:
            A PydanticModel instance representing the found record.

        Raises:
            NotFoundException: If no matching record is found.
        """
        session = self.session

        if field is None:
            field = self._dbmodel.id

        if isinstance(field, InstrumentedAttribute):
            where_cond: list = [field == val]
        else:
            where_cond: list = [getattr(self._dbmodel, field) == val]

        if where_clause:
            where_cond.extend(where_clause)

        stmt = select(self._dbmodel).where(*where_cond)

        if options:
            stmt = stmt.options(*options)

        result = await session.scalar(stmt)

        if result is None:
            raise NotFoundException

        return_model = return_model or self._model

        if options:
            return return_model.model_validate(result, from_attributes=True)
        else:
            return return_model(**result.dict())

        # return return_model(**result.dict())
    async def get_all(self,
                      where_clause: list[ColumnElement[bool]] = [],
                      order_clause: list[InstrumentedAttribute] = [],
                      options: list[_AbstractLoad] = None,
                      return_model: Optional[BaseModel | PydanticModel] = None,
                      ):
        session = self.session

        stmt = select(self._dbmodel)
        
        stmt = stmt.where(*where_clause).order_by(*order_clause)

        if options:
            stmt = stmt.options(*options)

        result = await session.scalars(stmt)

        return_model = return_model or self._model

        if options:
            item_list = [return_model.model_validate(
                item, from_attributes=True) for item in result.all()]
        else:
            item_list = [return_model(**item.dict()) for item in result.all()]

        return item_list

    async def get_many(
        self,
        page: int,
        size: int,
        where_clause: list[ColumnElement[bool]] = [],
        order_clause: list[InstrumentedAttribute] = [],
        relations: list[_AbstractLoad] = None,
        return_model: Optional[BaseModel | PydanticModel] = None,
    ) -> PaginatedResponse[PydanticModel]:
        session = self.session

        stmt = (
            select(self._dbmodel)
            .where(*where_clause)
            .order_by(*order_clause)
            .offset((page - 1) * size)
            .limit(size)
        )

        if relations:
            options = relations
            stmt = stmt.options(*options)

        result = await session.scalars(stmt)

        total_count = await session.scalar(
            select(func.count()).select_from(
                select(self._dbmodel).where(*where_clause).subquery()
            )
        )

        # print(f"total_count: {total_count}")

        return_model = return_model or self._model

        if relations:
            item_list = [return_model.model_validate(
                item, from_attributes=True) for item in result.all()]
        else:
            item_list = [return_model(**item.dict()) for item in result.all()]

        PaginatedResponse.__model__ = return_model
        return PaginatedResponse[PydanticModel](
            result=item_list,
            total_count=total_count,
            page=page,
            size=size,
        )

    async def delete_one(
        self,
        val: Any,
        field: InstrumentedAttribute | None = None,
        where_clause: list[ColumnElement[bool]] = None,
        return_model: Optional[BaseModel | PydanticModel] = None,
    ) -> PydanticModel:
        """
        Deletes a single record from the database matching the given criteria.

        Args:
            val: The value to search for.
            field: The InstrumentedAttribute representing the column to search in. Defaults to the model's primary key.
            where_clause: An optional list of additional SQLAlchemy where clauses to apply.
            return_model: An optional BaseModel or PydanticModel to use for returning the deleted record. Defaults to the repository's model.

        Returns:
            A PydanticModel instance representing the deleted record.

        Raises:
            NotFoundException: If no matching record is found.
        """

        session = self.session

        if field is None:
            field = self._dbmodel.id

        if isinstance(field, InstrumentedAttribute):
            where_cond: list = [field == val]
        else:
            where_cond: list = [getattr(self._dbmodel, field) == val]

        if where_clause:
            where_cond.extend(where_clause)

        deleted_db_model = await session.scalar(
            delete(self._dbmodel).filter(*where_cond).returning(self._dbmodel)
        )

        await session.commit()

        if not deleted_db_model:
            raise NotFoundException

        if not return_model:
            return_model = self._model

        return return_model(**deleted_db_model.dict())

    async def delete_many(
        self,
        where_clause: list[ColumnElement[bool]],
        return_model: Optional[BaseModel | PydanticModel] = None,
    ):
        """
        Deletes multiple records from the database matching the given criteria.

        Args:
            where_clause: A list of SQLAlchemy where clauses to identify the records to delete.
            return_model: An optional BaseModel or PydanticModel to use for returning the deleted records. Defaults to the repository's model.

        Returns:
            A list of PydanticModel instances representing the deleted records.

        Raises:
            ValueError: If no where_clause is provided.
        """
        session = self.session

        if not where_clause:
            raise ValueError("'where_cluse' must be passed")

        deleted_model_records = await session.scalars(
            delete(self._dbmodel).where(*where_clause).returning(self._dbmodel)
        )

        await session.commit()

        result = deleted_model_records.all()

        print(f"deleted_records: {result} at where_clause: {where_clause}")

        if not return_model:
            return_model = self._model

        return [return_model(**item.dict()) for item in result]

    async def update_one(
        self,
        data: BaseModel,
        where_clause: list[ColumnElement[bool]] = None,
        return_model: Optional[BaseModel | PydanticModel] = None,
        commit: bool = True,
    ) -> PydanticModel:
        """
        Updates a single record in the database matching the given criteria.

        Args:
            data: A BaseModel instance containing the updated data.
            where_clause: A list of SQLAlchemy where clauses to identify the record to update.
            return_model: An optional BaseModel or PydanticModel to use for returning the result. Defaults to the repository's model.

        Returns:
            A PydanticModel instance representing the updated record.
        """
        session = self.session

        if not where_clause:
            raise ValueError("must pass where_clause")

        updated_db_model = await session.scalar(
            update(self._dbmodel)
            .values(data.model_dump(exclude_none=True, by_alias=False))
            .filter(*where_clause)
            .returning(self._dbmodel)
        )

        if commit:
            await session.commit()

        if updated_db_model is None:
            raise NotFoundException

        if not return_model:
            return_model = self._model

        return return_model(**updated_db_model.dict())

    async def update_many(
        self,
        data: list[BaseModel],
        field: Any = "id",
        return_model: Optional[BaseModel | PydanticModel] = None,
        commit: bool = True
    ) -> list[PydanticModel]:
        """
        We expect that data is a list of dictionaries, where each dictionary element will have a field acting (ideally) as primary key, or at least it should be unique. This field should be passed to the `field` argument in this function.


        Example usage:
            session.execute(
            ...     update(User),
            ...     [
            ...         {"id": 1, "fullname": "Spongebob Squarepants"},
            ...         {"id": 3, "fullname": "Patrick Star"},
            ...         {"id": 5, "fullname": "Eugene H. Krabs"},
            ...     ],
            ... )
        """
        if any(field not in item.model_fields for item in data):
            raise ValueError(
                f"Model is invalid: item in 'data' must contain an '{field}' key."
            )

        if any(
            field not in item.model_dump(exclude_unset=True, by_alias=False).keys() for item in data
        ):
            raise ValueError(
                f"Your passed data sequence contains items that are missing the field: {field}"
            )

        session: AsyncSession = self.session

        update_values = [item.model_dump(
            exclude_none=True, by_alias=False) for item in data]

        # unlike a single record update, a bulk update does not support RETURNING
        # it is best to update with `executemany` which receives a parameter sets
        await session.execute(update(self._dbmodel), update_values)
        
        if commit:
            await session.commit()

        field_values = [item.get(field) for item in update_values]

        where_clause = getattr(self._dbmodel, field).in_(field_values)

        result = await session.scalars(select(self._dbmodel).where(where_clause))

        return_model = return_model or self._model

        return [return_model(**item.dict()) for item in result.all()]
