def __init__(
    self,
    job,
    subdir = settings.DAGS_FOLDER,
    num_runs = conf.getint("scheduler", "num_runs"),
    num_times_parse_dags = -1,
    scheduler_idle_sleep_time = conf.getfloat("scheduler", "scheduler_idle_sleep_time"),
    do_pickle = False,
    log = None,
    processor_poll_interval = None,
):
    super().__init__(job)
    self.subdir , self.num_runs , self.num_times_parse_dags  = subdir, num_runs, num_times_parse_dags
    if processor_poll_interval:
        warnings.warn(
            "The 'processor_poll_interval' parameter is deprecated. "
            "Please use 'scheduler_idle_sleep_time'.",
            RemovedInAirflow3Warning,
            stacklevel=2,
        )
        scheduler_idle_sleep_time = processor_poll_interval
    self._scheduler_idle_sleep_time , self._zombie_threshold_secs , self._standalone_dag_processor , self._dag_stale_not_seen_duration , stalled_task_timeout  = scheduler_idle_sleep_time, conf.getint('scheduler', 'scheduler_zombie_task_threshold'), conf.getboolean('scheduler', 'standalone_dag_processor'), conf.getint('scheduler', 'dag_stale_not_seen_duration'), conf.getfloat('celery', 'stalled_task_timeout', fallback=0)
    if stalled_task_timeout:
        warnings.warn(
            "The '[celery] stalled_task_timeout' config option is deprecated. "
            "Please update your config to use '[scheduler] task_queued_timeout' instead.",
            DeprecationWarning,
        )
    task_adoption_timeout = conf.getfloat("celery", "task_adoption_timeout", fallback=0)
    if task_adoption_timeout:
        warnings.warn(
            "The '[celery] task_adoption_timeout' config option is deprecated. "
            "Please update your config to use '[scheduler] task_queued_timeout' instead.",
            DeprecationWarning,
        )
    worker_pods_pending_timeout = conf.getfloat(
        "kubernetes_executor", "worker_pods_pending_timeout", fallback=0
    )
    if worker_pods_pending_timeout:
        warnings.warn(
            "The '[kubernetes_executor] worker_pods_pending_timeout' config option is deprecated. "
            "Please update your config to use '[scheduler] task_queued_timeout' instead.",
            DeprecationWarning,
        )
    task_queued_timeout = conf.getfloat("scheduler", "task_queued_timeout")
    self._task_queued_timeout , self.do_pickle  = max(stalled_task_timeout, task_adoption_timeout, worker_pods_pending_timeout, task_queued_timeout), do_pickle
    if log:
        self._log = log
    sql_conn = conf.get_mandatory_value("database", "sql_alchemy_conn").lower()
    self.using_sqlite , self.processor_agent  = sql_conn.startswith('sqlite'), None
    self.dagbag = DagBag(dag_folder=self.subdir, read_dags_from_db=True, load_op_links=False)
