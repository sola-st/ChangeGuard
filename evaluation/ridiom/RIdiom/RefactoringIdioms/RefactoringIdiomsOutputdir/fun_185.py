def report_speed(self):
    now = time()
    if now - self._prev_time >= self._update_interval:
        downloaded = self.status.downloaded
        try:
            speed = ((downloaded - self._prev_bytes)
                     / (now - self._prev_time))
        except ZeroDivisionError:
            speed = 0
        if not self.status.total_size:
            self._status_line = PROGRESS_NO_CONTENT_LENGTH.format(
                downloaded=humanize_bytes(downloaded),
                speed=humanize_bytes(speed),
            )
        else:
            try:
                percentage = downloaded / self.status.total_size * 100
            except ZeroDivisionError:
                percentage = 0
            if not speed:
                eta = '-:--:--'
            else:
                s = int((self.status.total_size - downloaded) / speed)
                h, s = divmod(s, 60 * 60)
                m, s = divmod(s, 60)
                eta = f'{h}:{m:0>2}:{s:0>2}'
            self._status_line = PROGRESS.format(
                percentage=percentage,
                downloaded=humanize_bytes(downloaded),
                speed=humanize_bytes(speed),
                eta=eta,
            )
        self._prev_time , self._prev_bytes  = now, downloaded
    self.output.write(
        f'{CLEAR_LINE} {SPINNER[self._spinner_pos]} {self._status_line}'
    )
    self.output.flush()
    self._spinner_pos = (self._spinner_pos + 1) % len(SPINNER)
