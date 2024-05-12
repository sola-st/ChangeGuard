def process_file(self, file_path, pickle_dags=False, session=None):
    self.logger.info("Processing file %s for tasks to queue", file_path)
    simple_dags = []
    try:
        dagbag = models.DagBag(file_path)
    except Exception:
        self.logger.exception("Failed at reloading the DAG file %s", file_path)
        Stats.incr('dag_file_refresh_error', 1, 1)
        return []
    if len(dagbag.dags) > 0:
        self.logger.info("DAG(s) %s retrieved from %s", dagbag.dags.keys(), file_path)
    else:
        self.logger.warning("No viable dags retrieved from %s", file_path)
        self.update_import_errors(session, dagbag)
        return []
    for dag in dagbag.dags.values():
        dag.sync_to_db()
    paused_dag_ids = [dag.dag_id for dag in dagbag.dags.values()
                      if dag.is_paused]
    for dag_id in dagbag.dags:
        dag , pickle_id  = dagbag.get_dag(dag_id), None
        if pickle_dags:
            pickle_id = dag.pickle(session).id
        task_ids = [task.task_id for task in dag.tasks]
        if dag_id not in paused_dag_ids:
            simple_dags.append(SimpleDag(dag.dag_id,
                                         task_ids,
                                         dag.full_filepath,
                                         dag.concurrency,
                                         dag.is_paused,
                                         pickle_id))
    if len(self.dag_ids) > 0:
        dags = [dag for dag in dagbag.dags.values()
                if dag.dag_id in self.dag_ids and
                dag.dag_id not in paused_dag_ids]
    else:
        dags = [dag for dag in dagbag.dags.values()
                if not dag.parent_dag and
                dag.dag_id not in paused_dag_ids]
    ti_keys_to_schedule = []
    self._process_dags(dagbag, dags, ti_keys_to_schedule)
    for (ti_key_0, ti_key_1, ti_key_2, *ti_key_len) in ti_keys_to_schedule:
        dag = dagbag.dags[ti_key_0]
        task = dag.get_task(ti_key_1)
        ti = models.TaskInstance(task, ti_key_2)
        ti.refresh_from_db(session=session, lock_for_update=True)
        dep_context = DepContext(deps=QUEUE_DEPS, ignore_task_deps=True)
        if ti.are_dependencies_met(dep_context=dep_context, session=session, verbose=True):
            ti.state = State.SCHEDULED
        self.logger.info('Creating / updating %s in ORM', ti)
        session.merge(ti)
        session.commit()
    try:
        self.update_import_errors(session, dagbag)
    except Exception:
        self.logger.exception("Error logging import errors!")
    try:
        dagbag.kill_zombies()
    except Exception:
        self.logger.exception("Error killing zombies!")
    return simple_dags
