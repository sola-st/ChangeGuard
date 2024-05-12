def update_task_state(self, key, state, info):
    try:
        if state == celery_states.SUCCESS:
            self.success(key, info)
        elif state in (celery_states.FAILURE, celery_states.REVOKED):
            self.fail(key, info)
        elif state in (celery_states.STARTED, celery_states.PENDING):
            pass
        else:
            self.log.info("Unexpected state for %s: %s", key, state)
    except Exception:
        self.log.exception("Error syncing the Celery executor, ignoring it.")
