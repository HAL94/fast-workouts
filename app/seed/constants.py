from datetime import datetime, timedelta
from typing import Any

# --- Categories Data ---
# Represents exercise categories
exercise_categories: list[dict[str, Any]] = [
    {"id": 1, "name": "Strength Training"},
    {"id": 2, "name": "Weightlifting (Free Weights)"},
    {"id": 3, "name": "Compound Exercises"},
    {"id": 4, "name": "Powerlifting Focus"},
    {"id": 5, "name": "Bodyweight Exercises"},
    {"id": 6, "name": "Machine Exercises"},
    {"id": 7, "name": "Isolation Exercises"},
    {"id": 8, "name": "Core Strength"},
    {"id": 9, "name": "Calisthenics"},
]

# --- Exercise Data ---
# Represents exercises
exercises_list: list[dict[str, Any]] = [
    {"id": 1, "name": "Overhead Press (Shoulder Press)"},
    {"id": 2, "name": "Bicep Curl"},
    {"id": 3, "name": "Russian Twists"},
    {"id": 4, "name": "Squat"},
    {"id": 5, "name": "Crunches/Sit-ups"},
    {"id": 6, "name": "Glute Bridge/Hip Thrust"},
    {"id": 7, "name": "Leg Curl"},
    {"id": 8, "name": "Rear Delt Fly"},
    {"id": 9, "name": "Calf Raises"},
    {"id": 10, "name": "Good Mornings"},
    {"id": 11, "name": "Front Raise"},
    {"id": 12, "name": "Bench Press"},
    {"id": 13, "name": "Dumbbell Row"},
    {"id": 14, "name": "Plank"},
    {"id": 15, "name": "Tricep Extension"},
    {"id": 16, "name": "Leg Press"},
    {"id": 17, "name": "Shrugs"},
    {"id": 18, "name": "Lunges"},
    {"id": 19, "name": "Pull-up/Chin-up"},
    {"id": 20, "name": "Bent-Over Row"},
    {"id": 21, "name": "Deadlift"},
    {"id": 22, "name": "Lateral Raise"},
    {"id": 23, "name": "Leg Extension"},
    {"id": 24, "name": "Face Pulls"},
]

# --- ExerciseCategory Data ---
# Represents a categorization of exercises
exercises_by_categories = {
    "Strength Training": [
        "Bench Press",
        "Bent-Over Row",
        "Bicep Curl",
        "Calf Raises",
        "Crunches/Sit-ups",
        "Deadlift",
        "Dumbbell Row",
        "Face Pulls",
        "Front Raise",
        "Glute Bridge/Hip Thrust",
        "Good Mornings",
        "Leg Curl",
        "Leg Extension",
        "Leg Press",
        "Lunges",
        "Overhead Press (Shoulder Press)",
        "Plank",
        "Pull-up/Chin-up",
        "Rear Delt Fly",
        "Russian Twists",
        "Shrugs",
        "Squat",
        "Tricep Extension",
    ],
    "Weightlifting (Free Weights)": [
        "Bench Press",
        "Bent-Over Row",
        "Bicep Curl",
        "Calf Raises",
        "Deadlift",
        "Dumbbell Row",
        "Face Pulls",
        "Front Raise",
        "Glute Bridge/Hip Thrust",
        "Good Mornings",
        "Lunges",
        "Overhead Press (Shoulder Press)",
        "Rear Delt Fly",
        "Shrugs",
        "Squat",
        "Tricep Extension",
        "Lateral Raise",
    ],
    "Compound Exercises": [
        "Bench Press",
        "Bent-Over Row",
        "Deadlift",
        "Dumbbell Row",
        "Face Pulls",
        "Glute Bridge/Hip Thrust",
        "Good Mornings",
        "Leg Press",
        "Lunges",
        "Overhead Press (Shoulder Press)",
        "Pull-up/Chin-up",
        "Squat",
    ],
    "Powerlifting Focus": ["Bench Press", "Deadlift", "Squat"],
    "Bodyweight Exercises": [
        "Calf Raises",
        "Crunches/Sit-ups",
        "Glute Bridge/Hip Thrust",
        "Lunges",
        "Plank",
        "Pull-up/Chin-up",
        "Russian Twists",
    ],
    "Machine Exercises": ["Leg Curl", "Leg Extension", "Leg Press"],
    "Isolation Exercises": [
        "Bicep Curl",
        "Calf Raises",
        "Glute Bridge/Hip Thrust",
        "Leg Curl",
        "Leg Extension",
        "Lateral Raise",
        "Front Raise",
        "Rear Delt Fly",
        "Shrugs",
        "Tricep Extension",
    ],
    "Core Strength": ["Crunches/Sit-ups", "Plank", "Russian Twists"],
    "Calisthenics": ["Crunches/Sit-ups", "Plank", "Pull-up/Chin-up"],
}

