def _write_lock_file(self, repo, force = False):
    if self._write_lock and (force or self._update):
        updated_lock = self._locker.set_lock_data(self._package, repo.packages)
        if updated_lock:
            self._io.write_line("")
            self._io.write_line("<info>Writing lock file</>")
