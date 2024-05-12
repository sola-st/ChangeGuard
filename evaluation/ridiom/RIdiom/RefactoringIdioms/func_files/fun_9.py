def _read(
    self, ti, try_number, metadata = None
):
    if not metadata:
        metadata = {"offset": 0}
    if "offset" not in metadata:
        metadata["offset"] = 0
    offset = metadata["offset"]
    log_id = self._render_log_id(ti, try_number)
    logs = self.es_read(log_id, offset, metadata)
    logs_by_host = self._group_logs_by_host(logs)
    next_offset = offset if not logs else attrgetter(self.offset_field)(logs[-1])
    metadata["offset"] = str(next_offset)
    metadata["end_of_log"] = False
    if any(x[-1].message == self.end_of_log_mark for x in logs_by_host.values()):
        metadata["end_of_log"] = True
    cur_ts = pendulum.now()
    if "last_log_timestamp" in metadata:
        last_log_ts = timezone.parse(metadata["last_log_timestamp"])
        if int(next_offset) == 0 and cur_ts.diff(last_log_ts).in_seconds() > 5:
            metadata["end_of_log"] = True
            missing_log_message = (
                f"*** Log {log_id} not found in Elasticsearch. "
                "If your task started recently, please wait a moment and reload this page. "
                "Otherwise, the logs for this task instance may have been removed."
            )
            return [("", missing_log_message)], metadata
        if (
            cur_ts.diff(last_log_ts).in_minutes() >= 5
            or ("max_offset" in metadata and int(offset) >= int(metadata["max_offset"]))
        ):
            metadata["end_of_log"] = True
    if int(offset) != int(next_offset) or "last_log_timestamp" not in metadata:
        metadata["last_log_timestamp"] = str(cur_ts)
    def concat_logs(lines):
        log_range = (len(lines) - 1) if lines[-1].message == self.end_of_log_mark else len(lines)
        return "\n".join(self._format_msg(lines[i]) for i in range(log_range))
    message = [(host, concat_logs(hosted_log)) for host, hosted_log in logs_by_host.items()]
    return message, metadata
