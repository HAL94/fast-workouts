from datetime import datetime
import enum
from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database.base_model import Base


class WorkoutSessionStatus(str, enum.Enum):
    """
    Status of a workout session (e.g., 'scheduled', 'in_progress', 'completed', 'cancelled').
    """

    scheduled = "scheduled"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"

class User(Base):
    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    # relationships
    workout_plans: Mapped[list["WorkoutPlan"]] = relationship(back_populates="user")
    workout_plan_sessions: Mapped[list["WorkoutSession"]] = relationship(
        back_populates="user"
    )
    workout_plan_schedules: Mapped[list["WorkoutPlanSchedule"]] = relationship(
        back_populates="user"
    )

class ExerciseMuscleGroup(Base):
    __tablename__ = "exercise_muscle_groups"

    exercise_id: Mapped[int] = mapped_column(
        ForeignKey("exercises.id"), primary_key=True
    )
    muscle_group_id: Mapped[int] = mapped_column(
        ForeignKey("muscle_groups.id"), primary_key=True
    )

    __table_args__ = (
        UniqueConstraint(
            "exercise_id", "muscle_group_id", name="unique_exercise_muscle_group"
        ),
    )

    is_primary_muscle: Mapped[bool] = mapped_column(nullable=False)

    # relationships
    exercise: Mapped["Exercise"] = relationship(
        back_populates="exercise_muscle_associations"
    )
    muscle_groups: Mapped["MuscleGroup"] = relationship(
        back_populates="exercise_muscle_associations"
    )

class ExerciseCategory(Base):
    __tablename__ = "exercise_categories"

    # relationships
    exercise_id: Mapped[int] = mapped_column(
        ForeignKey("exercises.id"), primary_key=True
    )
    exercise: Mapped["Exercise"] = relationship(
        back_populates="exercise_category_association"
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), primary_key=True
    )
    category: Mapped["Category"] = relationship(
        back_populates="exercise_category_association"
    )

    __table_args__ = (
        UniqueConstraint("exercise_id", "category_id", name="unique_exercise_category"),
    )

class Category(Base):
    """
    Defines categories for exercises (e.g., 'Strength', 'Cardio').
    """

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )  # Explicitly define primary key
    name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )  # Added length and unique constraint

    # relationships
    exercise_category_association: Mapped[list["ExerciseCategory"]] = relationship(
        back_populates="category"
    )
    exercises: Mapped[list["Exercise"]] = relationship(
        secondary="exercise_categories",
        back_populates="categories",
        viewonly=True,
    )

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name='{self.name}')>"

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

    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    is_custom: Mapped[bool] = mapped_column(default=False)
    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=True, default=None
    )

    # relationships
    exercise_muscle_associations: Mapped[list["ExerciseMuscleGroup"]] = relationship(
        back_populates="exercise"
    )
    exercise_category_association: Mapped[list["ExerciseCategory"]] = relationship(
        back_populates="exercise"
    )
    muscle_groups: Mapped[list["MuscleGroup"]] = relationship(
        secondary="exercise_muscle_groups",  # Specifies the association table
        back_populates="exercises",  # Points to the 'exercises' relationship on the MuscleGroup model
        viewonly=True,  # Prevents SQLAlchemy from trying to write to the secondary table directly
    )
    categories: Mapped[list["Category"]] = relationship(
        secondary="exercise_categories",  # Specifies the association table
        back_populates="exercises",  # Points to the 'exercises' relationship on the Category model
        viewonly=True,  # Prevents SQLAlchemy from trying to write to the secondary table directly
    )
    workout_exercise_plans: Mapped[list["WorkoutExercisePlan"]] = relationship(
        back_populates="exercise"
    )

class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    comments: Mapped[str] = mapped_column(String(500), nullable=True)

    # relationships
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="workout_plans")

    workout_plan_schedules: Mapped[list["WorkoutPlanSchedule"]] = relationship(
        back_populates="workout_plan",
        cascade="all, delete-orphan",
    )

    workout_plan_sessions: Mapped[list["WorkoutSession"]] = relationship(
        back_populates="workout_plan"
    )

    workout_exercise_plans: Mapped[list["WorkoutExercisePlan"]] = relationship(
        back_populates="workout_plan", cascade="all, delete-orphan", lazy="selectin"
    )

class WorkoutPlanSchedule(Base):
    __tablename__ = "workout_plan_schedules"

    start_at: Mapped[datetime] = mapped_column(nullable=False, index=True)
    end_time: Mapped[datetime] = mapped_column(nullable=True, index=True)
    remind_before_minutes: Mapped[int] = mapped_column(nullable=True)

    # relationships
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="workout_plan_schedules")

    workout_plan_id: Mapped[int] = mapped_column(
        ForeignKey("workout_plans.id", ondelete="CASCADE")
    )
    workout_plan: Mapped["WorkoutPlan"] = relationship(
        back_populates="workout_plan_schedules"
    )

