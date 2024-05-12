def _print_stat(self):
    if 0 < self.print_stats_interval < (
            timezone.utcnow() - self.last_stat_print_time).total_seconds():
        if self._file_paths:
            self._log_file_processing_stats(self._file_paths)
        self.last_stat_print_time = timezone.utcnow()