# --- ExerciseMuscleGroup Data ---
# Represents exercises and muscles they target
muscle_groups = {
    "Squat": [
        "Quadriceps",
        "Hamstrings",
        "Glutes",
        "Adductors",
        "Calves",
        "Lower Back",
        "Core",
    ],
    "Deadlift": [
        "Hamstrings",
        "Glutes",
        "Lower Back",
        "Trapezius",
        "Forearms",
        "Core",
        "Quadriceps",
    ],
    "Bench Press": ["Pectoralis Major", "Anterior Deltoids", "Triceps"],
    "Overhead Press (Shoulder Press)": [
        "Anterior Deltoids",
        "Lateral Deltoids",
        "Triceps",
        "Upper Trapezius",
        "Core",
    ],
    "Bent-Over Row": [
        "Latissimus Dorsi",
        "Rhomboids",
        "Trapezius",
        "Posterior Deltoids",
        "Biceps",
        "Forearms",
    ],
    "Pull-up/Chin-up": [
        "Latissimus Dorsi",
        "Biceps",
        "Forearms",
        "Rhomboids",
        "Trapezius",
    ],
    "Lunges": ["Quadriceps", "Hamstrings", "Glutes", "Calves", "Core"],
    "Leg Press": ["Quadriceps", "Hamstrings", "Glutes", "Calves"],
    "Leg Curl": ["Hamstrings"],
    "Leg Extension": ["Quadriceps"],
    "Calf Raises": ["Gastrocnemius", "Soleus"],
    "Bicep Curl": ["Biceps", "Brachialis", "Brachioradialis"],
    "Tricep Extension": ["Triceps"],
    "Lateral Raise": ["Lateral Deltoids"],
    "Front Raise": ["Anterior Deltoids"],
    "Rear Delt Fly": ["Posterior Deltoids", "Rhomboids", "Trapezius"],
    "Shrugs": ["Trapezius"],
    "Plank": [
        "Rectus Abdominis",
        "Obliques",
        "Transverse Abdominis",
        "Lower Back",
        "Shoulders",
        "Glutes",
    ],
    "Crunches/Sit-ups": ["Rectus Abdominis", "Obliques"],
    "Russian Twists": ["Obliques", "Rectus Abdominis", "Transverse Abdominis"],
    "Good Mornings": ["Hamstrings", "Glutes", "Lower Back"],
    "Face Pulls": ["Posterior Deltoids", "Rhomboids", "Trapezius", "Rotator Cuff"],
    "Glute Bridge/Hip Thrust": ["Glutes", "Hamstrings"],
    "Dumbbell Row": [
        "Latissimus Dorsi",
        "Rhomboids",
        "Trapezius",
        "Posterior Deltoids",
        "Biceps",
        "Forearms",
    ],
}

