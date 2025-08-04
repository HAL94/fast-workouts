from alembic_utils.pg_trigger import PGTrigger
from alembic_utils.pg_function import PGFunction

exercise_plan_id_validation_func = PGFunction(
    schema="public",
    signature="validate_exercise_plan_id()",  # PGFunction will pre-append CREATE FUNCTION DDL
    definition="""
        RETURNS TRIGGER AS $$
        DECLARE
            current_plan_id INTEGER;
            exercise_parent_plan_id INTEGER;
        BEGIN
            IF NEW.exercise_plan_id IS NOT NULL THEN
                SELECT workout_plan_id INTO current_plan_id
                FROM workout_sessions
                WHERE id = NEW.workout_session_id;
                
                SELECT workout_plan_id INTO exercise_parent_plan_id
                FROM exercise_plans
                WHERE id = NEW.exercise_plan_id;
                
                -- Check if the workout plans are the same
                IF current_plan_id IS DISTINCT FROM exercise_parent_plan_id THEN
                    RAISE EXCEPTION 'Exercise result references an exercise plan not associated with the session''s workout plan.';
                END IF;
            END IF;
            RETURN NEW;
        END
        $$ LANGUAGE plpgsql;
    """,
)

exercise_set_plan_id_validation_func = PGFunction(
    schema="public",
    signature="validate_exercise_set_plan_id()",
    definition="""
        RETURNS TRIGGER AS $$
        DECLARE
            current_ex_plan_id INTEGER;
            target_ex_plan_id INTEGER;
        BEGIN
            IF NEW.exercise_set_plan_id IS NOT NULL THEN
                SELECT exercise_plan_id INTO current_ex_plan_id 
                FROM exercise_results 
                WHERE id = NEW.exercise_result_id;
                
                SELECT exercise_plan_id INTO target_ex_plan_id
                FROM exercise_set_plans
                WHERE id = NEW.exercise_set_plan_id;
                
                IF current_ex_plan_id IS DISTINCT FROM target_ex_plan_id THEN
                    RAISE EXCEPTION 'Exercise set result references a set plan not associated with the session''s workout plan.';
                END IF;
            END IF;
            RETURN NEW;
        END
        $$ LANGUAGE plpgsql;
    """,
)
exercise_set_plan_id_validation_trigger = PGTrigger(
    schema="public",
    signature="check_exercise_set_plan_id_relation",
    on_entity="public.exercise_set_results",
    definition="""
        BEFORE INSERT OR UPDATE on public.exercise_set_results
        FOR EACH ROW
        EXECUTE FUNCTION validate_exercise_set_plan_id();
    """,
)

exercise_plan_id_validation_trigger = PGTrigger(
    schema="public",
    signature="check_exercise_plan_id_relation",
    on_entity="public.exercise_results",  # PGTrigger will pre-append the CREATE TRIGGER DDL
    definition="""
        BEFORE INSERT OR UPDATE ON public.exercise_results
        FOR EACH ROW
        EXECUTE FUNCTION validate_exercise_plan_id();
    """,
)

# Using the psql cli, we can check all functions and their signatures using \df

# check for a trigger associated with a specific table: \d [table name] E.g. \d exercise_results
