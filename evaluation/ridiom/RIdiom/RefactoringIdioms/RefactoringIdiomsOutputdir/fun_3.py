def __init__(self, cron, timezone):
    self._expression = cron_presets.get(cron, cron)
    if isinstance(timezone, str):
        timezone = Timezone(timezone)
    self._timezone = timezone
    try:
        descriptor = ExpressionDescriptor(
            expression=self._expression, casing_type=CasingTypeEnum.Sentence, use_24hour_time_format=True
        )
        if len(croniter(self._expression).expanded) > 5:
            raise FormatException()
        interval_description = descriptor.get_description()
    except (CroniterBadCronError, FormatException, MissingFieldException):
        interval_description = ""
    self.description = interval_description
