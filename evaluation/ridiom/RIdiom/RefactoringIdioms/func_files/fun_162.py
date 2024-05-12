def end(self):
    if TYPE_CHECKING:
        assert self.task_queue
        assert self.result_queue
        assert self.kube_scheduler
    self.log.info("Shutting down Kubernetes executor")
    try:
        self.log.debug("Flushing task_queue...")
        self._flush_task_queue()
        self.log.debug("Flushing result_queue...")
        self._flush_result_queue()
        self.task_queue.join()
        self.result_queue.join()
    except ConnectionResetError:
        self.log.exception("Connection Reset error while flushing task_queue and result_queue.")
    if self.kube_scheduler:
        self.kube_scheduler.terminate()
    self._manager.shutdown()
