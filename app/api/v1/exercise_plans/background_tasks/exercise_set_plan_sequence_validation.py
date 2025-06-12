import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import WorkoutExerciseSetPlan

logger = logging.getLogger("uvicorn")


async def fix_exercise_set_plan_sequence(
    session: AsyncSession,
    exercise_plan_id: int,
):
    try:
        logger.info(
            f"[Background Task: ExerciseSetResequence]: Resequencing sets for WorkoutExercisePlan ID: {exercise_plan_id}"
        )

        stmt = (
            select(WorkoutExerciseSetPlan)
            .where(WorkoutExerciseSetPlan.workout_exercise_plan_id == exercise_plan_id)
            .order_by(WorkoutExerciseSetPlan.set_number)
        )

        set_plans_to_update = await session.scalars(stmt)
        updated_count = 0

        for index, set_plan in enumerate(set_plans_to_update, 1):  # Start from 1
            if set_plan.set_number != index:  # Only update if necessary
                set_plan.set_number = index
                session.add(set_plan)  # Add to session if modified
                updated_count += 1

        if updated_count > 0:
            await session.commit()
            logger.info(
                f"[Background Task: ExerciseSetResequence]: Successfully resequenced {updated_count} sets for WorkoutExercisePlan ID: {exercise_plan_id}"
            )
        else:
            logger.info(
                f"[Background Task: ExerciseSetResequence]: No sets needed resequencing for WorkoutExercisePlan ID: {exercise_plan_id}"
            )
    except Exception as e:
        await session.rollback()
        logger.error(
            f"[Background Task: ExerciseSetResequence]: Error for WorkoutExercisePlan ID {exercise_plan_id}: {e}"
        )