class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    title: Mapped[str] = mapped_column(String(100), nullable=True)
    started_at: Mapped[datetime] = mapped_column(nullable=True)
    ended_at: Mapped[datetime] = mapped_column(nullable=True)
    duration_minutes: Mapped[int] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=True)
    session_comments: Mapped[str] = mapped_column(String(500), nullable=True)

    # relationships
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="workout_plan_sessions")

    workout_plan_id: Mapped["WorkoutPlan"] = mapped_column(
        ForeignKey("workout_plans.id", ondelete="SET NULL"), nullable=True
    )
    workout_plan: Mapped["WorkoutPlan"] = relationship(
        back_populates="workout_plan_sessions"
    )

    schedule_id: Mapped[int] = mapped_column(
        ForeignKey("workout_plan_schedules.id"), nullable=True
    )
    workout_session_results: Mapped[list["WorkoutSessionExerciseResult"]] = relationship(
        back_populates="workout_session"
    )

class WorkoutExercisePlan(Base):
    """
    Describes an exercise plan for a specific workout plan. It also acts as a parent of `workout_exercise_set_plans` list.
    """
    __tablename__ = "workout_exercise_plans"

    order_in_plan: Mapped[int] = mapped_column(nullable=False)
    target_sets: Mapped[int] = mapped_column(nullable=False)
    target_duration_minutes: Mapped[float] = mapped_column(nullable=True)
    notes: Mapped[str] = mapped_column(String(500), nullable=True)

    # relationships
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"))
    exercise: Mapped["Exercise"] = relationship(back_populates="workout_exercise_plans")

    workout_plan_id: Mapped[int] = mapped_column(
        ForeignKey("workout_plans.id", ondelete="CASCADE")
    )
    workout_plan: Mapped["WorkoutPlan"] = relationship(
        back_populates="workout_exercise_plans"
    )
    
    workout_exercise_set_plans: Mapped[list["WorkoutExerciseSetPlan"]] = relationship(
        back_populates="workout_exercise_plan", cascade="all, delete-orphan", lazy="selectin" 
    )
    
    workout_exercise_results: Mapped[list["WorkoutSessionExerciseResult"]] = relationship(
        back_populates="workout_exercise_plan"
    )

    __table_args__ = (
        UniqueConstraint("exercise_id", "workout_plan_id", name="unique_exercise_plan"),
    )

class WorkoutExerciseSetPlan(Base):
    """
    Describes an exercise set plan for a specific exercise plan. It also acts as a parent of `workout_session_exercise_set_results` list.
    """
    __tablename__ = "workout_exercise_set_plans"

    set_number: Mapped[int] = mapped_column(nullable=False)
    target_reps: Mapped[int] = mapped_column(nullable=False)
    target_weight: Mapped[float] = mapped_column(nullable=False)
    target_duration_seconds: Mapped[int] = mapped_column(nullable=True)
    
    workout_exercise_plan_id: Mapped[int] = mapped_column(
        ForeignKey("workout_exercise_plans.id", ondelete="CASCADE")
    )
    workout_exercise_plan: Mapped["WorkoutExercisePlan"] = relationship(
        back_populates="workout_exercise_set_plans"
    )
    
    workout_session_exercise_set_results: Mapped[list["WorkoutSessionExerciseSetResult"]] = relationship(
        back_populates="workout_exercise_set_plan"
    )

class WorkoutSessionExerciseResult(Base):
    """ 
        Describes an exercise results for a specific session for a given exercise plan. 
    """
    __tablename__ = "workout_session_exercise_results"

    sets_achieved: Mapped[int] = mapped_column(nullable=False)
    duration_minutes_achieved: Mapped[float] = mapped_column(nullable=True)

    # relationships
    workout_exercise_plan_id: Mapped[int] = mapped_column(
        ForeignKey("workout_exercise_plans.id", ondelete="SET NULL"), nullable=True
    )
    workout_exercise_plan: Mapped["WorkoutExercisePlan"] = relationship(
        back_populates="workout_exercise_results"
    )
    workout_session_exercise_set_results: Mapped[
        list["WorkoutSessionExerciseSetResult"]
    ] = relationship(back_populates="workout_session_exercise_result")
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"))   

    workout_session_id: Mapped[int] = mapped_column(ForeignKey("workout_sessions.id"))
    workout_session: Mapped["WorkoutSession"] = relationship(
        back_populates="workout_session_results"
    )

class WorkoutSessionExerciseSetResult(Base):
    __tablename__ = "workout_session_exercise_set_results"

    set_number: Mapped[int] = mapped_column(Integer, nullable=False)
    reps_achieved: Mapped[int] = mapped_column(nullable=False)
    weight_achieved: Mapped[float] = mapped_column(nullable=False)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rpe: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )  # Rate of Perceived Exertion (1-10)

    session_exercise_result_id: Mapped[int] = mapped_column(
        ForeignKey("workout_session_exercise_results.id")
    )
    workout_session_exercise_result: Mapped["WorkoutSessionExerciseResult"] = (
        relationship(back_populates="workout_session_exercise_set_results")
    )
    workout_exercise_set_plan_id: Mapped[int] = mapped_column(
        ForeignKey("workout_exercise_set_plans.id")
    )
    workout_exercise_set_plan: Mapped["WorkoutExerciseSetPlan"] = relationship(
        back_populates="workout_session_exercise_set_results"
    )
