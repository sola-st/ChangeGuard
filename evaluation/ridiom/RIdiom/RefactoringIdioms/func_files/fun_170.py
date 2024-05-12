def _check_value(self, action, value):
    executor = conf.get('core', 'EXECUTOR')
    if value == 'celery' and executor != ExecutorLoader.CELERY_EXECUTOR:
        message = f'celery subcommand works only with CeleryExecutor, your current executor: {executor}'
        raise ArgumentError(action, message)
    if value == 'kubernetes':
        try:
            import kubernetes.client  
        except ImportError:
            message = (
                'The kubernetes subcommand requires that you pip install the kubernetes python client.'
                "To do it, run: pip install 'apache-airflow[cncf.kubernetes]'"
            )
            raise ArgumentError(action, message)
    if action.choices is not None and value not in action.choices:
        check_legacy_command(action, value)
    super()._check_value(action, value)
