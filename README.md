# Project Intro
A FastAPI server that will track and record workout exercises. This project is from the [roadmap.sh](https://roadmap.sh/) and can be found at here: [Workout Fitness Tracker](https://roadmap.sh/projects/fitness-workout-tracker)


# Tools
- `FastAPI[standard]>=0.115.12`
- `celery>=5.5.3`
- `PostgreSQL=latest`
- `uv` for project management
- `pyjwt>=2.10.1`
- `faker>=37.3.0`

# Technology
- `FastAPI`
- `PostgreSQL`
- `Resend API`: handles sending emails (get your key from [`resend`](https://resend.com/))
- `Celery`: for queueing tasks and handling jobs.
- `Redis`: as a message broker and as a database for `celery`.

# Features
- User Authentication and Authorization
    - User Signup and Login.
    - JWT-based accesss with protected routes for API.
    - Bcrypt password hashing.

- System-provided Exercises:
    - System has a record of generated exercises
    - Each exercise link to many muscle groups.
    - System supports categories of exercises.

- Workout Plans
    - Create plans for exercises and sets with following details:
        - target repetitions, 
        - target weight and 
        - target exercises duration.
    - Record notes for exercises and workouts.

- Workout Session Results
    - Track results for exercises and sets:
        - achieved sets.
        - repetitions achieved for a set.
        - weight acheived for a given set.
        - duration achieved at exercise-level.
        - duration achieved at set-level.
        - Track Rate of Perceived Exertion.

- Scheduling
    - Schedule workouts at a specific date/time.
    - Set reminders for workout schedule via email.

- Report
    - For any given workout session, get a comparison between your plans vs your achievements.


# Installation
1. Clone repository
```git clone https://github.com/HAL94/fast-workouts.git```

2. Navigate to project directory: `cd fast-workouts`

3. Create environment with your favourite tool.
    - using `uv`: `uv venv .venv`
    - activate (Windows): `.venv\Scripts\activate`
    - activate (MacOS/Linux): `source .venv/bin/activate`

4. Setup `.env`:
```
PG_USER="postgres"
PG_PW="postgres"
PG_SERVER="localhost"
PG_PORT="5432" 
PG_DB="workouts"
REDIS_SERVER="redis://localhost:6379"
ENV="dev"
EMAIL_SERVICE="API_FOR_RESEND"
```

5. Install dependencies:
with your tool of choice or with uv: `uv sync`

6. Deactivate environement
```deactivate```

# Using Docker
A `docker-compose.yaml` file is included for various services:
- `app`: Backend application.
- `migration`: Attempts to apply `alembic` migrations
- `seeder`: Applies data seeding.
- `postgres`.
- `redis`.
- `celery`: runs the celery worker.

1. Ensure the `PG_SERVER` env variable refers to the `postgres` server instead of `localhost`:
2. Similarly for `REDIS_SERVER`: `redis://redis:6379`

As these are the names of the services.

## Running
`docker compose up`

# Usage
Use one of the following commands:
- `uv run uvicorn app.main:app --reload`
- Alternative: `uv run fastapi dev`

This will start the API server at the `http://localhost:8000/api/v1`.

# Data Seeding
Data is seeded using `faker` and it is generated for: `User` data and for:
- Exercise Categories
- Exercises
- MuscleGroups


Seeding module is located at `app/seed`. Generated users are populated in `PostgreSQL`. with a dummy password as `123456`.

## Running seed as a Module
- Using uv: `uv run python -m app.seed.run`
- This will generate:
    - One user with a random name, email and a password fixed at: `123456`.
    - Exercises, Categories and Muscle Groups.

Everytime you run the script, it will generate one user.

# API

## Authentication
Base path: /auth
- POST /login - Login
- GET /auth/me - Get/Verify User
- POST /auth/signup Register

## Workouts
Base path: /workouts

- GET / - Get all workout plans (paginated)
- GET /{workout_plan_id} - Get a specific workout plan
- POST / - Create a new workout plan
- PATCH / - Update an existing workout plan
- DELETE /{workout_plan_id} - Delete a workout plan

### Exercise Plans
Base path: /workouts/{workout_plan_id}/exercises

- GET / - Get all exercise plans for a workout (paginated)
- GET /{exercise_plan_id} - Get a specific exercise plan
- POST / - Add an exercise plan to a workout
- PATCH /{exercise_plan_id} - Update an exercise plan
- DELETE /{exercise_plan_id} - Delete an exercise plan

### Exercise Set Plans
Base path: /workouts/{workout_plan_id}/exercises/{exercise_plan_id}/sets

- GET / - Get all set plans for an exercise (paginated)
- GET /{exercise_set_plan_id} - Get a specific set plan
- POST / - Create a new set plan
- PATCH /{exercise_set_plan_id} - Update a set plan
- DELETE /{exercise_set_plan_id} - Delete a set plan

### Workout Schedules
Base path: /workouts/{workout_plan_id}/schedules

- GET / - Get all schedules for a workout plan (paginated)
- GET /{workout_plan_schedule_id} - Get a specific schedule
- GET /suggestions - Get schedule reminder suggestions
- POST / - Create a new workout schedule

## Workout Sessions
Base path: /sessions

- GET / - Get all workout sessions (paginated)
- GET /{session_id} - Get a specific workout session
- POST /start - Start a new workout session
- POST /end/{session_id} - End a workout session
- POST /{session_id}/results - Record session results
- GET /{session_id}/report - Generate workout report

### Exercise Results
Base path: /sessions/{session_id}/exercises
- GET / - Get all exercises results (paginated)
- GET /{result_id} - Get a specific exercise result
- POST / - Create a new exercise result
- PATCH /{set_result_id} - Update an exercise result
- DELETE /{set_result_id} - Delete an exercise result

### Exercise Set Results
Base path: /sessions/{session_id}/exercises/{exercise_result_id}/sets

- GET / - Get all set results (paginated)
- GET /{set_result_id} - Get a specific set result
- POST / - Create a new set result
- PATCH /{set_result_id} - Update a set result
- DELETE /{set_result_id} - Delete a set result

## Exercises
Base path: /exercises

- GET / - Get all exercises (paginated)
- GET /{exercise_id} - Get a specific exercise

## Muscle Groups
Base path: /muscle-groups

- GET / - Get all muscle groups (paginated)
- GET /{muscle_group_id} - Get a specific muscle group
- GET /{muscle_group_id}/exercises - Get exercises for a muscle group

## Categories
Base path: /categories

- GET / - Get all exercise categories (paginated)
- GET /{category_id} - Get a specific category
- GET /{category_id}/exercises - Get exercises for a category

All endpoints that return multiple items support pagination through query parameters. Authentication is required for most endpoints through JWT validation middleware.

# Scheduling Rules and Validation
## Time Buffers
- Default `buffer` time: 5 minutes
- Minimum scheduling start time: 15 minutes (3x default buffer)
- Maximum reminder time: 43,200 minutes (30 days)

## Validation Rules
### Start Time Validation
- Must be in the future
- Cannot be more than 30 days in the future
- Must be at least 15 minutes (3x default `buffer`) from current time

## Reminder Suggestions
Suggestions are dynamically generated based on time until workout:

### 1-3 hours until workout
if the workout is `1 hour` to `3 hours` in the future, these reminder values are suggested:
- 1 hour
- 30 minutes
- 15 minutes

### 3-12 hours until workout
if the workout is between `3 hour` to `12 hours` in the future, these reminder values are suggested
- 3 hours
- 1 hour
- 30 minutes
- 15 minutes

### 12-24 hours until workout
if the workout is between `12 hour` to `24 hours` in the future, these reminder values are suggested 
- 12 hours 
- 3 hours
- 1 hour
- 30 minutes


# Short-comings; Current Bugs and Future Work
- Integrate a frontend.
- Ensuring the sequence of exercise plans and/or set plans is still relatively buggy.
- Reports could be improved with AI
    - Could be more descriptive on analyzing if user's strngeth, cardio or general stats have improved.
- Support generating trends for exercise/set results