# --- MuscleGroup Data ---
# Represents unique muscle group data
all_unique_muscle_groups: list[dict[str, Any]] = [
    {"id": 1, "name": "Adductors"},
    {"id": 2, "name": "Anterior Deltoids"},
    {"id": 3, "name": "Biceps"},
    {"id": 4, "name": "Brachialis"},
    {"id": 5, "name": "Brachioradialis"},
    {"id": 6, "name": "Calves"},
    {"id": 7, "name": "Core"},
    {"id": 8, "name": "Forearms"},
    {"id": 9, "name": "Gastrocnemius"},
    {"id": 10, "name": "Glutes"},
    {"id": 11, "name": "Hamstrings"},
    {"id": 12, "name": "Latissimus Dorsi"},
    {"id": 13, "name": "Lateral Deltoids"},
    {"id": 14, "name": "Lower Back"},
    {"id": 15, "name": "Obliques"},
    {"id": 16, "name": "Pectoralis Major"},
    {"id": 17, "name": "Posterior Deltoids"},
    {"id": 18, "name": "Quadriceps"},
    {"id": 19, "name": "Rectus Abdominis"},
    {"id": 20, "name": "Rhomboids"},
    {"id": 21, "name": "Rotator Cuff"},
    {"id": 22, "name": "Shoulders"},
    {"id": 23, "name": "Soleus"},
    {"id": 24, "name": "Transverse Abdominis"},
    {"id": 25, "name": "Trapezius"},
    {"id": 26, "name": "Triceps"},
    {"id": 27, "name": "Upper Trapezius"},
]

# --- WorkoutPlan Data ---
# Represents reusable workout templates
workout_plans_data: list[dict[str, Any]] = [
    {
        "id": 1,
        "user_id": 1,  # Assumed existing user
        "title": "Full Body Strength",
        "description": "A comprehensive plan targeting all major muscle groups.",
        "comments": "Great for building foundational strength.",
    },
    {
        "id": 2,
        "user_id": 1,
        "title": "Upper Body Focus",
        "description": "Dedicated to increasing upper body strength and mass.",
        "comments": "Requires adequate recovery time for chest and arms.",
    },
]


# --- WorkoutExercisePlan Data ---
# Defines the planned exercises within each WorkoutPlan
workout_exercise_plans_data: list[dict[str, Any]] = [
    # For "Full Body Strength" (workout_plan_id: 1)
    {
        "id": 1,
        "workout_plan_id": 1,
        "exercise_id": 1,  # Assumed existing Exercise: Squat
        "order_in_plan": 1,
        "target_reps": "5",
        "target_sets": 3,
        "target_weights": 100,  # kg
        "target_duration_minutes": None,
        "notes": "Ensure proper depth and core engagement.",
    },
    {
        "id": 2,
        "workout_plan_id": 1,
        "exercise_id": 2,  # Assumed existing Exercise: Bench Press
        "order_in_plan": 2,
        "target_reps": "8",
        "target_sets": 3,
        "target_weights": 70,  # kg
        "target_duration_minutes": None,
        "notes": "Maintain consistent tempo.",
    },
    {
        "id": 3,
        "workout_plan_id": 1,
        "exercise_id": 3,  # Assumed existing Exercise: Deadlift
        "order_in_plan": 3,
        "target_reps": "5",
        "target_sets": 2,
        "target_weights": 120,  # kg
        "target_duration_minutes": None,
        "notes": "Keep spine neutral.",
    },
    # For "Upper Body Focus" (workout_plan_id: 2)
    {
        "id": 4,
        "workout_plan_id": 2,
        "exercise_id": 2,  # Assumed existing Exercise: Bench Press
        "order_in_plan": 1,
        "target_reps": "10",
        "target_sets": 4,
        "target_weights": 65,  # kg
        "target_duration_minutes": None,
        "notes": "Warm up rotator cuffs.",
    },
]

# --- WorkoutPlanSchedule Data ---
# Schedules specific WorkoutPlans for future dates/times
now = datetime.now()
workout_plan_schedules_data = [
    {
        "id": 1,
        "user_id": 1,  # Note: User ID is also present here in your model
        "workout_plan_id": 1,  # Links to "Full Body Strength"
        "start_at": now + timedelta(days=1, hours=9, minutes=0),  # Tomorrow 9:00 AM
        "end_time": now + timedelta(days=1, hours=10, minutes=30),  # Tomorrow 10:30 AM
        "remind_before_minutes": 15,  # minutes
        "created_at": now,  # Inherited from Base
        "updated_at": now,  # Inherited from Base
    },
    {
        "id": 2,
        "user_id": 1,
        "workout_plan_id": 2,  # Links to "Upper Body Focus"
        "start_at": now + timedelta(days=7, hours=18, minutes=0),  # Next week 6:00 PM
        "end_time": now + timedelta(days=7, hours=19, minutes=15),  # Next week 7:15 PM
        "remind_before_minutes": 30,
    },
]

