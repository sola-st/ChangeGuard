def __init__(
    self,
    pod_name,
    pod_namespace,
    trigger_start_time,
    base_container_name,
    kubernetes_conn_id = None,
    poll_interval = 2,
    cluster_context = None,
    config_file = None,
    in_cluster = None,
    get_logs = True,
    startup_timeout = 120,
    on_finish_action = "delete_pod",
    should_delete_pod = None,
):
    super().__init__()
    self.pod_name = pod_name
    self.pod_namespace = pod_namespace
    self.trigger_start_time = trigger_start_time
    self.base_container_name = base_container_name
    self.kubernetes_conn_id = kubernetes_conn_id
    self.poll_interval = poll_interval
    self.cluster_context = cluster_context
    self.config_file = config_file
    self.in_cluster = in_cluster
    self.get_logs = get_logs
    self.startup_timeout = startup_timeout
    if should_delete_pod is not None:
        warnings.warn(
            "`should_delete_pod` parameter is deprecated, please use `on_finish_action`",
            category=AirflowProviderDeprecationWarning,
            stacklevel=2,
        )
        self.on_finish_action = (
            OnFinishAction.DELETE_POD if should_delete_pod else OnFinishAction.KEEP_POD
        )
        self.should_delete_pod = should_delete_pod
    else:
        self.on_finish_action = OnFinishAction(on_finish_action)
        self.should_delete_pod = self.on_finish_action == OnFinishAction.DELETE_POD
    self._hook = None
    self._since_time = None
