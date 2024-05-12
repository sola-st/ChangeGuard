def triggerer(args):
    settings.MASK_SECRETS_IN_LOGS = True
    print(settings.HEADER)
    triggerer_heartrate = conf.getfloat("triggerer", "JOB_HEARTBEAT_SEC")
    if args.daemon:
        pid, stdout, stderr, log_file = setup_locations(
            "triggerer", args.pid, args.stdout, args.stderr, args.log_file
        )
        handle = setup_logging(log_file)
        with open(stdout, "a") as stdout_handle, open(stderr, "a") as stderr_handle:
            stdout_handle.truncate(0)
            stderr_handle.truncate(0)
            daemon_context = daemon.DaemonContext(
                pidfile=TimeoutPIDLockFile(pid, -1),
                files_preserve=[handle],
                stdout=stdout_handle,
                stderr=stderr_handle,
                umask=int(settings.DAEMON_UMASK, 8),
            )
            with daemon_context, _serve_logs(args.skip_serve_logs):
                triggerer_job_runner = TriggererJobRunner(
                    job=Job(heartrate=triggerer_heartrate), capacity=args.capacity
                )
                run_job(job=triggerer_job_runner.job, execute_callable=triggerer_job_runner._execute)
    else:
        signal.signal(signal.SIGINT, sigint_handler)
        signal.signal(signal.SIGTERM, sigint_handler)
        signal.signal(signal.SIGQUIT, sigquit_handler)
        with _serve_logs(args.skip_serve_logs):
            triggerer_job_runner = TriggererJobRunner(
                job=Job(heartrate=triggerer_heartrate), capacity=args.capacity
            )
            run_job(job=triggerer_job_runner.job, execute_callable=triggerer_job_runner._execute)
