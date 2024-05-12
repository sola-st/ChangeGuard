def _emit_true_scheduling_delay_stats_for_finished_state(self, finished_tis):
    if self.state == TaskInstanceState.RUNNING:
        return
    if self.external_trigger:
        return
    if not finished_tis:
        return
    try:
        dag = self.get_dag()
        if not dag.timetable.periodic:
            return
        try:
            first_start_date = min(ti.start_date for ti in finished_tis if ti.start_date)
        except ValueError:  
            pass
        else:
            data_interval_end = dag.get_run_data_interval(self).end
            true_delay = first_start_date - data_interval_end
            if true_delay.total_seconds() > 0:
                Stats.timing(f"dagrun.{dag.dag_id}.first_task_scheduling_delay", true_delay)
                Stats.timing(
                    "dagrun.first_task_scheduling_delay",
                    true_delay,
                    tags={"dag_id": dag.dag_id},
                )
    except Exception:
        self.log.warning("Failed to record first_task_scheduling_delay metric:", exc_info=True)
