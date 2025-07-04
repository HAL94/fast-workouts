from datetime import datetime, timedelta
import pytz


def format_to_local_time(date: datetime):
    return date.astimezone().strftime("%Y-%m-%d %H:%M:%S")


class TimeValidation:
    """
        A default buffer:
            - buffer_after_current_date_time: reminders should be higher than current date/time by this value (5 minutes)
            - buffer_before_workout_date_time: reminders should be less than start_at date/time by this value (5 minutes)
            - Therefore, scheduling should start 15 (DEFAULT_BUFFER_TIME * 3)

            - Maybe we should consider a sperate buffer between start and reminder, and between schedule time and reminder

    """
    DEFAULT_BUFFER_TIME = 5  # 5 minutes

    REMINDER_LIMITS = {
        # 15 minutes
        'MIN_SCHEDULE_START_TIME': DEFAULT_BUFFER_TIME * 3,  # 15 minutes
        # 30 days
        'ABSOLUTE_MAX_MINUTES': 43200,
        # 7 days
        'WEEKLY_MAX_MINUTES': 10080,
        # 24 hours
        'DAILY_MAX_MINUTES': 1440,
        # 12 hours
        'PRACTICAL_MAX_MINUTES': 720,
        # 5 minutes
        'MINIMUM_MINUTES': 5,
        # 50% of time until workout
        'MAX_PERCENTAGE_OF_WAIT_TIME': 0.5
    }

    @staticmethod
    def calculate_reminder_time(start_at: datetime, remind_before_minutes: int) -> datetime:
        """Calculate when the reminder should be sent"""
        return start_at - timedelta(minutes=remind_before_minutes)

    @staticmethod
    def is_reminder_time_valid(start_at: datetime, remind_before_minutes: int) -> bool:
        """Check if the calculated reminder time is in the future"""
        reminder_time = TimeValidation.calculate_reminder_time(
            start_at, remind_before_minutes
        )
        return reminder_time > datetime.now(pytz.UTC)

    @staticmethod
    def is_valid_start_datetime(start_at: datetime) -> dict[str, bool]:
        now = datetime.now(pytz.UTC)

        if start_at.tzinfo is None:
            start_at = pytz.UTC.localize(start_at)

        max_future = now + timedelta(days=30)

        is_too_early = start_at <= now + \
            timedelta(
                minutes=TimeValidation.DEFAULT_BUFFER_TIME * 2)

        return {
            "max_reached": start_at > max_future,
            "too_close_to_now": start_at <= now,
            "is_too_early": is_too_early
        }

    @staticmethod
    def get_max_reminder_minutes(start_at: datetime) -> int:
        """Get maximum valid remind_before_minutes for a given start time"""
        now = datetime.now(pytz.UTC)
        if start_at.tzinfo is None:
            start_at = pytz.UTC.localize(start_at)
        else:
            start_at = start_at.astimezone(pytz.UTC)

        time_diff = start_at - now
        return int(time_diff.total_seconds() / 60)

    @staticmethod
    def reminder_too_close_to_now(remind_before_minutes: int, start_at: datetime, buffer_time: int):
        now = datetime.now(pytz.UTC)

        if start_at.tzinfo is None:
            start_at = pytz.UTC.localize(start_at)
        else:
            start_at = start_at.astimezone(pytz.UTC)

        reminder_before_start = start_at - \
            timedelta(minutes=remind_before_minutes)

        diff_now_reminder = (reminder_before_start - now).total_seconds() / 60

        print(
            f"Difference between now and reminder: {diff_now_reminder}, now: {format_to_local_time(now)}"
            f" reminder_time: {format_to_local_time(reminder_before_start)}, workout_time: {format_to_local_time(start_at)}")

        return {
            "is_not_valid": diff_now_reminder < buffer_time,
            "reminder_send_minutes": diff_now_reminder,
            "now": now
        }

    @staticmethod
    def validate_excessive_reminder(start_at: datetime, remind_before_minutes: int, buffer_time: int = DEFAULT_BUFFER_TIME) -> dict:
        """
        Comprehensive validation for excessive reminder times
        Returns validation result with details
        """
        limits = TimeValidation.REMINDER_LIMITS

        if buffer_time != TimeValidation.DEFAULT_BUFFER_TIME:
            limits['MIN_SCHEDULE_START_TIME'] = buffer_time * 2 + buffer_time

        now = datetime.now(pytz.UTC)

        # Ensure start_at has timezone info
        if start_at.tzinfo is None:
            start_at = pytz.UTC.localize(start_at)
        else:
            start_at = start_at.astimezone(pytz.UTC)

        result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'suggested_max': None
        }

        # Check minimum
        if remind_before_minutes < limits['MINIMUM_MINUTES']:
            result['is_valid'] = False
            result['errors'].append(
                f"Minimum reminder time is {limits['MINIMUM_MINUTES']} minutes")

        # Check absolute maximum
        if remind_before_minutes > limits['ABSOLUTE_MAX_MINUTES']:
            result['is_valid'] = False
            result['errors'].append(
                f"Maximum reminder time is {limits['ABSOLUTE_MAX_MINUTES']} minutes (30 days)")

        # Calculate time until workout
        time_until_workout = start_at - now
        hours_until_workout = time_until_workout.total_seconds() / 3600
        minutes_until_workout = time_until_workout.total_seconds() / 60

        print(f"Hours until workout: {hours_until_workout}")
        print(f"Minutes until workout: {minutes_until_workout}")

        # Check if reminder is in the past
        if remind_before_minutes >= minutes_until_workout:
            result['is_valid'] = False
            result['errors'].append("Reminder time would be in the past")
            result['suggested_max'] = int(minutes_until_workout - 1)

        close_result = TimeValidation.reminder_too_close_to_now(
            remind_before_minutes, start_at, buffer_time=buffer_time)

        if close_result.get("is_not_valid"):
            result['is_valid'] = False
            formatted_datetime = format_to_local_time(now)

            result['errors'].append(f"Reminder would be sent in {close_result.get("reminder_send_minutes"):.1f} minutes, "
                                    f"which is too soon to the current date/time: {formatted_datetime} (minimum {buffer_time} minutes buffer required)")

        # Context-based excessive checks
        if hours_until_workout <= 24:
            # For workouts within 24 hours
            if remind_before_minutes > limits['PRACTICAL_MAX_MINUTES']:
                result['warnings'].append(
                    f"For workouts within 24 hours, consider max {limits['PRACTICAL_MAX_MINUTES']} minutes")
                result['suggested_max'] = min(
                    limits['PRACTICAL_MAX_MINUTES'], int(minutes_until_workout * 0.5))

        elif hours_until_workout <= 168:  # Within a week
            # For workouts within a week
            if remind_before_minutes > limits['DAILY_MAX_MINUTES']:
                result['warnings'].append(
                    f"For workouts within a week, consider max {limits['DAILY_MAX_MINUTES']} minutes")
                result['suggested_max'] = min(
                    limits['DAILY_MAX_MINUTES'], int(minutes_until_workout * 0.5))

        # Percentage-based check (reminder shouldn't be more than 50% of wait time)
        max_percentage_minutes = minutes_until_workout * \
            limits['MAX_PERCENTAGE_OF_WAIT_TIME']
        if remind_before_minutes > max_percentage_minutes:
            result['warnings'].append(
                f"Reminder time ({remind_before_minutes} min) is more than 50% of wait time. "
                f"Consider max {int(max_percentage_minutes)} minutes"
            )
            if result['suggested_max'] is None:
                result['suggested_max'] = int(max_percentage_minutes)

        # Practical suggestions based on workout timing
        if hours_until_workout > 24:
            practical_suggestions = TimeValidation._get_practical_suggestions(
                hours_until_workout)
            if remind_before_minutes > practical_suggestions['recommended_max']:
                result['warnings'].append(practical_suggestions['message'])

        return result

    @staticmethod
    def _get_practical_suggestions(hours_until_workout: float) -> dict:
        """Get practical suggestions based on how far the workout is"""
        if hours_until_workout <= 24:
            return {'recommended_max': 720, 'message': 'For same-day workouts, 12 hours max is recommended'}
        elif hours_until_workout <= 168:  # 1 week
            return {'recommended_max': 1440, 'message': 'For workouts this week, 24 hours max is recommended'}
        elif hours_until_workout <= 720:  # 1 month
            return {'recommended_max': 10080, 'message': 'For workouts this month, 1 week max is recommended'}
        else:
            return {'recommended_max': 43200, 'message': 'For distant workouts, 30 days max is recommended'}


