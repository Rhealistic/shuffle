from datetime import datetime, timedelta

def get_next_day_of_week(day_of_week):
    days_mapping = {
        'monday': 0,
        'tuesday': 1,
        'wednesday': 2,
        'thursday': 3,
        'friday': 4,
        'saturday': 5,
        'sunday': 6
    }

    if isinstance(day_of_week, str):
        day_of_week = day_of_week.lower()

    today = datetime.today()
    days_until_next_day = (days_mapping[day_of_week] - today.weekday() + 7) % 7
    next_day = today + timedelta(days=days_until_next_day)
    return next_day