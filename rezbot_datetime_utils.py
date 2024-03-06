#datetime stuff
from datetime import datetime, timedelta

day_to_int = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6
}

def get_week_start():
    now = datetime.now()
    week_start = now - timedelta(days = now.weekday())
    week_start = datetime(year=week_start.year,
                        month=week_start.month,
                        day=week_start.day)
    return week_start

def get_seans_datetime(seans):#for exp seans = "Thursday 18:00"
    seans_day = seans.split(" ")[0]
    seans_time = seans.split(" ")[1]

    seans_day_int = day_to_int[seans_day]
    seans_day_int

    seans_time_hour = seans_time.split(":")[0]
    seans_time_minute = seans_time.split(":")[1]

    seans_datetime = get_week_start() + timedelta(days=int(seans_day_int),
                                hours=int(seans_time_hour),
                                minutes=int(seans_time_minute))
    
    return(seans_datetime)