class TimeReminderSuggestion:
    @staticmethod
    def get_reminder_suggestions(start_at: datetime) -> list:
        """Get suggested reminder times based on when the workout is scheduled"""
        now = datetime.now(pytz.UTC)
        if start_at.tzinfo is None:
            start_at = pytz.UTC.localize(start_at)
        else:
            start_at = start_at.astimezone(pytz.UTC)

        hours_until = (start_at - now).total_seconds() / 3600

        suggestions = []

        if hours_until >= 24:
            # 1 day, 12h, 3h, 1h, 30min
            suggestions.extend([1440, 720, 180, 60, 30])
        elif hours_until >= 12:
            suggestions.extend([720, 180, 60, 30])  # 12h, 3h, 1h, 30min
        elif hours_until >= 3:
            suggestions.extend([180, 60, 30, 15])  # 3h, 1h, 30min, 15min
        elif hours_until >= 1:
            suggestions.extend([60, 30, 15])  # 1h, 30min, 15min
        else:
            max_minutes = int(hours_until * 60) - 5  # Leave 5 min buffer
            if max_minutes >= 30:
                suggestions.append(30)
            if max_minutes >= 15:
                suggestions.append(15)
            if max_minutes >= 10:
                suggestions.append(10)

        # Filter suggestions to only include valid ones
        max_valid = int(hours_until * 60) - 1
        initial_data = [s for s in suggestions if s <= max_valid]

        def mapper(item: int):
            if item >= 1440:
                unit = "day"
            elif item >= 60:
                unit = "hour"
            else:
                unit = "minutes"
            return { "unit": unit, "value": item }

        generated = list(map(mapper, initial_data))

        return {"suggestions": generated}
