from typing import Any, Type, TypeVar
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import Session, sessionmaker
from app.seed.base_seed import BaseSeed
from app.seed.category_seed import CategorySeed
from app.seed.exercise_category_seed import ExerciseCategoryMapSeed
from app.seed.exercise_muscle_group_seed import ExerciseMuscleGroupSeed
from app.seed.exercise_seed import ExerciseSeed
from app.seed.muscle_group_seed import MuscleGroupSeed
from app.seed.user_seed import UserSeed
from app.core.config import settings
import inspect


DATABASE_URL = URL.create(
    drivername="postgresql",
    username=settings.PG_USER,
    password=settings.PG_PW,
    host=settings.PG_SERVER,
    database=settings.PG_DB,
    port=settings.PG_PORT,
)

engine = create_engine(url=DATABASE_URL)


def get_session(SessionLocal: sessionmaker[Session]):
    db = SessionLocal()
    try:
        yield db
    except Exception as e:        
        print(f"an error occured: {e}")
    


# constructs dependency graph
SEED_DI = {}

# constructs dependency resolver
DI_RESOLVER = {
    "Session": None,
}


def register_dependency(injection_cls: Type[Any]):
    class_name = injection_cls.__name__
    SEED_DI[class_name] = injection_cls

T = TypeVar("T", bound=BaseSeed)

def resolve_dependency(dependency_cls: Type[T]) -> T:
    dependencies = {}
    dependency_name = dependency_cls.__name__
    # print("Running for class", dependency_name)
    if dependency_name not in SEED_DI:
        raise ValueError(f"Dependency {dependency_name} not registered")
    if dependency_name in DI_RESOLVER:
        return DI_RESOLVER[dependency_name]

    for key, param in dependency_inspector(dependency_cls):
        if key == "self":
            continue
        if param.annotation is inspect.Parameter.empty:
            raise ValueError(
                f"Dependency {dependency_name} has a key {key} with empty annotation"
            )

        dep_name = param.annotation.__name__
        if dep_name not in SEED_DI:
            raise ValueError(f"Dependency {dep_name} not registered")

        resolved_dep = resolve_dependency(SEED_DI[dep_name])
        dependencies[key] = resolved_dep
        # print("keyis", key, "class_target", dependency_cls, dependencies)

    print(f"Resolved for: {dependency_name}", dependencies)
    constructed_cls = dependency_cls(**dependencies)
    DI_RESOLVER[dependency_name] = constructed_cls

    return constructed_cls


def dependency_inspector(cls: Type[Any]):
    class_args_items = inspect.signature(cls.__init__).parameters.items()
    return class_args_items


def main():
    session: Session = next(get_session(sessionmaker(bind=engine)))
    
    DI_RESOLVER["Session"] = session

    register_dependency(Session)
    register_dependency(CategorySeed)
    register_dependency(ExerciseSeed)
    register_dependency(ExerciseCategoryMapSeed)
    register_dependency(MuscleGroupSeed)
    register_dependency(ExerciseMuscleGroupSeed)
    register_dependency(UserSeed)
    
    user_seed = resolve_dependency(UserSeed)
    exercise_muscle_group_seeder = resolve_dependency(ExerciseMuscleGroupSeed)
    exercise_category_seeder = resolve_dependency(ExerciseCategoryMapSeed)
    
    user_seed.create_many()
    exercise_category_seeder.create_many()
    exercise_muscle_group_seeder.create_many()

    print("Done!")


if __name__ == "__main__":
    main()