# --- WorkoutSession Data ---
# Represents an actual instance of a workout, completed or scheduled.
workout_sessions_data: list[dict[str, Any]] = [
    {
        "id": 1,
        "user_id": 1,
        "workout_plan_id": 1,  # Linked to "Full Body Strength" plan
        "schedule_id": 1,  # Linked to WorkoutPlanSchedule 1
        "title": "Full Body Strength - 2025-06-08 Session",
        "started_at": now
        - timedelta(days=10, hours=1, minutes=55),  # Completed 10 days ago
        "ended_at": now - timedelta(days=10, hours=0, minutes=20),
        "duration_minutes": 95,
        "status": "completed",
        "session_comments": "Great session, felt strong on squats. Need to push more on deadlifts next time."
    },
    {
        "id": 2,
        "user_id": 1,
        "workout_plan_id": 2,  # Ad-hoc sessions should be considered, meaning (not from a plan)
        "schedule_id": 2,
        "title": "Morning Outdoor Run",
        "started_at": now
        - timedelta(days=3, hours=8, minutes=0),  # Completed 3 days ago
        "ended_at": now - timedelta(days=3, hours=8, minutes=45),
        "duration_minutes": 45,
        "status": "completed",
        "session_comments": "Refreshing run, slightly humid.",
    },
    {
        "id": 3,
        "user_id": 1,
        "workout_plan_id": 2,  # Linked to "Upper Body Focus" plan
        "schedule_id": 2,  # Linked to WorkoutPlanSchedule 2
        "title": "Upper Body Workout - Scheduled",
        "started_at": None,  # Not yet started
        "ended_at": None,
        "duration_minutes": None,
        "status": "coming_soon",  # As per your provided enum
        "session_comments": None,
    },
    {
        "id": 4,
        "user_id": 1,
        "workout_plan_id": 2,  # Linked to "Upper Body Focus" plan
        "schedule_id": None,  # No scheduling, ad-hoc session
        "title": "Cardio Run",
        "started_at": now - timedelta(hours=10, minutes=0),  # Not yet started
        "ended_at": now - timedelta(hours=10, minutes=30),
        "duration_minutes": None,
        "status": "completed",  # As per your provided enum
        "session_comments": None,
    },
]

# --- WorkoutSessionResult Data ---
# Represents summary results for an exercise within a completed WorkoutSession.
# Only results linked to a WorkoutPlan have been kept.
workout_session_results_data = [
    {
        "id": 1,
        "workout_session_id": 1,  # Result for WorkoutSession 1
        "workout_exercise_plan_id": 1,  # Linked to plan_squat (exercise_id:1, workout_plan_id:1)
        "exercise_id": 1,  # The exercise this result is for (Squat)
        "workout_plan_id": 1,  # The plan this exercise belongs to
        "reps_achieved": 5,
        "sets_achieved": 3,
        "weights_achieved": 105.0,  # Achieved slightly more than target
        "total_weight_lifted": 1575,  # 3 sets * 5 reps * 105 kg
        "created_at": now - timedelta(days=10),  # Inherited from Base
        "updated_at": now - timedelta(days=10),  # Inherited from Base
    },
]

# helpers
exercise_name_to_id = {ex["name"]: ex["id"] for ex in exercises_list}
exercise_category_to_id = {excat["name"]: excat["id"] for excat in exercise_categories}
muscle_group_to_id = {
    musclegroup["name"]: musclegroup["id"] for musclegroup in all_unique_muscle_groups
}
