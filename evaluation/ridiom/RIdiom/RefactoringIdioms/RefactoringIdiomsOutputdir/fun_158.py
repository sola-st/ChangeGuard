def update_state(
    self, session = NEW_SESSION, execute_callbacks = True
):
    callback = None
    class _UnfinishedStates(NamedTuple):
        def calculate(cls, unfinished_tis):
            return cls(tis=unfinished_tis)
        def should_schedule(self):
            return (
                bool(self.tis)
                and all(not t.task.depends_on_past for t in self.tis)
                and all(t.task.max_active_tis_per_dag is None for t in self.tis)
                and all(t.task.max_active_tis_per_dagrun is None for t in self.tis)
                and all(t.state != TaskInstanceState.DEFERRED for t in self.tis)
            )
        def recalculate(self):
            return self._replace(tis=[t for t in self.tis if t.state in State.unfinished])
    start_dttm = timezone.utcnow()
    self.last_scheduling_decision = start_dttm
    with Stats.timer(
        f"dagrun.dependency-check.{self.dag_id}",
        tags=self.stats_tags,
    ):
        dag , info  = self.get_dag(), self.task_instance_scheduling_decisions(session)
        tis , schedulable_tis , changed_tis , finished_tis , unfinished  = info.tis, info.schedulable_tis, info.changed_tis, info.finished_tis, _UnfinishedStates.calculate(info.unfinished_tis)
        if unfinished.should_schedule:
            are_runnable_tasks = schedulable_tis or changed_tis
            if not are_runnable_tasks:
                are_runnable_tasks, changed_by_upstream = self._are_premature_tis(
                    unfinished.tis, finished_tis, session
                )
                if changed_by_upstream:  
                    unfinished = unfinished.recalculate()
    leaf_task_ids = {t.task_id for t in dag.leaves}
    leaf_tis = {ti for ti in tis if ti.task_id in leaf_task_ids if ti.state != TaskInstanceState.REMOVED}
    if dag.teardowns:
        teardown_task_ids = {t.task_id for t in dag.teardowns}
        upstream_of_teardowns , teardown_tis  = {t.task_id for t in dag.tasks_upstream_of_teardowns}, {ti for ti in tis if ti.task_id in teardown_task_ids}
        on_failure_fail_tis , tis_upstream_of_teardowns  = (ti for ti in teardown_tis if ti.task.on_failure_fail_dagrun), (ti for ti in tis if ti.task_id in upstream_of_teardowns)
        leaf_tis -= teardown_tis
        leaf_tis.update(on_failure_fail_tis, tis_upstream_of_teardowns)
    if not unfinished.tis and any(leaf_ti.state in State.failed_states for leaf_ti in leaf_tis):
        self.log.error("Marking run %s failed", self)
        self.set_state(DagRunState.FAILED)
        self.notify_dagrun_state_changed(msg="task_failure")
        if execute_callbacks:
            dag.handle_callback(self, success=False, reason="task_failure", session=session)
        elif dag.has_on_failure_callback:
            from airflow.models.dag import DagModel
            dag_model = DagModel.get_dagmodel(dag.dag_id, session)
            callback = DagCallbackRequest(
                full_filepath=dag.fileloc,
                dag_id=self.dag_id,
                run_id=self.run_id,
                is_failure_callback=True,
                processor_subdir=None if dag_model is None else dag_model.processor_subdir,
                msg="task_failure",
            )
    elif not unfinished.tis and all(leaf_ti.state in State.success_states for leaf_ti in leaf_tis):
        self.log.info("Marking run %s successful", self)
        self.set_state(DagRunState.SUCCESS)
        self.notify_dagrun_state_changed(msg="success")
        if execute_callbacks:
            dag.handle_callback(self, success=True, reason="success", session=session)
        elif dag.has_on_success_callback:
            from airflow.models.dag import DagModel
            dag_model = DagModel.get_dagmodel(dag.dag_id, session)
            callback = DagCallbackRequest(
                full_filepath=dag.fileloc,
                dag_id=self.dag_id,
                run_id=self.run_id,
                is_failure_callback=False,
                processor_subdir=None if dag_model is None else dag_model.processor_subdir,
                msg="success",
            )
    elif unfinished.should_schedule and not are_runnable_tasks:
        self.log.error("Task deadlock (no runnable tasks); marking run %s failed", self)
        self.set_state(DagRunState.FAILED)
        self.notify_dagrun_state_changed(msg="all_tasks_deadlocked")
        if execute_callbacks:
            dag.handle_callback(self, success=False, reason="all_tasks_deadlocked", session=session)
        elif dag.has_on_failure_callback:
            from airflow.models.dag import DagModel
            dag_model = DagModel.get_dagmodel(dag.dag_id, session)
            callback = DagCallbackRequest(
                full_filepath=dag.fileloc,
                dag_id=self.dag_id,
                run_id=self.run_id,
                is_failure_callback=True,
                processor_subdir=None if dag_model is None else dag_model.processor_subdir,
                msg="all_tasks_deadlocked",
            )
    else:
        self.set_state(DagRunState.RUNNING)
    if self._state == DagRunState.FAILED or self._state == DagRunState.SUCCESS:
        msg = (
            "DagRun Finished: dag_id=%s, execution_date=%s, run_id=%s, "
            "run_start_date=%s, run_end_date=%s, run_duration=%s, "
            "state=%s, external_trigger=%s, run_type=%s, "
            "data_interval_start=%s, data_interval_end=%s, dag_hash=%s"
        )
        self.log.info(
            msg,
            self.dag_id,
            self.execution_date,
            self.run_id,
            self.start_date,
            self.end_date,
            (self.end_date - self.start_date).total_seconds()
            if self.start_date and self.end_date
            else None,
            self._state,
            self.external_trigger,
            self.run_type,
            self.data_interval_start,
            self.data_interval_end,
            self.dag_hash,
        )
        session.flush()
    self._emit_true_scheduling_delay_stats_for_finished_state(finished_tis)
    self._emit_duration_stats_for_finished_state()
    session.merge(self)
    return schedulable_tis, callback
