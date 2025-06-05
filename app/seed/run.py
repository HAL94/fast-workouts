from sqlalchemy import URL, create_engine
from sqlalchemy.orm import Session, sessionmaker
from app.seed.exercise_category_seed import ExerciseCategorySeed
from app.seed.exercise_muscle_group_seed import ExerciseMuscleGroupSeed
from app.seed.exercise_seed import ExerciseSeed
from app.seed.muscle_group_seed import MuscleGroupSeed
from app.seed.user_seed import UserSeed
from app.core.config import settings

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
        db.rollback()
        print(f"an error occured: {e}")
    finally:
        db.close()


def main():
    session: Session = next(get_session(sessionmaker(bind=engine)))

    user_seed = UserSeed(session=session)
    muscle_group_seed = MuscleGroupSeed(session=session)
    exercise_category_seed = ExerciseCategorySeed(session=session)
    
    exercise_seed = ExerciseSeed(
        session=session, category_seeder=exercise_category_seed
    )
    exercise_muscle_group_seed = ExerciseMuscleGroupSeed(
        session=session,
        exercise_seeder=exercise_seed,
        muscle_group_seeder=muscle_group_seed,
    )

    user_seed.create_many()
    exercise_muscle_group_seed.create_many()    

    print("Done!")


if __name__ == "__main__":
    main()
