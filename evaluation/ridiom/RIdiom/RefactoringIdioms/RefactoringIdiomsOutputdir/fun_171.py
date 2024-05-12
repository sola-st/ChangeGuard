def update_state(self, session=None):
    dag , ready_tis , tis  = self.get_dag(), [], [ti for ti in self.get_task_instances(session=session, state=State.task_states + (State.SHUTDOWN,))]
    self.log.debug("number of tis tasks for %s: %s task(s)", self, len(tis))
    for ti in tis:
        ti.task = dag.get_task(ti.task_id)
    start_dttm , unfinished_tasks  = timezone.utcnow(), [t for t in tis if t.state in State.unfinished()]
    finished_tasks , none_depends_on_past , none_task_concurrency  = [t for t in tis if t.state in State.finished() + [State.UPSTREAM_FAILED]], all((not t.task.depends_on_past for t in unfinished_tasks)), all((t.task.task_concurrency is None for t in unfinished_tasks))
    if unfinished_tasks:
        scheduleable_tasks = [ut for ut in unfinished_tasks if ut.state in SCHEDULEABLE_STATES]
        self.log.debug(
            "number of scheduleable tasks for %s: %s task(s)",
            self, len(scheduleable_tasks))
        ready_tis, changed_tis = self._get_ready_tis(scheduleable_tasks, finished_tasks, session)
        self.log.debug("ready tis length for %s: %s task(s)", self, len(ready_tis))
        if none_depends_on_past and none_task_concurrency:
            are_runnable_tasks = ready_tis or self._are_premature_tis(
                unfinished_tasks, finished_tasks, session) or changed_tis
    duration = (timezone.utcnow() - start_dttm)
    Stats.timing("dagrun.dependency-check.{}".format(self.dag_id), duration)
    leaf_task_ids = {t.task_id for t in dag.leaves}
    leaf_tis = [ti for ti in tis if ti.task_id in leaf_task_ids]
    if not unfinished_tasks and any(
        leaf_ti.state in {State.FAILED, State.UPSTREAM_FAILED} for leaf_ti in leaf_tis
    ):
        self.log.error('Marking run %s failed', self)
        self.set_state(State.FAILED)
        dag.handle_callback(self, success=False, reason='task_failure',
                            session=session)
    elif not unfinished_tasks and all(
        leaf_ti.state in {State.SUCCESS, State.SKIPPED} for leaf_ti in leaf_tis
    ):
        self.log.info('Marking run %s successful', self)
        self.set_state(State.SUCCESS)
        dag.handle_callback(self, success=True, reason='success', session=session)
    elif (unfinished_tasks and none_depends_on_past and
          none_task_concurrency and not are_runnable_tasks):
        self.log.error('Deadlock; marking run %s failed', self)
        self.set_state(State.FAILED)
        dag.handle_callback(self, success=False, reason='all_tasks_deadlocked',
                            session=session)
    else:
        self.set_state(State.RUNNING)
    self._emit_duration_stats_for_finished_state()
    session.merge(self)
    session.commit()
    return ready_tis
