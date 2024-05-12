def create_timetable(interval, timezone):
    if interval is NOTSET:
        return DeltaDataIntervalTimetable(DEFAULT_SCHEDULE_INTERVAL)
    if interval is None:
        return NullTimetable()
    if interval == "@once":
        return OnceTimetable()
    if interval == "@continuous":
        return ContinuousTimetable()
    if isinstance(interval, (timedelta, relativedelta)):
        return DeltaDataIntervalTimetable(interval)
    if isinstance(interval, str):
        return CronDataIntervalTimetable(interval, timezone)
    raise ValueError(f"{interval!r} is not a valid interval.")
