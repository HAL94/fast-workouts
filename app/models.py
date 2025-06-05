from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database.base_model import Base


class User(Base):
    __tablename__ = "users"
    
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)


class ExerciseMuscleGroup(Base):
    __tablename__ = "exercise_muscle_groups"

    exercise_id: Mapped[int] = mapped_column(
        ForeignKey("exercises.id"), primary_key=True
    )
    muscle_group_id: Mapped[int] = mapped_column(
        ForeignKey("muscle_groups.id"), primary_key=True
    )
    is_primary_muscle: Mapped[bool] = mapped_column()
    # relationships
    exercise: Mapped["Exercise"] = relationship(
        back_populates="exercise_muscle_associations"
    )
    muscle_groups: Mapped["MuscleGroup"] = relationship(
        back_populates="exercise_muscle_associations"
    )


class ExerciseCategory(Base):
    """
    Defines categories for exercises (e.g., 'Strength', 'Cardio').
    """
    __tablename__ = "exercise_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True) # Explicitly define primary key
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False) # Added length and unique constraint

    # Bidirectional relationship with Exercise: one category has many exercises
    exercises: Mapped[list["Exercise"]] = relationship(
        back_populates="exercise_category",
        cascade="all, delete-orphan" # If a category is deleted, delete associated exercises (consider implications)
    )

    def __repr__(self) -> str:
        return f"<ExerciseCategory(id={self.id}, name='{self.name}')>"
    

class MuscleGroup(Base):
    __tablename__ = "muscle_groups"

    muscle_target: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    
    # relationships
    exercise_muscle_associations: Mapped[list["ExerciseMuscleGroup"]] = relationship(
        back_populates="muscle_groups", cascade="all, delete-orphan"
    )
    exercises: Mapped[list["Exercise"]] = relationship(
        secondary="exercise_muscle_groups",  # Specifies the association table
        back_populates="muscle_groups",  # Points to the 'muscle_groups' relationship on the Exercise model
        viewonly=True,  # Prevents SQLAlchemy from trying to write to the secondary table directly
    )


class Exercise(Base):
    __tablename__ = "exercises"

    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    is_custom: Mapped[bool] = mapped_column(default=False)
    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=True, default=None
    )

    # relationships
    exercise_category_id: Mapped[int] = mapped_column(ForeignKey("exercise_categories.id"))
    exercise_category: Mapped["ExerciseCategory"] = relationship(back_populates="exercises")
    
    exercise_muscle_associations: Mapped[list["ExerciseMuscleGroup"]] = relationship(
        back_populates="exercise"
    )
    muscle_groups: Mapped[list["MuscleGroup"]] = relationship(
        secondary="exercise_muscle_groups",  # Specifies the association table
        back_populates="exercises",  # Points to the 'exercises' relationship on the MuscleGroup model
        viewonly=True,  # Prevents SQLAlchemy from trying to write to the secondary table directly
    )
