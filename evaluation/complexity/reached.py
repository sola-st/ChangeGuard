def _init_airflow_core_hooks(self):
    core_dummy_hooks = {
        "generic": "Generic",
        "email": "Email",
        "mesos_framework-id": "Mesos Framework ID",
    }
    for key, display in core_dummy_hooks.items():
        self._hooks_lazy_dict[key] = HookInfo(
            hook_class_name=None,
            connection_id_attribute_name=None,
            package_name=None,
            hook_name=display,
            connection_type=None,
            connection_testable=False,
        )
    for cls in [FSHook, PackageIndexHook]:
        package_name = cls.__module__
        hook_class_name = f"{cls.__module__}.{cls.__name__}"
        hook_info = self._import_hook(
            connection_type=None,
            provider_info=None,
            hook_class_name=hook_class_name,
            package_name=package_name,
        )
        self._hook_provider_dict[hook_info.connection_type] = HookClassProvider(
            hook_class_name=hook_class_name, package_name=package_name
        )
        self._hooks_lazy_dict[hook_info.connection_type] = hook_info

def exec_ssh_client_command(self, ssh_client, command):
    warnings.warn(
        "exec_ssh_client_command method on SSHOperator is deprecated, call "
        "`ssh_hook.exec_ssh_client_command` instead",
        AirflowProviderDeprecationWarning,
    )
    return self.hook.exec_ssh_client_command(
        ssh_client, command, timeout=self.cmd_timeout, environment=self.environment, get_pty=self.get_pty
    )

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
            AirflowProviderDeprecationWarning,
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

def __init__(self, cron, timezone):
    self._expression = cron_presets.get(cron, cron)
    if isinstance(timezone, str):
        timezone = Timezone(timezone)
    self._timezone = timezone
    descriptor = ExpressionDescriptor(
        expression=self._expression, casing_type=CasingTypeEnum.Sentence, use_24hour_time_format=True
    )
    try:
        if len(croniter(self._expression).expanded) > 5:
            raise FormatException()
        interval_description = descriptor.get_description()
    except (CroniterBadCronError, FormatException, MissingFieldException):
        interval_description = ""
    self.description = interval_description

def check_correctness_of_list_of_sensors_operators_hook_trigger_modules(
    yaml_files
):
    num_errors = 0
    num_modules = 0
    for (yaml_file_path, provider_data), resource_type in itertools.product(
        yaml_files.items(), ["sensors", "operators", "hooks", "triggers"]
    ):
        expected_modules, provider_package, resource_data = parse_module_data(
            provider_data, resource_type, yaml_file_path
        )
        expected_modules = {module for module in expected_modules if module not in DEPRECATED_MODULES}
        current_modules = {str(i) for r in resource_data for i in r.get("python-modules", [])}
        num_modules += len(current_modules)
        num_errors += check_if_objects_exist_and_belong_to_package(
            current_modules, provider_package, yaml_file_path, resource_type, ObjectType.MODULE
        )
        try:
            package_name = os.fspath(ROOT_DIR.joinpath(yaml_file_path).parent.relative_to(ROOT_DIR)).replace(
                "/", "."
            )
            assert_sets_equal(
                set(expected_modules),
                f"Found list of {resource_type} modules in provider package: {package_name}",
                set(current_modules),
                f"Currently configured list of {resource_type} modules in {yaml_file_path}",
                extra_message="[yellow]Additional check[/]: If there are deprecated modules in the list,"
                "please add them to DEPRECATED_MODULES in "
                f"{pathlib.Path(__file__).relative_to(ROOT_DIR)}[/]",
            )
        except AssertionError as ex:
            nested_error = textwrap.indent(str(ex), "  ")
            errors.append(
                f"Incorrect content of key '{resource_type}/python-modules' "
                f"in file: {yaml_file_path}\n{nested_error}"
            )
            num_errors += 1
    return num_modules, num_errors

def generate_back_references(link, base_path):
    is_downloaded, file_name = download_file(link)
    if not is_downloaded:
        old_to_new = []
    else:
        get_console().print(f"Constructs old to new mapping from redirects.txt for {base_path}")
        old_to_new = construct_old_to_new_tuple_mapping(file_name)
    old_to_new.append(("index.html", "changelog.html"))
    old_to_new.append(("index.html", "security.html"))
    old_to_new.append(("security.html", "security/security-model.html"))
    for versioned_provider_path in (p for p in base_path.iterdir() if p.is_dir()):
        get_console().print(f"Processing {base_path}, version: {versioned_provider_path.name}")
        for old, new in old_to_new:
            if (versioned_provider_path / old).exists():
                if "/" in new:
                    split_new_path, file_name = new.rsplit("/", 1)
                    dest_dir = versioned_provider_path / split_new_path
                else:
                    file_name = new
                    dest_dir = versioned_provider_path
                relative_path = os.path.relpath(old, new)
                relative_path = relative_path.replace("../", "", 1)
                os.makedirs(dest_dir, exist_ok=True)
                dest_file_path = dest_dir / file_name
                create_back_reference_html(relative_path, dest_file_path)

def render_content(self, *, tags, header_separator = DEFAULT_HEADER_SEPARATOR):
    raise NotImplementedError("Tou need to override render_content method.")

def triggerer(args):
    settings.MASK_SECRETS_IN_LOGS = True
    print(settings.HEADER)
    triggerer_heartrate = conf.getfloat("triggerer", "JOB_HEARTBEAT_SEC")
    triggerer_job_runner = TriggererJobRunner(job=Job(heartrate=triggerer_heartrate), capacity=args.capacity)
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
                run_job(job=triggerer_job_runner.job, execute_callable=triggerer_job_runner._execute)
    else:
        signal.signal(signal.SIGINT, sigint_handler)
        signal.signal(signal.SIGTERM, sigint_handler)
        signal.signal(signal.SIGQUIT, sigquit_handler)
        with _serve_logs(args.skip_serve_logs):
            run_job(job=triggerer_job_runner.job, execute_callable=triggerer_job_runner._execute)

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
    self.subdir = subdir
    self.num_runs = num_runs
    self.num_times_parse_dags = num_times_parse_dags
    if processor_poll_interval:
        warnings.warn(
            "The 'processor_poll_interval' parameter is deprecated. "
            "Please use 'scheduler_idle_sleep_time'.",
            RemovedInAirflow3Warning,
            stacklevel=2,
        )
        scheduler_idle_sleep_time = processor_poll_interval
    self._scheduler_idle_sleep_time = scheduler_idle_sleep_time
    self._zombie_threshold_secs = conf.getint("scheduler", "scheduler_zombie_task_threshold")
    self._standalone_dag_processor = conf.getboolean("scheduler", "standalone_dag_processor")
    self._dag_stale_not_seen_duration = conf.getint("scheduler", "dag_stale_not_seen_duration")
    stalled_task_timeout = conf.getfloat("celery", "stalled_task_timeout", fallback=0)
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
    self._task_queued_timeout = max(
        stalled_task_timeout, task_adoption_timeout, worker_pods_pending_timeout, task_queued_timeout
    )
    self.do_pickle = do_pickle
    if log:
        self._log = log
    sql_conn = conf.get_mandatory_value("database", "sql_alchemy_conn").lower()
    self.using_sqlite = sql_conn.startswith("sqlite")
    self.processor_agent = None
    self.dagbag = DagBag(dag_folder=self.subdir, read_dags_from_db=True, load_op_links=False)
    self._paused_dag_without_running_dagruns = set()

def _read(
    self, ti, try_number, metadata = None
):
    if not metadata:
        metadata = {"offset": 0}
    if "offset" not in metadata:
        metadata["offset"] = 0
    offset = metadata["offset"]
    log_id = self._render_log_id(ti, try_number)
    logs = self.es_read(log_id, offset, metadata)
    logs_by_host = self._group_logs_by_host(logs)
    next_offset = offset if not logs else attrgetter(self.offset_field)(logs[-1])
    metadata["offset"] = str(next_offset)
    metadata["end_of_log"] = False
    for logs in logs_by_host.values():
        if logs[-1].message == self.end_of_log_mark:
            metadata["end_of_log"] = True
    cur_ts = pendulum.now()
    if "last_log_timestamp" in metadata:
        last_log_ts = timezone.parse(metadata["last_log_timestamp"])
        if int(next_offset) == 0 and cur_ts.diff(last_log_ts).in_seconds() > 5:
            metadata["end_of_log"] = True
            missing_log_message = (
                f"*** Log {log_id} not found in Elasticsearch. "
                "If your task started recently, please wait a moment and reload this page. "
                "Otherwise, the logs for this task instance may have been removed."
            )
            return [("", missing_log_message)], metadata
        if (
            cur_ts.diff(last_log_ts).in_minutes() >= 5
            or ("max_offset" in metadata and int(offset) >= int(metadata["max_offset"]))
        ):
            metadata["end_of_log"] = True
    if int(offset) != int(next_offset) or "last_log_timestamp" not in metadata:
        metadata["last_log_timestamp"] = str(cur_ts)
    def concat_logs(lines):
        log_range = (len(lines) - 1) if lines[-1].message == self.end_of_log_mark else len(lines)
        return "\n".join(self._format_msg(lines[i]) for i in range(log_range))
    message = [(host, concat_logs(hosted_log)) for host, hosted_log in logs_by_host.items()]
    return message, metadata

def create_timetable(interval, timezone):
    if interval is NOTSET:
        return DeltaDataIntervalTimetable(DEFAULT_SCHEDULE_INTERVAL)
    if interval is None:
        return NullTimetable()
    if interval == "@once":
        return OnceTimetable()
    if interval == "@continuous":
        return ContinuousTimetable()
    if isinstance(interval, (timedelta, relativedelta)):
        return DeltaDataIntervalTimetable(interval)
    if isinstance(interval, str):
        return CronDataIntervalTimetable(interval, timezone)
    raise ValueError(f"{interval!r} is not a valid schedule_interval.")

def iter_mapped_task_groups(self):
    parent = self.task_group
    while parent is not None:
        if isinstance(parent, MappedTaskGroup):
            yield parent
        parent = parent.task_group

def connections_export(args):
    file_formats = [".yaml", ".json", ".env"]
    if args.format:
        warnings.warn("Option `--format` is deprecated.  Use `--file-format` instead.", DeprecationWarning)
    if args.format and args.file_format:
        raise SystemExit("Option `--format` is deprecated.  Use `--file-format` instead.")
    default_format = ".json"
    provided_file_format = None
    if args.format or args.file_format:
        provided_file_format = f".{(args.format or args.file_format).lower()}"
    with args.file as f:
        if file_is_stdout := is_stdout(f):
            filetype = provided_file_format or default_format
        elif provided_file_format:
            filetype = provided_file_format
        else:
            filetype = Path(args.file.name).suffix.lower()
            if filetype not in file_formats:
                raise SystemExit(
                    f"Unsupported file format. The file must have the extension {', '.join(file_formats)}."
                )
        if args.serialization_format and filetype != ".env":
            raise SystemExit("Option `--serialization-format` may only be used with file type `env`.")
        with create_session() as session:
            connections = session.scalars(select(Connection).order_by(Connection.conn_id)).all()
        msg = _format_connections(
            conns=connections,
            file_format=filetype,
            serialization_format=args.serialization_format or "uri",
        )
        f.write(msg)
    if file_is_stdout:
        print("\nConnections successfully exported.", file=sys.stderr)
    else:
        print(f"Connections successfully exported to {args.file.name}.")

def load_providers_configuration(self):
    log.debug("Loading providers configuration")
    from airflow.providers_manager import ProvidersManager
    self.restore_core_default_configuration()
    for provider, config in ProvidersManager().already_initialized_provider_configs:
        for provider_section, provider_section_content in config.items():
            provider_options = provider_section_content["options"]
            section_in_current_config = self.configuration_description.get(provider_section)
            if not section_in_current_config:
                self.configuration_description[provider_section] = deepcopy(provider_section_content)
                section_in_current_config = self.configuration_description.get(provider_section)
                section_in_current_config["source"] = f"default-{provider}"
                for option in provider_options:
                    section_in_current_config["options"][option]["source"] = f"default-{provider}"
            else:
                section_source = section_in_current_config.get("source", "Airflow's core package").split(
                    "default-"
                )[-1]
                raise AirflowConfigException(
                    f"The provider {provider} is attempting to contribute "
                    f"configuration section {provider_section} that "
                    f"has already been added before. The source of it: {section_source}."
                    "This is forbidden. A provider can only add new sections. It"
                    "cannot contribute options to existing sections or override other "
                    "provider's configuration.",
                    UserWarning,
                )
    self._default_values = create_default_config_parser(self.configuration_description)
    try:
        del self.sensitive_config_values
    except AttributeError:
        pass
    self._providers_configuration_loaded = True

def monitor_job(self, context):
    if not self.job_id:
        raise AirflowException("AWS Batch job - job_id was not found")
    try:
        job_desc = self.hook.get_job_description(self.job_id)
        job_definition_arn = job_desc["jobDefinition"]
        job_queue_arn = job_desc["jobQueue"]
        self.log.info(
            "AWS Batch job (%s) Job Definition ARN: %r, Job Queue ARN: %r",
            self.job_id,
            job_definition_arn,
            job_queue_arn,
        )
    except KeyError:
        self.log.warning("AWS Batch job (%s) can't get Job Definition ARN and Job Queue ARN", self.job_id)
    else:
        BatchJobDefinitionLink.persist(
            context=context,
            operator=self,
            region_name=self.hook.conn_region_name,
            aws_partition=self.hook.conn_partition,
            job_definition_arn=job_definition_arn,
        )
        BatchJobQueueLink.persist(
            context=context,
            operator=self,
            region_name=self.hook.conn_region_name,
            aws_partition=self.hook.conn_partition,
            job_queue_arn=job_queue_arn,
        )
    if self.awslogs_enabled:
        if self.waiters:
            self.waiters.wait_for_job(self.job_id, get_batch_log_fetcher=self._get_batch_log_fetcher)
        else:
            self.hook.wait_for_job(self.job_id, get_batch_log_fetcher=self._get_batch_log_fetcher)
    else:
        if self.waiters:
            self.waiters.wait_for_job(self.job_id)
        else:
            self.hook.wait_for_job(self.job_id)
    awslogs = self.hook.get_job_all_awslogs_info(self.job_id)
    if awslogs:
        self.log.info("AWS Batch job (%s) CloudWatch Events details found. Links to logs:", self.job_id)
        link_builder = CloudWatchEventsLink()
        for log in awslogs:
            self.log.info(link_builder.format_link(**log))
        if len(awslogs) > 1:
            self.log.warning(
                "out of all those logs, we can only link to one in the UI. Using the first one."
            )
        CloudWatchEventsLink.persist(
            context=context,
            operator=self,
            region_name=self.hook.conn_region_name,
            aws_partition=self.hook.conn_partition,
            **awslogs[0],
        )
    self.hook.check_job_success(self.job_id)
    self.log.info("AWS Batch job (%s) succeeded", self.job_id)

def _maybe_empty_lines(self, current_line):
    max_allowed = 1
    if current_line.depth == 0:
        max_allowed = 1 if self.mode.is_pyi else 2
    if current_line.leaves:
        first_leaf = current_line.leaves[0]
        before = first_leaf.prefix.count("\n")
        before = min(before, max_allowed)
        first_leaf.prefix = ""
    else:
        before = 0
    depth = current_line.depth
    while self.previous_defs and self.previous_defs[-1].depth >= depth:
        if self.mode.is_pyi:
            assert self.previous_line is not None
            if depth and not current_line.is_def and self.previous_line.is_def:
                before = min(1, before)
            elif (
                Preview.blank_line_after_nested_stub_class in self.mode
                and self.previous_defs[-1].is_class
                and not self.previous_defs[-1].is_stub_class
            ):
                before = 1
            elif depth:
                before = 0
            else:
                before = 1
        else:
            if depth:
                before = 1
            elif (
                not depth
                and self.previous_defs[-1]
                and current_line.leaves[-1].type == token.COLON
                and (
                    current_line.leaves[0].value
                    not in ("with", "try", "for", "while", "if", "match")
                )
            ):
                before = 1
            else:
                before = 2
        self.previous_defs.pop()
    if current_line.is_decorator or current_line.is_def or current_line.is_class:
        return self._maybe_empty_lines_for_class_or_def(current_line, before)
    if (
        self.previous_line
        and self.previous_line.is_import
        and not current_line.is_import
        and not current_line.is_fmt_pass_converted(first_leaf_matches=is_import)
        and depth == self.previous_line.depth
    ):
        return (before or 1), 0
    if (
        self.previous_line
        and self.previous_line.is_class
        and current_line.is_triple_quoted_string
    ):
        return before, 1
    if self.previous_line and self.previous_line.opens_block:
        return 0, 0
    return before, 0

def blackify(base_branch, black_command, logger):
    current_branch = git("branch", "--show-current")
    if not current_branch or base_branch == current_branch:
        logger.error("You need to check out a feature branch to work on")
        return 1
    if not os.path.exists(".git"):
        logger.error("Run me in the root of your repo")
        return 1
    merge_base = git("merge-base", "HEAD", base_branch)
    if not merge_base:
        logger.error(
            "Could not find a common commit for current head and %s" % base_branch
        )
        return 1
    commits = git(
        "log", "--reverse", "--pretty=format:%H", "%s~1..HEAD" % merge_base
    ).split()
    for commit in commits:
        git("checkout", commit, "-b%s-black" % commit)
        check_output(black_command, shell=True)
        git("commit", "-aqm", "blackify")
    git("checkout", base_branch, "-b%s-black" % current_branch)
    for last_commit, commit in zip(commits, commits[1:]):
        allow_empty = (
            b"--allow-empty" in run(["git", "apply", "-h"], stdout=PIPE).stdout
        )
        quiet = b"--quiet" in run(["git", "apply", "-h"], stdout=PIPE).stdout
        git_diff = Popen(
            [
                "git",
                "diff",
                "--find-copies",
                "%s-black..%s-black" % (last_commit, commit),
            ],
            stdout=PIPE,
        )
        git_apply = Popen(
            [
                "git",
                "apply",
            ]
            + (["--quiet"] if quiet else [])
            + [
                "-3",
                "--intent-to-add",
            ]
            + (["--allow-empty"] if allow_empty else [])
            + [
                "-",
            ],
            stdin=git_diff.stdout,
        )
        if git_diff.stdout is not None:
            git_diff.stdout.close()
        git_apply.communicate()
        git("commit", "--allow-empty", "-aqC", commit)
    for commit in commits:
        git("branch", "-qD", "%s-black" % commit)
    return 0

def _format_str_once(src_contents, *, mode):
    src_node = lib2to3_parse(src_contents.lstrip(), mode.target_versions)
    dst_contents = []
    future_imports = get_future_imports(src_node)
    if mode.target_versions:
        versions = mode.target_versions
    else:
        versions = detect_target_versions(src_node, future_imports=future_imports)
    normalize_fmt_off(src_node, preview=mode.preview)
    lines = LineGenerator(mode=mode)
    elt = EmptyLineTracker(is_pyi=mode.is_pyi)
    empty_line = Line(mode=mode)
    after = 0
    split_line_features = {
        feature
        for feature in {Feature.TRAILING_COMMA_IN_CALL, Feature.TRAILING_COMMA_IN_DEF}
        if supports_feature(versions, feature)
    }
    for current_line in lines.visit(src_node):
        dst_contents.append(str(empty_line) * after)
        before, after = elt.maybe_empty_lines(current_line)
        dst_contents.append(str(empty_line) * before)
        for line in transform_line(
            current_line, mode=mode, features=split_line_features
        ):
            dst_contents.append(str(line))
    return "".join(dst_contents)

def blackify(base_branch, black_command, logger):
    current_branch = git("branch", "--show-current")
    if not current_branch or base_branch == current_branch:
        logger.error("You need to check out a feature brach to work on")
        return 1
    if not os.path.exists(".git"):
        logger.error("Run me in the root of your repo")
        return 1
    merge_base = git("merge-base", "HEAD", base_branch)
    if not merge_base:
        logger.error(
            "Could not find a common commit for current head and %s" % base_branch
        )
        return 1
    commits = git(
        "log", "--reverse", "--pretty=format:%H", "%s~1..HEAD" % merge_base
    ).split()
    for commit in commits:
        git("checkout", commit, "-b%s-black" % commit)
        check_output(black_command, shell=True)
        git("commit", "-aqm", "blackify")
    git("checkout", base_branch, "-b%s-black" % current_branch)
    for last_commit, commit in zip(commits, commits[1:]):
        allow_empty = (
            b"--allow-empty" in run(["git", "apply", "-h"], stdout=PIPE).stdout
        )
        quiet = b"--quiet" in run(["git", "apply", "-h"], stdout=PIPE).stdout
        git_diff = Popen(
            [
                "git",
                "diff",
                "--find-copies",
                "%s-black..%s-black" % (last_commit, commit),
            ],
            stdout=PIPE,
        )
        git_apply = Popen(
            [
                "git",
                "apply",
            ]
            + (["--quiet"] if quiet else [])
            + [
                "-3",
                "--intent-to-add",
            ]
            + (["--allow-empty"] if allow_empty else [])
            + [
                "-",
            ],
            stdin=git_diff.stdout,
        )
        if git_diff.stdout is not None:
            git_diff.stdout.close()
        git_apply.communicate()
        git("commit", "--allow-empty", "-aqC", commit)
    for commit in commits:
        git("branch", "-qD", "%s-black" % commit)
    return 0

def assert_equivalent(src, dst, *, pass_num = 1):
    try:
        src_ast = parse_ast(src)
    except Exception as exc:
        raise AssertionError(
            f"cannot use --safe with this file; failed to parse source file: {exc}"
        ) from exc
    try:
        dst_ast = parse_ast(dst)
    except Exception as exc:
        log = dump_to_file("".join(traceback.format_tb(exc.__traceback__)), dst)
        raise AssertionError(
            f"INTERNAL ERROR: Black produced invalid code on pass {pass_num}: {exc}. "
            "Please report a bug on https://github.com/psf/black/issues.  "
            f"This invalid output might be helpful: {log}"
        ) from None
    src_ast_str = "\n".join(stringify_ast(src_ast))
    dst_ast_str = "\n".join(stringify_ast(dst_ast))
    if src_ast_str != dst_ast_str:
        log = dump_to_file(diff(src_ast_str, dst_ast_str, "src", "dst"))
        raise AssertionError(
            "INTERNAL ERROR: Black produced code that is not equivalent to the"
            f" source on pass {pass_num}.  Please report a bug on "
            f"https://github.com/psf/black/issues.  This diff might be helpful: {log}"
        ) from None

def stack_copy(
    stack
):
    return [(copy.deepcopy(dfa), label, DUMMY_NODE) for dfa, label, _ in stack]

def matches_grammar(src_txt, grammar):
    drv = driver.Driver(grammar)
    try:
        drv.parse_string(src_txt, True)
    except ParseError:
        return False
    else:
        return True

def visit_Assign(self, node):
    if isinstance(node.value, ast.Call) and _is_ipython_magic(node.value.func):
        args = _get_str_args(node.value.args)
        if node.value.func.attr == "getoutput":
            src = f"!{args[0]}"
        elif node.value.func.attr == "run_line_magic":
            src = f"%{args[0]}"
            if args[1]:
                src += f" {args[1]}"
        else:
            raise AssertionError(
                "Unexpected IPython magic {node.value.func.attr!r} found. "
                "Please report a bug on https://github.com/psf/black/issues."
            ) from None
        self.magics[node.value.lineno].append(
            OffsetAndMagic(node.value.col_offset, src)
        )
    self.generic_visit(node)

def format_str(src_contents, *, mode):
    src_node = lib2to3_parse(src_contents.lstrip(), mode.target_versions)
    dst_contents = []
    future_imports = get_future_imports(src_node)
    if mode.target_versions:
        versions = mode.target_versions
    else:
        versions = detect_target_versions(src_node)
    if TargetVersion.PY27 in mode.target_versions or versions == {TargetVersion.PY27}:
        msg = (
            "DEPRECATION: Python 2 support will be removed in the first stable release"
            "expected in January 2022."
        )
        err(msg, fg="yellow", bold=True)
    normalize_fmt_off(src_node)
    lines = LineGenerator(
        mode=mode,
        remove_u_prefix="unicode_literals" in future_imports
        or supports_feature(versions, Feature.UNICODE_LITERALS),
    )
    elt = EmptyLineTracker(is_pyi=mode.is_pyi)
    empty_line = Line(mode=mode)
    after = 0
    split_line_features = {
        feature
        for feature in {Feature.TRAILING_COMMA_IN_CALL, Feature.TRAILING_COMMA_IN_DEF}
        if supports_feature(versions, feature)
    }
    for current_line in lines.visit(src_node):
        dst_contents.append(str(empty_line) * after)
        before, after = elt.maybe_empty_lines(current_line)
        dst_contents.append(str(empty_line) * before)
        for line in transform_line(
            current_line, mode=mode, features=split_line_features
        ):
            dst_contents.append(str(line))
    return "".join(dst_contents)

def path_empty(
    src, msg, quiet, verbose, ctx
):
    if not src and (verbose or not quiet):
        out(msg)
        ctx.exit(0)

def test_idempotent_any_syntatically_valid_python(
    src_contents, mode
):
    compile(src_contents, "<string>", "exec")  
    try:
        dst_contents = black.format_str(src_contents, mode=mode)
    except black.InvalidInput:
        return
    except TokenError as e:
        if (
            e.args[0] == "EOF in multi-line statement"
            and re.search(r"\r?\n\\\r?\n", src_contents) is not None
        ):
            return
        raise
    black.assert_equivalent(src_contents, dst_contents)
    black.assert_stable(src_contents, dst_contents, mode=mode)

def format_file_in_place(
    src,
    fast,
    mode,
    write_back = WriteBack.NO,
    lock = None,  
):
    if src.suffix == ".pyi":
        mode = replace(mode, is_pyi=True)
    then = datetime.utcfromtimestamp(src.stat().st_mtime)
    with open(src, "rb") as buf:
        src_contents, encoding, newline = decode_bytes(buf.read())
    try:
        dst_contents = format_file_contents(src_contents, fast=fast, mode=mode)
    except NothingChanged:
        return False
    if write_back == WriteBack.YES:
        with open(src, "w", encoding=encoding, newline=newline) as f:
            f.write(dst_contents)
    elif write_back in (WriteBack.DIFF, WriteBack.COLOR_DIFF):
        now = datetime.utcnow()
        src_name = f"{src}\t{then} +0000"
        dst_name = f"{src}\t{now} +0000"
        diff_contents = diff(src_contents, dst_contents, src_name, dst_name)
        if write_back == write_back.COLOR_DIFF:
            diff_contents = color_diff(diff_contents)
        with lock or nullcontext():
            f = io.TextIOWrapper(
                sys.stdout.buffer,
                encoding=encoding,
                newline=newline,
                write_through=True,
            )
            f = wrap_stream_for_windows(f)
            f.write(diff_contents)
            f.detach()
    return True

def can_omit_invisible_parens(
    line,
    line_length,
    omit_on_explode = (),
):
    bt = line.bracket_tracker
    if not bt.delimiters:
        return True
    max_priority = bt.max_delimiter_priority()
    if bt.delimiter_count_with_priority(max_priority) > 1:
        return False
    if max_priority == DOT_PRIORITY:
        return True
    assert len(line.leaves) >= 2, "Stranded delimiter"
    first = line.leaves[0]
    second = line.leaves[1]
    if first.type in OPENING_BRACKETS and second.type not in CLOSING_BRACKETS:
        if _can_omit_opening_paren(line, first=first, line_length=line_length):
            return True
    penultimate = line.leaves[-2]
    last = line.leaves[-1]
    if line.magic_trailing_comma:
        try:
            penultimate, last = last_two_except(line.leaves, omit=omit_on_explode)
        except LookupError:
            return False
    if (
        last.type == token.RPAR
        or last.type == token.RBRACE
        or (
            last.type == token.RSQB
            and last.parent
            and last.parent.type != syms.trailer
        )
    ):
        if penultimate.type in OPENING_BRACKETS:
            return False
        if is_multiline_string(first):
            return True
        if penultimate.type == token.COMMA:
            return True
        if _can_omit_closing_paren(line, last=last, line_length=line_length):
            return True
    return False

def transform_line(
    line, mode, features = ()
):
    if line.is_comment:
        yield line
        return
    line_str = line_to_string(line)
    def init_st(ST):
        return ST(mode.line_length, mode.string_normalization)
    string_merge = init_st(StringMerger)
    string_paren_strip = init_st(StringParenStripper)
    string_split = init_st(StringSplitter)
    string_paren_wrap = init_st(StringParenWrapper)
    if (
        not line.contains_uncollapsable_type_comments()
        and not (line.should_split or line.magic_trailing_comma)
        and (
            is_line_short_enough(line, line_length=mode.line_length, line_str=line_str)
            or line.contains_unsplittable_type_ignore()
        )
        and not (line.inside_brackets and line.contains_standalone_comments())
    ):
        if mode.experimental_string_processing:
            transformers = [string_merge, string_paren_strip]
        else:
            transformers = []
    elif line.is_def:
        transformers = [left_hand_split]
    else:
        def rhs(line, features):
            for omit in generate_trailers_to_omit(line, mode.line_length):
                lines = list(
                    right_hand_split(line, mode.line_length, features, omit=omit)
                )
                if is_line_short_enough(lines[0], line_length=mode.line_length):
                    yield from lines
                    return
            yield from right_hand_split(
                line, line_length=mode.line_length, features=features
            )
        if mode.experimental_string_processing:
            if line.inside_brackets:
                transformers = [
                    string_merge,
                    string_paren_strip,
                    string_split,
                    delimiter_split,
                    standalone_comment_split,
                    string_paren_wrap,
                    rhs,
                ]
            else:
                transformers = [
                    string_merge,
                    string_paren_strip,
                    string_split,
                    string_paren_wrap,
                    rhs,
                ]
        else:
            if line.inside_brackets:
                transformers = [delimiter_split, standalone_comment_split, rhs]
            else:
                transformers = [rhs]
    for transform in transformers:
        try:
            result = run_transformer(line, transform, mode, features, line_str=line_str)
        except CannotTransform:
            continue
        else:
            yield from result
            break
    else:
        yield line

def generate_trailers_to_omit(line, line_length):
    omit = set()
    if not line.should_split and not line.magic_trailing_comma:
        yield omit
    length = 4 * line.depth
    opening_bracket = None
    closing_bracket = None
    inner_brackets = set()
    for index, leaf, leaf_length in enumerate_with_length(line, reversed=True):
        length += leaf_length
        if length > line_length:
            break
        has_inline_comment = leaf_length > len(leaf.value) + len(leaf.prefix)
        if leaf.type == STANDALONE_COMMENT or has_inline_comment:
            break
        if opening_bracket:
            if leaf is opening_bracket:
                opening_bracket = None
            elif leaf.type in CLOSING_BRACKETS:
                prev = line.leaves[index - 1] if index > 0 else None
                if (
                    line.magic_trailing_comma
                    and prev
                    and prev.type == token.COMMA
                    and not is_one_tuple_between(
                        leaf.opening_bracket, leaf, line.leaves
                    )
                ):
                    break
                inner_brackets.add(id(leaf))
        elif leaf.type in CLOSING_BRACKETS:
            prev = line.leaves[index - 1] if index > 0 else None
            if prev and prev.type in OPENING_BRACKETS:
                inner_brackets.add(id(leaf))
                continue
            if closing_bracket:
                omit.add(id(closing_bracket))
                omit.update(inner_brackets)
                inner_brackets.clear()
                yield omit
            if (
                line.magic_trailing_comma
                and prev
                and prev.type == token.COMMA
                and not is_one_tuple_between(leaf.opening_bracket, leaf, line.leaves)
            ):
                break
            if leaf.value:
                opening_bracket = leaf.opening_bracket
                closing_bracket = leaf

def headers(self):
    try:
        raw_version = self._orig.raw._original_response.version
    except AttributeError:
        raw_version = 11
    version = {
        9: '0.9',
        10: '1.0',
        11: '1.1',
        20: '2',
    }[raw_version]
    original = self._orig
    status_line = f'HTTP/{version} {original.status_code} {original.reason}'
    headers = [status_line]
    headers.extend(
        ': '.join(header)
        for header in original.headers.items()
        if header[0] != 'Set-Cookie'
    )
    headers.extend(
        f'Set-Cookie: {cookie}'
        for header, value in original.headers.items()
        for cookie in split_cookies(value)
        if header == 'Set-Cookie'
    )
    return '\r\n'.join(headers)

def upgrade_session(env, args, hostname, session_name):
    session = get_httpie_session(
        env=env,
        config_dir=env.config.directory,
        session_name=session_name,
        host=hostname,
        url=hostname,
        refactor_mode=True
    )
    session_name = session.path.stem
    if session.is_new():
        env.log_error(f'{session_name!r} (for {hostname!r}) does not exist.')
        return ExitStatus.ERROR
    fixers = [
        fixer
        for version, fixer in FIXERS_TO_VERSIONS.items()
        if is_version_greater(version, session.version)
    ]
    if len(fixers) == 0:
        env.stdout.write(f'{session_name!r} (for {hostname!r}) is already up-to-date.\n')
        return ExitStatus.SUCCESS
    for fixer in fixers:
        fixer(session, hostname, args)
    session.save(bump_version=True)
    env.stdout.write(f'Refactored {session_name!r} (for {hostname!r}) to the version {session.version}.\n')
    return ExitStatus.SUCCESS

def error(self, message):
    self.print_usage(sys.stderr)
    self.exit(
        2,
        dedent(
            f'''
                error:
                    {message}

                For more information:
                    - Try running {self.prog} --help
                    - Or visiting https://httpie.io/docs/cli
                '''
        )
    )

def convert(self, content_bytes):
    raise NotImplementedError

def program(args, env):
    exit_status = ExitStatus.SUCCESS
    downloader = None
    initial_request = None
    final_response = None
    def separate():
        getattr(env.stdout, 'buffer', env.stdout).write(MESSAGE_SEPARATOR_BYTES)
    def request_body_read_callback(chunk):
        should_pipe_to_stdout = bool(
            OUT_REQ_BODY in args.output_options
            and initial_request
            and chunk
        )
        if should_pipe_to_stdout:
            msg = requests.PreparedRequest()
            msg.is_body_upload_chunk = True
            msg.body = chunk
            msg.headers = initial_request.headers
            write_message(requests_message=msg, env=env, args=args, with_body=True, with_headers=False)
    try:
        if args.download:
            args.follow = True  
            downloader = Downloader(output_file=args.output_file, progress_file=env.stderr, resume=args.download_resume)
            downloader.pre_request(args.headers)
        messages = collect_messages(args=args, config_dir=env.config.directory,
                                    request_body_read_callback=request_body_read_callback)
        force_separator = False
        prev_with_body = False
        for message in messages:
            is_request = isinstance(message, requests.PreparedRequest)
            with_headers, with_body = get_output_options(args=args, message=message)
            do_write_body = with_body
            if prev_with_body and (with_headers or with_body) and (force_separator or not env.stdout_isatty):
                separate()
            force_separator = False
            if is_request:
                if not initial_request:
                    initial_request = message
                if with_body:
                    is_streamed_upload = not isinstance(message.body, (str, bytes))
                    do_write_body = not is_streamed_upload
                    force_separator = is_streamed_upload and env.stdout_isatty
            else:
                final_response = message
                if args.check_status or downloader:
                    exit_status = http_status_to_exit_status(http_status=message.status_code, follow=args.follow)
                    if exit_status != ExitStatus.SUCCESS and (not env.stdout_isatty or args.quiet):
                        env.log_error(f'HTTP {message.raw.status} {message.raw.reason}', level='warning')
            write_message(requests_message=message, env=env, args=args, with_headers=with_headers,
                          with_body=do_write_body)
            prev_with_body = with_body
        if force_separator:
            separate()
        if downloader and exit_status == ExitStatus.SUCCESS:
            download_stream, download_to = downloader.start(
                initial_url=initial_request.url,
                final_response=final_response,
            )
            write_stream(stream=download_stream, outfile=download_to, flush=False)
            downloader.finish()
            if downloader.interrupted:
                exit_status = ExitStatus.ERROR
                env.log_error(
                    f'Incomplete download: size={downloader.status.total_size};'
                    f' downloaded={downloader.status.downloaded}'
                )
        return exit_status
    finally:
        if downloader and not downloader.finished:
            downloader.failed()
        if not isinstance(args, list) and args.output_file and args.output_file_specified:
            args.output_file.close()

def parse_format_options(s, defaults):
    value_map = {
        'true': True,
        'false': False,
    }
    options = deepcopy(defaults or {})
    for option in s.split(','):
        try:
            path, value = option.lower().split('=')
            section, key = path.split('.')
        except ValueError:
            raise argparse.ArgumentTypeError(
                f'--format-options: invalid option: {option!r}')
        if value in value_map:
            parsed_value = value_map[value]
        else:
            if value.isnumeric():
                parsed_value = int(value)
            else:
                parsed_value = value
        if defaults is None:
            options.setdefault(section, {})
        else:
            try:
                default_value = defaults[section][key]
            except KeyError:
                raise argparse.ArgumentTypeError(
                    f'--format-options: invalid key: {path!r} in {option!r}')
            default_type, parsed_type = type(default_value), type(parsed_value)
            if parsed_type is not default_type:
                raise argparse.ArgumentTypeError(
                    '--format-options: invalid value type:'
                    f' {value!r} in {option!r}'
                    f' (expected {default_type.__name__}'
                    f' got {parsed_type.__name__})'
                )
        options[section][key] = parsed_value
    return options

def main(
    args = sys.argv,
    env=Environment(),
):
    program_name, *args = args
    env.program_name = os.path.basename(program_name)
    args = decode_raw_args(args, env.stdin_encoding)
    plugin_manager.load_installed_plugins()
    from httpie.cli.definition import parser
    if env.config.default_options:
        args = env.config.default_options + args
    include_debug_info = '--debug' in args
    include_traceback = include_debug_info or '--traceback' in args
    if include_debug_info:
        print_debug_info(env)
        if args == ['--debug']:
            return ExitStatus.SUCCESS
    exit_status = ExitStatus.SUCCESS
    try:
        parsed_args = parser.parse_args(
            args=args,
            env=env,
        )
    except KeyboardInterrupt:
        env.stderr.write('\n')
        if include_traceback:
            raise
        exit_status = ExitStatus.ERROR_CTRL_C
    except SystemExit as e:
        if e.code != ExitStatus.SUCCESS:
            env.stderr.write('\n')
            if include_traceback:
                raise
            exit_status = ExitStatus.ERROR
    else:
        try:
            exit_status = program(
                args=parsed_args,
                env=env,
            )
        except KeyboardInterrupt:
            env.stderr.write('\n')
            if include_traceback:
                raise
            exit_status = ExitStatus.ERROR_CTRL_C
        except SystemExit as e:
            if e.code != ExitStatus.SUCCESS:
                env.stderr.write('\n')
                if include_traceback:
                    raise
                exit_status = ExitStatus.ERROR
        except requests.Timeout:
            exit_status = ExitStatus.ERROR_TIMEOUT
            env.log_error(f'Request timed out ({parsed_args.timeout}s).')
        except requests.TooManyRedirects:
            exit_status = ExitStatus.ERROR_TOO_MANY_REDIRECTS
            env.log_error(
                f'Too many redirects'
                f' (--max-redirects=parsed_args.max_redirects).'
            )
        except Exception as e:
            msg = str(e)
            if hasattr(e, 'request'):
                request = e.request
                if hasattr(request, 'url'):
                    msg = (
                        f'{msg} while doing a {request.method}'
                        f' request to URL: {request.url}'
                    )
            env.log_error(f'{type(e).__name__}: {msg}')
            if include_traceback:
                raise
            exit_status = ExitStatus.ERROR
    return exit_status

def _body_from_file(self, fd):
    if self.args.data:
        self.error('Request body (from stdin or a file) and request '
                   'data (key=value) cannot be mixed. Pass '
                   '--ignore-stdin to let key/value take priority. '
                   'See https://httpie.org/doc#scripting for details.')
    self.args.data = getattr(fd, 'buffer', fd).read()

def auth(self, auth):
    assert set(['type', 'raw_auth']) == set(auth.keys())
    self['auth'] = auth

def _body_from_file(self, fd):
    if self.args.data:
        self.error('Request body (from stdin or a file) and request '
                   'data (key=value) cannot be mixed.')
    self.args.data = getattr(fd, 'buffer', fd).read()

def get_requests_kwargs(args, base_headers=None):
    data = args.data
    auto_json = data and not args.form
    if (args.json or auto_json) and isinstance(data, dict):
        if data:
            data = json.dumps(data)
        else:
            data = ''
    headers = get_default_headers(args)
    if base_headers:
        headers.update(base_headers)
    headers.update(args.headers)
    headers = finalize_headers(headers)
    cert = None
    if args.cert:
        cert = args.cert
        if args.cert_key:
            cert = cert, args.cert_key
    kwargs = {
        'stream': True,
        'method': args.method.lower(),
        'url': args.url,
        'headers': headers,
        'data': data,
        'verify': {
            'yes': True,
            'no': False
        }.get(args.verify, args.verify),
        'cert': cert,
        'timeout': args.timeout,
        'auth': args.auth,
        'proxies': dict((p.key, p.value) for p in args.proxy),
        'files': args.files,
        'allow_redirects': args.follow,
        'params': args.params,
    }
    return kwargs

def format_body(self, body, mime):
    if 'json' in mime or self.kwargs['explicit_json']:
        try:
            obj = json.loads(body)
        except ValueError:
            pass  
        else:
            body = json.dumps(
                obj=obj,
                sort_keys=True,
                ensure_ascii=False,
                indent=DEFAULT_INDENT
            )
    return body

def get_filename_max_length(directory):
    try:
        max_len = os.pathconf(directory, 'PC_NAME_MAX')
    except OSError as e:
        if e.errno == errno.EINVAL:
            max_len = 255
        else:
            raise
    return max_len

def log_error(msg, *args, level='error'):
    msg = msg % args
    env.stderr.write('\nhttp: %s: %s\n' % (level, msg))

def finalize_options(self):
    TestCommand.finalize_options(self)
    self.test_suite = True
    self.test_args = [
        '--doctest-modules', '--verbose',
        './httpie', './tests'
    ]
    self.test_suite = True

def get_mkdocs_material_langs():
    material_path = Path(material.__file__).parent
    material_langs_path = material_path / "partials" / "languages"
    langs = [file.stem for file in material_langs_path.glob("*.html")]
    return langs

def get_graphql_response(
    *,
    settings,
    query,
    after = None,
    category_id = None,
):
    headers = {"Authorization": f"token {settings.input_token.get_secret_value()}"}
    variables = {"after": after, "category_id": category_id}
    response = httpx.post(
        github_graphql_url,
        headers=headers,
        timeout=settings.httpx_timeout,
        json={"query": query, "variables": variables, "operationName": "Q"},
    )
    if response.status_code != 200:
        logging.error(
            f"Response was not 200, after: {after}, category_id: {category_id}"
        )
        logging.error(response.text)
        raise RuntimeError(response.text)
    data = response.json()
    return data

def build_all():
    site_path = Path("site").absolute()
    update_languages(lang=None)
    current_dir = os.getcwd()
    os.chdir(en_docs_path)
    typer.echo("Building docs for: en")
    subprocess.run(["mkdocs", "build", "--site-dir", site_path], check=True)
    os.chdir(current_dir)
    langs = []
    for lang in get_lang_paths():
        if lang == en_docs_path or not lang.is_dir():
            continue
        langs.append(lang.name)
    cpu_count = os.cpu_count() or 1
    with Pool(cpu_count * 2) as p:
        p.map(build_lang, langs)

def get_model_definitions(
    *,
    flat_models,
    model_name_map,
):
    definitions = {}
    for model in flat_models:
        m_schema, m_definitions, m_nested_models = model_process_schema(
            model, model_name_map=model_name_map, ref_prefix=REF_PREFIX
        )
        definitions.update(m_definitions)
        model_name = model_name_map[model]
        definitions[model_name] = m_schema
    return definitions

def get_redoc_html(
    *,
    openapi_url,
    title,
    redoc_js_url = "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    redoc_favicon_url = "https://fastapi.tiangolo.com/img/favicon.png",
    with_google_fonts = True,
):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <title>{title}</title>
    <!-- needed for adaptive design -->
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    """
    if with_google_fonts:
        html += """
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    """
    html += f"""
    <link rel="shortcut icon" href="{redoc_favicon_url}">
    <!--
    ReDoc doesn't change outer page styles
    -->
    <style>
      body {{
        margin: 0;
        padding: 0;
      }}
    </style>
    </head>
    <body>
    <redoc spec-url="{openapi_url}"></redoc>
    <script src="{redoc_js_url}"> </script>
    </body>
    </html>
    """
    return HTMLResponse(html)

async def get_model(model_name):
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}
    return {"model_name": model_name, "message": "Have some residuals"}

def create_cloned_field(
    field,
    *,
    cloned_types = None,
):
    if cloned_types is None:
        cloned_types = dict()
    original_type = field.type_
    if is_dataclass(original_type) and hasattr(original_type, "__pydantic_model__"):
        original_type = original_type.__pydantic_model__
    use_type = original_type
    if lenient_issubclass(original_type, BaseModel):
        original_type = cast(Type[BaseModel], original_type)
        use_type = cloned_types.get(original_type)
        if use_type is None:
            use_type = create_model(original_type.__name__, __base__=original_type)
            cloned_types[original_type] = use_type
            for f in original_type.__fields__.values():
                use_type.__fields__[f.name] = create_cloned_field(
                    f, cloned_types=cloned_types
                )
    new_field = create_response_field(name=field.name, type_=use_type)
    new_field.has_alias = field.has_alias
    new_field.alias = field.alias
    new_field.class_validators = field.class_validators
    new_field.default = field.default
    new_field.required = field.required
    new_field.model_config = field.model_config
    new_field.field_info = field.field_info
    new_field.allow_none = field.allow_none
    new_field.validate_always = field.validate_always
    if field.sub_fields:
        new_field.sub_fields = [
            create_cloned_field(sub_field, cloned_types=cloned_types)
            for sub_field in field.sub_fields
        ]
    if field.key_field:
        new_field.key_field = create_cloned_field(
            field.key_field, cloned_types=cloned_types
        )
    new_field.validators = field.validators
    new_field.pre_validators = field.pre_validators
    new_field.post_validators = field.post_validators
    new_field.parse_json = field.parse_json
    new_field.shape = field.shape
    new_field.populate_validators()
    return new_field

def jsonable_encoder(
    obj,
    include = None,
    exclude = None,
    by_alias = True,
    exclude_unset = False,
    exclude_defaults = False,
    exclude_none = False,
    custom_encoder = None,
    sqlalchemy_safe = True,
):
    custom_encoder = custom_encoder or {}
    if custom_encoder:
        if type(obj) in custom_encoder:
            return custom_encoder[type(obj)](obj)
        else:
            for encoder_type, encoder_instance in custom_encoder.items():
                if isinstance(obj, encoder_type):
                    return encoder_instance(obj)
    if include is not None and not isinstance(include, (set, dict)):
        include = set(include)
    if exclude is not None and not isinstance(exclude, (set, dict)):
        exclude = set(exclude)
    if isinstance(obj, BaseModel):
        encoder = getattr(obj.__config__, "json_encoders", {})
        if custom_encoder:
            encoder.update(custom_encoder)
        obj_dict = obj.dict(
            include=include,  
            exclude=exclude,  
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_none=exclude_none,
            exclude_defaults=exclude_defaults,
        )
        if "__root__" in obj_dict:
            obj_dict = obj_dict["__root__"]
        return jsonable_encoder(
            obj_dict,
            exclude_none=exclude_none,
            exclude_defaults=exclude_defaults,
            custom_encoder=encoder,
            sqlalchemy_safe=sqlalchemy_safe,
        )
    if dataclasses.is_dataclass(obj):
        return dataclasses.asdict(obj)
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, PurePath):
        return str(obj)
    if isinstance(obj, (str, int, float, type(None))):
        return obj
    if isinstance(obj, dict):
        encoded_dict = {}
        allowed_keys = set(obj.keys())
        if include is not None:
            allowed_keys &= set(include)
        if exclude is not None:
            allowed_keys -= set(exclude)
        for key, value in obj.items():
            if (
                (
                    not sqlalchemy_safe
                    or (not isinstance(key, str))
                    or (not key.startswith("_sa"))
                )
                and (value is not None or not exclude_none)
                and key in allowed_keys
            ):
                encoded_key = jsonable_encoder(
                    key,
                    by_alias=by_alias,
                    exclude_unset=exclude_unset,
                    exclude_none=exclude_none,
                    custom_encoder=custom_encoder,
                    sqlalchemy_safe=sqlalchemy_safe,
                )
                encoded_value = jsonable_encoder(
                    value,
                    by_alias=by_alias,
                    exclude_unset=exclude_unset,
                    exclude_none=exclude_none,
                    custom_encoder=custom_encoder,
                    sqlalchemy_safe=sqlalchemy_safe,
                )
                encoded_dict[encoded_key] = encoded_value
        return encoded_dict
    if isinstance(obj, (list, set, frozenset, GeneratorType, tuple)):
        encoded_list = []
        for item in obj:
            encoded_list.append(
                jsonable_encoder(
                    item,
                    include=include,
                    exclude=exclude,
                    by_alias=by_alias,
                    exclude_unset=exclude_unset,
                    exclude_defaults=exclude_defaults,
                    exclude_none=exclude_none,
                    custom_encoder=custom_encoder,
                    sqlalchemy_safe=sqlalchemy_safe,
                )
            )
        return encoded_list
    if type(obj) in ENCODERS_BY_TYPE:
        return ENCODERS_BY_TYPE[type(obj)](obj)
    for encoder, classes_tuple in encoders_by_class_tuples.items():
        if isinstance(obj, classes_tuple):
            return encoder(obj)
    errors = []
    try:
        data = dict(obj)
    except Exception as e:
        errors.append(e)
        try:
            data = vars(obj)
        except Exception as e:
            errors.append(e)
            raise ValueError(errors)
    return jsonable_encoder(
        data,
        include=include,
        exclude=exclude,
        by_alias=by_alias,
        exclude_unset=exclude_unset,
        exclude_defaults=exclude_defaults,
        exclude_none=exclude_none,
        custom_encoder=custom_encoder,
        sqlalchemy_safe=sqlalchemy_safe,
    )

async def app(request):
    try:
        body = None
        if body_field:
            if is_body_form:
                body = await request.form()
            else:
                body_bytes = await request.body()
                if body_bytes:
                    json_body = Undefined
                    content_type_value = request.headers.get("content-type")
                    if not content_type_value:
                        json_body = await request.json()
                    else:
                        message = email.message.Message()
                        message["content-type"] = content_type_value
                        if message.get_content_maintype() == "application":
                            subtype = message.get_content_subtype()
                            if subtype == "json" or subtype.endswith("+json"):
                                json_body = await request.json()
                    if json_body != Undefined:
                        body = json_body
                    else:
                        body = body_bytes
    except json.JSONDecodeError as e:
        raise RequestValidationError([ErrorWrapper(e, ("body", e.pos))], body=e.doc)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail="There was an error parsing the body"
        ) from e
    solved_result = await solve_dependencies(
        request=request,
        dependant=dependant,
        body=body,
        dependency_overrides_provider=dependency_overrides_provider,
    )
    values, errors, background_tasks, sub_response, _ = solved_result
    if errors:
        raise RequestValidationError(errors, body=body)
    else:
        raw_response = await run_endpoint_function(
            dependant=dependant, values=values, is_coroutine=is_coroutine
        )
        if isinstance(raw_response, Response):
            if raw_response.background is None:
                raw_response.background = background_tasks
            return raw_response
        response_args = {"background": background_tasks}
        current_status_code = (
            status_code if status_code else sub_response.status_code
        )
        if current_status_code is not None:
            response_args["status_code"] = current_status_code
        if sub_response.status_code:
            response_args["status_code"] = sub_response.status_code
        content = await serialize_response(
            field=response_field,
            response_content=raw_response,
            include=response_model_include,
            exclude=response_model_exclude,
            by_alias=response_model_by_alias,
            exclude_unset=response_model_exclude_unset,
            exclude_defaults=response_model_exclude_defaults,
            exclude_none=response_model_exclude_none,
            is_coroutine=is_coroutine,
        )
        response = actual_response_class(content, **response_args)
        if not is_body_allowed_for_status_code(status_code):
            response.body = b""
        response.headers.raw.extend(sub_response.headers.raw)
        return response

def get_swagger_ui_oauth2_redirect_html():
    html = """
    <!DOCTYPE html>
    <html lang="en-US">
    <body onload="run()">
    </body>
    </html>
    <script>
        'use strict';
        function run () {
            var oauth2 = window.opener.swaggerUIRedirectOauth2;
            var sentState = oauth2.state;
            var redirectUrl = oauth2.redirectUrl;
            var isValid, qp, arr;

            if (/code|token|error/.test(window.location.hash)) {
                qp = window.location.hash.substring(1);
            } else {
                qp = location.search.substring(1);
            }

            arr = qp.split("&")
            arr.forEach(function (v,i,_arr) { _arr[i] = '"' + v.replace('=', '":"') + '"';})
            qp = qp ? JSON.parse('{' + arr.join() + '}',
                    function (key, value) {
                        return key === "" ? value : decodeURIComponent(value)
                    }
            ) : {}

            isValid = qp.state === sentState

            if ((
            oauth2.auth.schema.get("flow") === "accessCode"||
            oauth2.auth.schema.get("flow") === "authorizationCode"
            ) && !oauth2.auth.code) {
                if (!isValid) {
                    oauth2.errCb({
                        authId: oauth2.auth.name,
                        source: "auth",
                        level: "warning",
                        message: "Authorization may be unsafe, passed state was changed in server Passed state wasn't returned from auth server"
                    });
                }

                if (qp.code) {
                    delete oauth2.state;
                    oauth2.auth.code = qp.code;
                    oauth2.callback({auth: oauth2.auth, redirectUrl: redirectUrl});
                } else {
                    let oauthErrorMsg
                    if (qp.error) {
                        oauthErrorMsg = "["+qp.error+"]: " +
                            (qp.error_description ? qp.error_description+ ". " : "no accessCode received from the server. ") +
                            (qp.error_uri ? "More info: "+qp.error_uri : "");
                    }

                    oauth2.errCb({
                        authId: oauth2.auth.name,
                        source: "auth",
                        level: "error",
                        message: oauthErrorMsg || "[Authorization failed]: no accessCode received from the server"
                    });
                }
            } else {
                oauth2.callback({auth: oauth2.auth, token: qp, isValid: isValid, redirectUrl: redirectUrl});
            }
            window.close();
        }
    </script>
        """
    return HTMLResponse(content=html)

def get_swagger_ui_html(
    *,
    openapi_url,
    title,
    swagger_js_url = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js",
    swagger_css_url = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css",
    swagger_favicon_url = "https://fastapi.tiangolo.com/img/favicon.png",
    oauth2_redirect_url = None,
    init_oauth = None,
    swagger_ui_parameters = None,
):
    current_swagger_ui_parameters = swagger_ui_default_parameters.copy()
    if swagger_ui_parameters:
        current_swagger_ui_parameters.update(swagger_ui_parameters)
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <link type="text/css" rel="stylesheet" href="{swagger_css_url}">
    <link rel="shortcut icon" href="{swagger_favicon_url}">
    <title>{title}</title>
    </head>
    <body>
    <div id="swagger-ui">
    </div>
    <script src="{swagger_js_url}"></script>
    <!-- `SwaggerUIBundle` is now available on the page -->
    <script>
    const ui = SwaggerUIBundle({{
        url: '{openapi_url}',
    """
    for key, value in current_swagger_ui_parameters.items():
        html += f"{json.dumps(key)}: {json.dumps(jsonable_encoder(value))},\n"
    if oauth2_redirect_url:
        html += f"oauth2RedirectUrl: window.location.origin + '{oauth2_redirect_url}',"
    html += """
    presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIBundle.SwaggerUIStandalonePreset
        ],
    })"""
    if init_oauth:
        html += f"""
        ui.initOAuth({json.dumps(jsonable_encoder(init_oauth))})
        """
    html += """
    </script>
    </body>
    </html>
    """
    return HTMLResponse(html)

def new_lang(lang = typer.Argument(..., callback=lang_callback)):
    new_path = Path("docs") / lang
    if new_path.exists():
        typer.echo(f"The language was already created: {lang}")
        raise typer.Abort()
    new_path.mkdir()
    new_config = get_base_lang_config(lang)
    new_config_path = Path(new_path) / mkdocs_name
    new_config_path.write_text(
        yaml.dump(new_config, sort_keys=False, width=200, allow_unicode=True),
        encoding="utf-8",
    )
    new_config_docs_path = new_path / "docs"
    new_config_docs_path.mkdir()
    en_index_path = en_docs_path / "docs" / "index.md"
    new_index_path = new_config_docs_path / "index.md"
    en_index_content = en_index_path.read_text(encoding="utf-8")
    new_index_content = f"{missing_translation_snippet}\n\n{en_index_content}"
    new_index_path.write_text(new_index_content, encoding="utf-8")
    typer.secho(f"Successfully initialized: {new_path}", color=typer.colors.GREEN)
    update_languages(lang=None)

def get_swagger_ui_html(
    *,
    openapi_url,
    title,
    swagger_js_url = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@3.30.0/swagger-ui-bundle.js",
    swagger_css_url = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@3.30.0/swagger-ui.css",
    swagger_favicon_url = "https://fastapi.tiangolo.com/img/favicon.png",
    oauth2_redirect_url = None,
    init_oauth = None,
):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <link type="text/css" rel="stylesheet" href="{swagger_css_url}">
    <link rel="shortcut icon" href="{swagger_favicon_url}">
    <title>{title}</title>
    </head>
    <body>
    <div id="swagger-ui">
    </div>
    <script src="{swagger_js_url}"></script>
    <!-- `SwaggerUIBundle` is now available on the page -->
    <script>
    const ui = SwaggerUIBundle({{
        url: '{openapi_url}',
    """
    if oauth2_redirect_url:
        html += f"oauth2RedirectUrl: window.location.origin + '{oauth2_redirect_url}',"
    html += """
        dom_id: '#swagger-ui',
        presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIBundle.SwaggerUIStandalonePreset
        ],
        layout: "BaseLayout",
        deepLinking: true,
        showExtensions: true,
        showCommonExtensions: true
    })"""
    if init_oauth:
        html += f"""
        ui.initOAuth({json.dumps(jsonable_encoder(init_oauth))})
        """
    html += """
    </script>
    </body>
    </html>
    """
    return HTMLResponse(html)

def build_lang(
    lang = typer.Argument(
        ..., callback=lang_callback, autocompletion=complete_existing_lang
    )
):
    lang_path = Path("docs") / lang
    if not lang_path.is_dir():
        typer.echo(f"The language translation doesn't seem to exist yet: {lang}")
        raise typer.Abort()
    typer.echo(f"Building docs for: {lang}")
    build_dir_path = Path("docs_build")
    build_dir_path.mkdir(exist_ok=True)
    build_lang_path = build_dir_path / lang
    en_lang_path = Path("docs/en")
    site_path = Path("site").absolute()
    if lang == "en":
        dist_path = site_path
    else:
        dist_path = site_path / lang
    shutil.rmtree(build_lang_path, ignore_errors=True)
    shutil.copytree(lang_path, build_lang_path)
    shutil.copytree(en_docs_path / "data", build_lang_path / "data")
    en_config_path = en_lang_path / mkdocs_name
    en_config = mkdocs.utils.yaml_load(en_config_path.read_text(encoding="utf-8"))
    nav = en_config["nav"]
    lang_config_path = lang_path / mkdocs_name
    lang_config = mkdocs.utils.yaml_load(
        lang_config_path.read_text(encoding="utf-8")
    )
    lang_nav = lang_config["nav"]
    use_nav = nav[2:]
    lang_use_nav = lang_nav[2:]
    file_to_nav = get_file_to_nav_map(use_nav)
    sections = get_sections(use_nav)
    lang_file_to_nav = get_file_to_nav_map(lang_use_nav)
    use_lang_file_to_nav = get_file_to_nav_map(lang_use_nav)
    for file in file_to_nav:
        file_path = Path(file)
        lang_file_path = build_lang_path / "docs" / file_path
        en_file_path = en_lang_path / "docs" / file_path
        lang_file_path.parent.mkdir(parents=True, exist_ok=True)
        if not lang_file_path.is_file():
            en_text = en_file_path.read_text(encoding="utf-8")
            lang_text = get_text_with_translate_missing(en_text)
            lang_file_path.write_text(lang_text, encoding="utf-8")
            file_key = file_to_nav[file]
            use_lang_file_to_nav[file] = file_key
            if file_key:
                composite_key = ()
                new_key = ()
                for key_part in file_key:
                    composite_key += (key_part,)
                    key_first_file = sections[composite_key]
                    if key_first_file in lang_file_to_nav:
                        new_key = lang_file_to_nav[key_first_file]
                    else:
                        new_key += (key_part,)
                use_lang_file_to_nav[file] = new_key
    key_to_section = {(): []}
    for file, file_key in use_lang_file_to_nav.items():
        section = get_key_section(key_to_section=key_to_section, key=file_key)
        section.append(file)
    new_nav = key_to_section[()]
    export_lang_nav = [lang_nav[0], nav[1]] + new_nav
    lang_config["nav"] = export_lang_nav
    build_lang_config_path = build_lang_path / mkdocs_name
    build_lang_config_path.write_text(
        yaml.dump(lang_config, sort_keys=False, width=200, allow_unicode=True),
        encoding="utf-8",
    )
    current_dir = os.getcwd()
    os.chdir(build_lang_path)
    mkdocs.commands.build.build(mkdocs.config.load_config(site_dir=str(dist_path)))
    os.chdir(current_dir)
    typer.secho(f"Successfully built docs for: {lang}", color=typer.colors.GREEN)

def jsonable_encoder(
    obj,
    include = None,
    exclude = None,
    by_alias = True,
    exclude_unset = False,
    exclude_defaults = False,
    exclude_none = False,
    custom_encoder = {},
):
    if include is not None and not isinstance(include, set):
        include = set(include)
    if exclude is not None and not isinstance(exclude, set):
        exclude = set(exclude)
    if isinstance(obj, BaseModel):
        encoder = getattr(obj.__config__, "json_encoders", {})
        if custom_encoder:
            encoder.update(custom_encoder)
        obj_dict = obj.dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_none=exclude_none,
            exclude_defaults=exclude_defaults,
        )
        if "__root__" in obj_dict:
            obj_dict = obj_dict["__root__"]
        return jsonable_encoder(
            obj_dict,
            exclude_none=exclude_none,
            exclude_defaults=exclude_defaults,
            custom_encoder=encoder,
        )
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, PurePath):
        return str(obj)
    if isinstance(obj, (str, int, float, type(None))):
        return obj
    if isinstance(obj, dict):
        encoded_dict = {}
        for key, value in obj.items():
            if (value is not None or not exclude_none) and (
                (include and key in include) or not exclude or key not in exclude
            ):
                encoded_key = jsonable_encoder(
                    key,
                    by_alias=by_alias,
                    exclude_unset=exclude_unset,
                    exclude_none=exclude_none,
                    custom_encoder=custom_encoder,
                )
                encoded_value = jsonable_encoder(
                    value,
                    by_alias=by_alias,
                    exclude_unset=exclude_unset,
                    exclude_none=exclude_none,
                    custom_encoder=custom_encoder,
                )
                encoded_dict[encoded_key] = encoded_value
        return encoded_dict
    if isinstance(obj, (list, set, frozenset, GeneratorType, tuple)):
        encoded_list = []
        for item in obj:
            encoded_list.append(
                jsonable_encoder(
                    item,
                    include=include,
                    exclude=exclude,
                    by_alias=by_alias,
                    exclude_unset=exclude_unset,
                    exclude_defaults=exclude_defaults,
                    exclude_none=exclude_none,
                    custom_encoder=custom_encoder,
                )
            )
        return encoded_list
    if custom_encoder:
        if type(obj) in custom_encoder:
            return custom_encoder[type(obj)](obj)
        else:
            for encoder_type, encoder in custom_encoder.items():
                if isinstance(obj, encoder_type):
                    return encoder(obj)
    if type(obj) in ENCODERS_BY_TYPE:
        return ENCODERS_BY_TYPE[type(obj)](obj)
    for encoder, classes_tuple in encoders_by_class_tuples.items():
        if isinstance(obj, classes_tuple):
            return encoder(obj)
    errors = []
    try:
        data = dict(obj)
    except Exception as e:
        errors.append(e)
        try:
            data = vars(obj)
        except Exception as e:
            errors.append(e)
            raise ValueError(errors)
    return jsonable_encoder(
        data,
        by_alias=by_alias,
        exclude_unset=exclude_unset,
        exclude_defaults=exclude_defaults,
        exclude_none=exclude_none,
        custom_encoder=custom_encoder,
    )

def create_url_adapter(self, request):
    if request is not None:
        if not self.subdomain_matching:
            subdomain = self.url_map.default_subdomain or None
        else:
            subdomain = None
        print(self.config["SERVER_NAME"], subdomain)
        return self.url_map.bind_to_environ(
            request.environ,
            server_name=self.config["SERVER_NAME"],
            subdomain=subdomain,
        )
    if self.config["SERVER_NAME"] is not None:
        return self.url_map.bind(
            self.config["SERVER_NAME"],
            script_name=self.config["APPLICATION_ROOT"],
            url_scheme=self.config["PREFERRED_URL_SCHEME"],
        )
    return None

def __getattr__(name):
    if name == "_app_ctx_stack":
        import warnings
        warnings.warn(
            "'_app_ctx_stack' is deprecated and will be remoevd in Flask 2.3.",
            DeprecationWarning,
            stacklevel=2,
        )
        return __app_ctx_stack
    if name == "_request_ctx_stack":
        import warnings
        warnings.warn(
            "'_request_ctx_stack' is deprecated and will be remoevd in Flask 2.3.",
            DeprecationWarning,
            stacklevel=2,
        )
        return __request_ctx_stack
    raise AttributeError(name)

def shell_command():
    import code
    banner = (
        f"Python {sys.version} on {sys.platform}\n"
        f"App: {current_app.import_name} [{current_app.env}]\n"
        f"Instance: {current_app.instance_path}"
    )
    ctx = {}
    startup = os.environ.get("PYTHONSTARTUP")
    if startup and os.path.isfile(startup):
        with open(startup) as f:
            eval(compile(f.read(), startup, "exec"), ctx)
    ctx.update(current_app.make_shell_context())
    interactive_hook = getattr(sys, "__interactivehook__", None)
    if interactive_hook is not None:
        try:
            import readline
            from rlcompleter import Completer
        except ImportError:
            pass
        else:
            readline.set_completer(Completer(ctx).complete)
        interactive_hook()
    code.interact(banner=banner, local=ctx)

def find_best_app(script_info, module):
    from . import Flask
    for attr_name in ("app", "application"):
        app = getattr(module, attr_name, None)
        if isinstance(app, Flask):
            return app
    matches = [v for v in module.__dict__.values() if isinstance(v, Flask)]
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        raise NoAppException(
            "Detected multiple Flask applications in module"
            f" {module.__name__!r}. Use 'FLASK_APP={module.__name__}:name'"
            f" to specify the correct one."
        )
    for attr_name in {"create_app", "make_app"}:
        app_factory = getattr(module, attr_name, None)
        if inspect.isfunction(app_factory):
            try:
                app = call_factory(script_info, app_factory)
                if isinstance(app, Flask):
                    return app
            except TypeError:
                if not _called_with_wrong_args(app_factory):
                    raise
                raise NoAppException(
                    f"Detected factory {attr_name!r} in module {module.__name__!r},"
                    " but could not call it without arguments. Use"
                    f" \"FLASK_APP='{module.__name__}:{attr_name}(args)'\""
                    " to specify arguments."
                )
    raise NoAppException(
        "Failed to find Flask application or factory in module"
        f" {module.__name__!r}. Use 'FLASK_APP={module.__name__}:name'"
        " to specify one."
    )

def handle_exception(self, e):
    exc_type, exc_value, tb = sys.exc_info()
    got_request_exception.send(self, exception=e)
    handler = self._find_error_handler(InternalServerError())
    if self.propagate_exceptions:
        if exc_value is e:
            reraise(exc_type, exc_value, tb)
        else:
            raise e
    self.log_exception((exc_type, exc_value, tb))
    if handler is None:
        return InternalServerError()
    return self.finalize_request(handler(e), from_error_handler=True)

def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
    if self.url_prefix:
        rule = '/'.join((self.url_prefix, rule.lstrip('/')))
    options.setdefault('subdomain', self.subdomain)
    if endpoint is None:
        endpoint = _endpoint_from_view_func(view_func)
    defaults = self.url_defaults
    if 'defaults' in options:
        defaults = dict(defaults, **options.pop('defaults'))
    self.app.add_url_rule(rule, '%s.%s' % (self.blueprint.name, endpoint),
                          view_func, defaults=defaults, **options)

def make_response(self, rv):
    status = headers = None
    if isinstance(rv, (tuple, list)):
        len_rv = len(rv)
        if len_rv == 3:
            rv, status, headers = rv
        elif len_rv == 2:
            if isinstance(rv[1], (Headers, dict, tuple, list)):
                rv, headers = rv
            else:
                rv, status = rv
        else:
            raise TypeError(
                'The view function did not return a valid response tuple.'
                ' The tuple must have the form (body, status, headers),'
                ' (body, status), or (body, headers).'
            )
    if rv is None:
        raise TypeError(
            'The view function did not return a valid response. The'
            ' function either returned None or ended without a return'
            ' statement.'
        )
    if not isinstance(rv, self.response_class):
        if isinstance(rv, (text_type, bytes, bytearray)):
            rv = self.response_class(rv, status=status, headers=headers)
            status = headers = None
        else:
            try:
                rv = self.response_class.force_type(rv, request.environ)
            except TypeError as e:
                new_error = TypeError(
                    '{e}\nThe view function did not return a valid'
                    ' response. The return type must be a string, tuple,'
                    ' Response instance, or WSGI callable, but it was a'
                    ' {rv.__class__.__name__}.'.format(e=e, rv=rv)
                )
                reraise(TypeError, new_error, sys.exc_info()[2])
    if status is not None:
        if isinstance(status, (text_type, bytes, bytearray)):
            rv.status = status
        else:
            rv.status_code = status
    if headers:
        rv.headers.extend(headers)
    return rv

def main(as_module=False):
    this_module = __package__ + '.cli'
    args = sys.argv[1:]
    if as_module:
        if sys.version_info >= (2, 7):
            name = 'python -m ' + this_module.rsplit('.', 1)[0]
        else:
            name = 'python -m ' + this_module
        sys.argv = ['-m', this_module] + sys.argv[1:]
    else:
        name = None
    cli.main(args=args, prog_name=name)

def locate_app(script_info, app_id, raise_if_not_found=True):
    __traceback_hide__ = True
    if ':' in app_id:
        module, app_obj = app_id.split(':', 1)
    else:
        module = app_id
        app_obj = None
    try:
        __import__(module)
    except ImportError:
        if sys.exc_info()[-1].tb_next:
            stack_trace = traceback.format_exc()
            raise NoAppException(
                'There was an error trying to import the app ({module}):\n'
                '{stack_trace}'.format(
                    module=module, stack_trace=stack_trace
                )
            )
        elif raise_if_not_found:
            raise NoAppException(
                'The file/path provided (%s) does not appear to exist. Please'
                ' verify the path is correct. If app is not on PYTHONPATH,'
                ' ensure the extension is .py.'.format(module=module)
            )
        else:
            return
    mod = sys.modules[module]
    if app_obj is None:
        return find_best_app(script_info, mod)
    else:
        return find_app_by_string(app_obj, script_info, mod)

def call_factory(app_factory, script_info, arguments=()):
    arg_names = getargspec(app_factory).args
    if 'script_info' in arg_names:
        return app_factory(*arguments, script_info=script_info)
    elif arguments:
        return app_factory(*arguments)
    elif not arguments and len(arg_names) == 1:
        return app_factory(script_info)
    return app_factory()

def find_best_app(module):
    from . import Flask
    for attr_name in 'app', 'application':
        app = getattr(module, attr_name, None)
        if app is not None and isinstance(app, Flask):
            return app
    matches = [v for k, v in iteritems(module.__dict__)
               if isinstance(v, Flask)]
    if len(matches) == 1:
        return matches[0]
    for attr_name in 'create_app', 'make_app':
        app_factory = getattr(module, attr_name, None)
        if app_factory is not None and callable(app_factory):
            try:
                app = app_factory()
                if app is not None and isinstance(app, Flask):
                    return app
            except TypeError:
                raise NoAppException('Auto-detected "%s()" in module "%s", '
                                     'but could not call it without '
                                     'specifying arguments.'
                                     % (attr_name, module.__name__))
    raise NoAppException('Failed to find application in module "%s".  Are '
                         'you sure it contains a Flask application?  Maybe '
                         'you wrapped it in a WSGI middleware or you are '
                         'using a factory function.' % module.__name__)

def __call__(self, *args, **kwargs):
    plot_backend = _get_plot_backend(kwargs.pop("backend", None))
    x, y, kind, kwargs = self._get_call_args(
        plot_backend.__name__, self._parent, args, kwargs
    )
    kind = self._kind_aliases.get(kind, kind)
    if plot_backend.__name__ != "pandas.plotting._matplotlib":
        return plot_backend.plot(self._parent, x=x, y=y, kind=kind, **kwargs)
    if kind not in self._all_kinds:
        raise ValueError(f"{kind} is not a valid plot kind")
    data = self._parent.copy()
    if isinstance(data, ABCSeries):
        kwargs["reuse_plot"] = True
    if kind in self._dataframe_kinds:
        if isinstance(data, ABCDataFrame):
            return plot_backend.plot(data, x=x, y=y, kind=kind, **kwargs)
        else:
            raise ValueError(f"plot kind {kind} can only be used for data frames")
    elif kind in self._series_kinds:
        if isinstance(data, ABCDataFrame):
            if y is None and kwargs.get("subplots") is False:
                raise ValueError(
                    f"{kind} requires either y column or 'subplots=True'"
                )
            if y is not None:
                if is_integer(y) and not data.columns._holds_integer():
                    y = data.columns[y]
                data = data[y].copy()
                data.index.name = y
    elif isinstance(data, ABCDataFrame):
        data_cols = data.columns
        if x is not None:
            if is_integer(x) and not data.columns._holds_integer():
                x = data_cols[x]
            elif not isinstance(data[x], ABCSeries):
                raise ValueError("x must be a label or position")
            data = data.set_index(x)
        if y is not None:
            int_ylist = is_list_like(y) and all(is_integer(c) for c in y)
            int_y_arg = is_integer(y) or int_ylist
            if int_y_arg and not data.columns._holds_integer():
                y = data_cols[y]
            label_kw = kwargs["label"] if "label" in kwargs else False
            for kw in ["xerr", "yerr"]:
                if kw in kwargs and (
                    isinstance(kwargs[kw], str) or is_integer(kwargs[kw])
                ):
                    try:
                        kwargs[kw] = data[kwargs[kw]]
                    except (IndexError, KeyError, TypeError):
                        pass
            data = data[y].copy()
            if isinstance(data, ABCSeries):
                label_name = label_kw or y
                data.name = label_name
            else:
                match = is_list_like(label_kw) and len(label_kw) == len(y)
                if label_kw and not match:
                    raise ValueError(
                        "label should be list-like and same length as y"
                    )
                label_name = label_kw or data.columns
                data.columns = label_name
    return plot_backend.plot(data, kind=kind, **kwargs)

def _transform(self, func, *args, engine=None, engine_kwargs=None, **kwargs):
    orig_func = func
    func = com.get_cython_func(func) or func
    if orig_func != func:
        warn_alias_replacement(self, orig_func, func)
    if not isinstance(func, str):
        return self._transform_general(func, engine, engine_kwargs, *args, **kwargs)
    elif func not in base.transform_kernel_allowlist:
        msg = f"'{func}' is not a valid function name for transform(name)"
        raise ValueError(msg)
    elif func in base.cythonized_kernels or func in base.transformation_kernels:
        if engine is not None:
            kwargs["engine"] = engine
            kwargs["engine_kwargs"] = engine_kwargs
        return getattr(self, func)(*args, **kwargs)
    else:
        with com.temp_setattr(self, "observed", True):
            with com.temp_setattr(self, "as_index", True):
                if engine is not None:
                    kwargs["engine"] = engine
                    kwargs["engine_kwargs"] = engine_kwargs
                result = getattr(self, func)(*args, **kwargs)
        return self._wrap_transform_fast_result(result)

def warn_alias_replacement(
    obj,
    func,
    alias,
):
    if alias.startswith("np."):
        full_alias = alias
    else:
        full_alias = f"{type(obj).__name__}.{alias}"
        alias = f"'{alias}'"
    warnings.warn(
        f"The provided callable {func} is currently using "
        f"{full_alias}. In a future version of pandas, "
        f"the provided callable will be used directly. To keep current "
        f"behavior pass {alias} instead.",
        category=FutureWarning,
        stacklevel=find_stack_level(),
    )

def is_categorical_dtype(arr_or_dtype):
    warnings.warn(
        "is_categorical_dtype is deprecated and will be removed in a future "
        "version. Use isinstance(dtype, CategoricalDtype) instead",
        FutureWarning,
        stacklevel=find_stack_level(),
    )
    if isinstance(arr_or_dtype, ExtensionDtype):
        return arr_or_dtype.name == "category"
    if arr_or_dtype is None:
        return False
    return CategoricalDtype.is_dtype(arr_or_dtype)

def _get_page_title(self, page):
    fname = os.path.join(SOURCE_PATH, f"{page}.rst")
    option_parser = docutils.frontend.OptionParser(
        components=(docutils.parsers.rst.Parser,)
    )
    doc = docutils.utils.new_document("<doc>", option_parser.get_default_values())
    with open(fname, encoding="utf-8") as f:
        data = f.read()
    parser = docutils.parsers.rst.Parser()
    with open(os.devnull, "a", encoding="utf-8") as f:
        doc.reporter.stream = f
        parser.parse(data, doc)
    section = next(
        node for node in doc.children if isinstance(node, docutils.nodes.section)
    )
    title = next(
        node for node in section.children if isinstance(node, docutils.nodes.title)
    )
    return title.astext()

def convert_fill_value(value, pa_type, dtype):
    if value is None:
        return value
    if isinstance(value, (pa.Scalar, pa.Array, pa.ChunkedArray)):
        return value
    if is_array_like(value):
        pa_box = pa.array
    else:
        pa_box = pa.scalar
    try:
        value = pa_box(value, type=pa_type, from_pandas=True)
    except pa.ArrowTypeError as err:
        msg = f"Invalid value '{str(value)}' for dtype {dtype}"
        raise TypeError(msg) from err
    return value

def _reduce(
    self,
    op,
    name,
    *,
    axis = 0,
    skipna = True,
    numeric_only = False,
    filter_type=None,
    **kwds,
):
    assert filter_type is None or filter_type == "bool", filter_type
    out_dtype = "bool" if filter_type == "bool" else None
    if axis is not None:
        axis = self._get_axis_number(axis)
    def func(values):
        return op(values, axis=axis, skipna=skipna, **kwds)
    def blk_func(values, axis = 1):
        if isinstance(values, ExtensionArray):
            if not is_1d_only_ea_dtype(values.dtype) and not isinstance(
                self._mgr, ArrayManager
            ):
                return values._reduce(name, axis=1, skipna=skipna, **kwds)
            sign = signature(values._reduce)
            if "keepdims" in sign.parameters:
                return values._reduce(name, skipna=skipna, keepdims=True, **kwds)
            else:
                warnings.warn(
                    f"{type(values)}._reduce will require a `keepdims` parameter "
                    "in the future",
                    FutureWarning,
                    stacklevel=find_stack_level(),
                )
                result = values._reduce(name, skipna=skipna, **kwds)
                return np.array([result])
        else:
            return op(values, axis=axis, skipna=skipna, **kwds)
    def _get_data():
        if filter_type is None:
            data = self._get_numeric_data()
        else:
            assert filter_type == "bool"
            data = self._get_bool_data()
        return data
    df = self
    if numeric_only:
        df = _get_data()
    if axis is None:
        dtype = find_common_type([arr.dtype for arr in df._mgr.arrays])
        if isinstance(dtype, ExtensionDtype):
            df = df.astype(dtype, copy=False)
            arr = concat_compat(list(df._iter_column_arrays()))
            return arr._reduce(name, skipna=skipna, keepdims=False, **kwds)
        return func(df.values)
    elif axis == 1:
        if len(df.index) == 0:
            result = df._reduce(
                op,
                name,
                axis=0,
                skipna=skipna,
                numeric_only=False,
                filter_type=filter_type,
                **kwds,
            ).iloc[:0]
            result.index = df.index
            return result
        df = df.T
    res = df._mgr.reduce(blk_func)
    out = df._constructor_from_mgr(res, axes=res.axes).iloc[0]
    if out_dtype is not None and out.dtype != "boolean":
        out = out.astype(out_dtype)
    elif (df._mgr.get_dtypes() == object).any() and name not in ["any", "all"]:
        out = out.astype(object)
    elif len(self) == 0 and out.dtype == object and name in ("sum", "prod"):
        out = out.astype(np.float64)
    return out

def setup(self):
    N = 50000
    self.left = DataFrame(
        np.random.randint(1, N / 500, (N, 2)), columns=["jim", "joe"]
    )
    self.right = DataFrame(
        np.random.randint(1, N / 500, (N, 2)), columns=["jolie", "jolia"]
    ).set_index("jolie")

def apply_standard(self):
    func = cast(Callable, self.func)
    obj = self.obj
    if isinstance(func, np.ufunc):
        with np.errstate(all="ignore"):
            return func(obj, *self.args, **self.kwargs)
    elif not self.by_row:
        return func(obj, *self.args, **self.kwargs)
    if self.args or self.kwargs:
        def curried(x):
            return func(x, *self.args, **self.kwargs)
    else:
        curried = func
    action = "ignore" if isinstance(obj.dtype, CategoricalDtype) else None
    mapped = obj._map_values(
        mapper=curried, na_action=action, convert=self.convert_dtype
    )
    if len(mapped) and isinstance(mapped[0], ABCSeries):
        warnings.warn(
            "Returning a DataFrame from Series.apply when the supplied function"
            "returns a Series is deprecated and will be removed in a future "
            "version.",
            FutureWarning,
            stacklevel=find_stack_level(),
        )  
        return obj._constructor_expanddim(list(mapped), index=obj.index)
    else:
        return obj._constructor(mapped, index=obj.index).__finalize__(
            obj, method="apply"
        )

def _str_repeat(self, repeats):
    if not isinstance(repeats, int):
        raise NotImplementedError(
            f"repeat is not implemented when repeats is {type(repeats).__name__}"
        )
    elif pa_version_under7p0:
        raise NotImplementedError("repeat is not implemented for pyarrow < 7")
    else:
        return type(self)(pc.binary_repeat(self._pa_array, repeats))

def _concat_homogeneous_fastpath(
    mgrs_indexers, shape, first_dtype
):
    arr = np.empty(shape, dtype=first_dtype)
    if first_dtype == np.float64:
        take_func = libalgos.take_2d_axis0_float64_float64
    else:
        take_func = libalgos.take_2d_axis0_float32_float32
    start = 0
    for mgr, indexers in mgrs_indexers:
        mgr_len = mgr.shape[1]
        end = start + mgr_len
        if 0 in indexers:
            take_func(
                mgr.blocks[0].values,
                indexers[0],
                arr[:, start:end],
            )
        else:
            arr[:, start:end] = mgr.blocks[0].values
        start += mgr_len
    bp = libinternals.BlockPlacement(slice(shape[0]))
    nb = new_block_2d(arr, bp)
    return nb

def roadmap_pdeps(context):
    KNOWN_STATUS = {
        "Under discussion",
        "Accepted",
        "Implemented",
        "Rejected",
        "Withdrawn",
    }
    context["pdeps"] = collections.defaultdict(list)
    pdeps_path = (
        pathlib.Path(context["source_path"]) / context["roadmap"]["pdeps_path"]
    )
    for pdep in sorted(pdeps_path.iterdir()):
        if pdep.suffix != ".md":
            continue
        with pdep.open() as f:
            title = f.readline()[2:]  
            status = None
            for line in f:
                if line.startswith("- Status: "):
                    status = line.strip().split(": ", 1)[1]
                    break
            if status not in KNOWN_STATUS:
                raise RuntimeError(
                    f'PDEP "{pdep}" status "{status}" is unknown. '
                    f"Should be one of: {KNOWN_STATUS}"
                )
        html_file = pdep.with_suffix(".html").name
        context["pdeps"][status].append(
            {
                "title": title,
                "url": f"pdeps/{html_file}",
            }
        )
    github_repo_url = context["main"]["github_repo_url"]
    resp = requests.get(
        "https://api.github.com/search/issues?"
        f"q=is:pr is:open label:PDEP repo:{github_repo_url}",
        headers=GITHUB_API_HEADERS,
    )
    if resp.status_code == 403:
        sys.stderr.write("WARN: GitHub API quota exceeded when fetching pdeps\n")
        resp_bkp = requests.get(context["main"]["production_url"] + "pdeps.json")
        resp_bkp.raise_for_status()
        pdeps = resp_bkp.json()
    else:
        resp.raise_for_status()
        pdeps = resp.json()
    with open(
        pathlib.Path(context["target_path"]) / "pdeps.json", "w", encoding="utf-8"
    ) as f:
        json.dump(pdeps, f)
    for pdep in sorted(pdeps["items"], key=operator.itemgetter("title")):
        context["pdeps"]["Under discussion"].append(
            {"title": pdep["title"], "url": pdep["html_url"]}
        )
    return context

def wrapper(*args, **kwargs):
    old_arg_value = kwargs.pop(old_arg_name, None)
    if old_arg_value is not None:
        if new_arg_name is None:
            msg = (
                f"the {repr(old_arg_name)} keyword is deprecated and "
                "will be removed in a future version. Please take "
                f"steps to stop the use of {repr(old_arg_name)}"
            )
            warnings.warn(msg, FutureWarning, stacklevel=stacklevel)
            kwargs[old_arg_name] = old_arg_value
            return func(*args, **kwargs)
        elif mapping is not None:
            if callable(mapping):
                new_arg_value = mapping(old_arg_value)
            else:
                new_arg_value = mapping.get(old_arg_value, old_arg_value)
            msg = (
                f"the {old_arg_name}={repr(old_arg_value)} keyword is "
                "deprecated, use "
                f"{new_arg_name}={repr(new_arg_value)} instead."
            )
        else:
            new_arg_value = old_arg_value
            msg = (
                f"the {repr(old_arg_name)}' keyword is deprecated, "
                f"use {repr(new_arg_name)} instead."
            )
        warnings.warn(msg, FutureWarning, stacklevel=stacklevel)
        if kwargs.get(new_arg_name) is not None:
            msg = (
                f"Can only specify {repr(old_arg_name)} "
                f"or {repr(new_arg_name)}, not both."
            )
            raise TypeError(msg)
        kwargs[new_arg_name] = new_arg_value
    return func(*args, **kwargs)

def infer_freq(
    index,
):
    from pandas.core.api import (
        DatetimeIndex,
        Index,
    )
    if isinstance(index, ABCSeries):
        values = index._values
        if not (
            lib.is_np_dtype(values.dtype, "mM")
            or isinstance(values.dtype, DatetimeTZDtype)
            or values.dtype == object
        ):
            raise TypeError(
                "cannot infer freq from a non-convertible dtype "
                f"on a Series of {index.dtype}"
            )
        index = values
    if not hasattr(index, "dtype"):
        pass
    elif isinstance(index.dtype, PeriodDtype):
        raise TypeError(
            "PeriodIndex given. Check the `freq` attribute "
            "instead of using infer_freq."
        )
    elif lib.is_np_dtype(index.dtype, "m"):
        inferer = _TimedeltaFrequencyInferer(index)
        return inferer.get_freq()
    if isinstance(index, Index) and not isinstance(index, DatetimeIndex):
        if is_numeric_dtype(index.dtype):
            raise TypeError(
                f"cannot infer freq from a non-convertible index of dtype {index.dtype}"
            )
        index = index._values  
    if not isinstance(index, DatetimeIndex):
        index = DatetimeIndex(index)
    inferer = _FrequencyInferer(index)
    return inferer.get_freq()

def sanitize_masked_array(data):
    mask = ma.getmaskarray(data)
    if mask.any():
        dtype, fill_value = maybe_promote(data.dtype, np.nan)
        dtype = cast(np.dtype, dtype)
        data = data.astype(dtype, copy=True)  
        data.soften_mask()  
        data[mask] = fill_value
    else:
        data = data.copy()
    return data

def complete_package(
    self, dependency_package
):
    package = dependency_package.package
    dependency = dependency_package.dependency
    if package.is_root():
        dependency_package = dependency_package.clone()
        package = dependency_package.package
        dependency = dependency_package.dependency
        requires = package.all_requires
    elif package.is_direct_origin():
        requires = package.requires
    else:
        try:
            dependency_package = DependencyPackage(
                dependency,
                self._pool.package(
                    package.pretty_name,
                    package.version,
                    extras=list(dependency.extras),
                    repository_name=dependency.source_name,
                ),
            )
        except PackageNotFound as e:
            try:
                dependency_package = next(
                    DependencyPackage(dependency, pkg)
                    for pkg in self.search_for_installed_packages(dependency)
                )
            except StopIteration:
                raise e from e
        package = dependency_package.package
        dependency = dependency_package.dependency
        requires = package.requires
    optional_dependencies = []
    _dependencies = []
    if dependency.extras:
        for extra in dependency.extras:
            if extra not in package.extras:
                continue
            optional_dependencies += [d.name for d in package.extras[extra]]
        dependency_package = dependency_package.with_features(
            list(dependency.extras)
        )
        package = dependency_package.package
        dependency = dependency_package.dependency
        new_dependency = package.without_features().to_dependency()
        if not new_dependency.source_name and dependency.source_name:
            new_dependency.source_name = dependency.source_name
        _dependencies.append(new_dependency)
    for dep in requires:
        if not self._python_constraint.allows_any(dep.python_constraint):
            continue
        if dep.name in self.UNSAFE_PACKAGES:
            continue
        if self._env and not dep.marker.validate(self._env.marker_env):
            continue
        if not package.is_root() and (
            (dep.is_optional() and dep.name not in optional_dependencies)
            or (
                dep.in_extras
                and not set(dep.in_extras).intersection(dependency.extras)
            )
        ):
            continue
        _dependencies.append(dep)
    if self._load_deferred:
        for dep in _dependencies:
            if dep.is_direct_origin():
                locked = self.get_locked(dep)
                if locked is not None and locked.package.is_same_package_as(dep):
                    continue
                self.search_for_direct_origin_dependency(dep)
    dependencies = self._get_dependencies_with_overrides(
        _dependencies, dependency_package
    )
    duplicates = defaultdict(list)
    for dep in dependencies:
        duplicates[dep.complete_name].append(dep)
    dependencies = []
    for dep_name, deps in duplicates.items():
        if len(deps) == 1:
            dependencies.append(deps[0])
            continue
        self.debug(f"<debug>Duplicate dependencies for {dep_name}</debug>")
        deps = self._resolve_overlapping_markers(package, deps)
        if len(deps) == 1:
            self.debug(f"<debug>Merging requirements for {deps[0]!s}</debug>")
            dependencies.append(deps[0])
            continue
        def fmt_warning(d):
            dependency_marker = d.marker if not d.marker.is_any() else "*"
            return (
                f"<c1>{d.name}</c1> <fg=default>(<c2>{d.pretty_constraint}</c2>)</>"
                f" with markers <b>{dependency_marker}</b>"
            )
        warnings = ", ".join(fmt_warning(d) for d in deps[:-1])
        warnings += f" and {fmt_warning(deps[-1])}"
        self.debug(
            f"<warning>Different requirements found for {warnings}.</warning>"
        )
        overrides = []
        overrides_marker_intersection = AnyMarker()
        for dep_overrides in self._overrides.values():
            for dep in dep_overrides.values():
                overrides_marker_intersection = (
                    overrides_marker_intersection.intersect(dep.marker)
                )
        for dep in deps:
            if not overrides_marker_intersection.intersect(dep.marker).is_empty():
                current_overrides = self._overrides.copy()
                package_overrides = current_overrides.get(
                    dependency_package, {}
                ).copy()
                package_overrides.update({dep.name: dep})
                current_overrides.update({dependency_package: package_overrides})
                overrides.append(current_overrides)
        if overrides:
            raise OverrideNeeded(*overrides)
    clean_dependencies = []
    for dep in dependencies:
        if not dependency.transitive_marker.without_extras().is_any():
            transitive_marker_intersection = (
                dependency.transitive_marker.without_extras().intersect(
                    dep.marker.without_extras()
                )
            )
            if transitive_marker_intersection.is_empty():
                continue
            dep.transitive_marker = transitive_marker_intersection
        if not dependency.python_constraint.is_any():
            python_constraint_intersection = dep.python_constraint.intersect(
                dependency.python_constraint
            )
            if python_constraint_intersection.is_empty():
                continue
            dep.transitive_python_versions = str(python_constraint_intersection)
        clean_dependencies.append(dep)
    package = package.with_dependency_groups([], only=True)
    dependency_package = DependencyPackage(dependency, package)
    for dep in clean_dependencies:
        package.add_dependency(dep)
    return dependency_package

def activate(self, env):
    activate_script = self._get_activate_script()
    bin_dir = "Scripts" if WINDOWS else "bin"
    activate_path = env.path / bin_dir / activate_script
    if sys.platform == "win32":
        args = None
        if self._name in ("powershell", "pwsh"):
            args = ["-NoExit", "-File", str(activate_path)]
        elif self._name == "cmd":
            args = ["/K", str(activate_path)]
        if args:
            completed_proc = subprocess.run([self.path, *args])
            return completed_proc.returncode
        else:
            return env.execute(self._path)
    import shlex
    terminal = shutil.get_terminal_size()
    with env.temp_environ():
        c = pexpect.spawn(
            self._path, ["-i"], dimensions=(terminal.lines, terminal.columns)
        )
    if self._name in ["zsh", "nu"]:
        c.setecho(False)
    if self._name == "zsh":
        c.sendline(f"emulate bash -c '. {shlex.quote(str(activate_path))}'")
    elif self._name == "xonsh":
        c.sendline(f"vox activate {shlex.quote(str(env.path))}")
    else:
        cmd = f"{self._get_source_command()} {shlex.quote(str(activate_path))}"
        if self._name in ["fish", "nu"]:
            cmd += "\r"
        c.sendline(cmd)
    def resize(sig, data):
        terminal = shutil.get_terminal_size()
        c.setwinsize(terminal.lines, terminal.columns)
    signal.signal(signal.SIGWINCH, resize)
    c.interact(escape_character=None)
    c.close()
    sys.exit(c.exitstatus)

def activate(self, env):
    activate_script = self._get_activate_script()
    bin_dir = "Scripts" if WINDOWS else "bin"
    activate_path = env.path / bin_dir / activate_script
    if sys.platform == "win32":
        args = None
        if self._name in ("powershell", "pwsh"):
            args = ["-NoExit", "-File", str(activate_path)]
        elif self._name == "cmd":
            args = ["/K", str(activate_path)]
        if args:
            completed_proc = subprocess.run([self.path, *args])
            return completed_proc.returncode
        else:
            return env.execute(self._path)
    import shlex
    terminal = shutil.get_terminal_size()
    with env.temp_environ():
        c = pexpect.spawn(
            self._path, ["-i"], dimensions=(terminal.lines, terminal.columns)
        )
    if self._name in ["zsh", "nu"]:
        c.setecho(False)
    if self._name == "zsh":
        c.sendline(f"emulate bash -c '. {shlex.quote(str(activate_path))}'")
    else:
        cmd = f"{self._get_source_command()} {shlex.quote(str(activate_path))}"
        if self._name in ["fish", "nu"]:
            cmd += "\r"
        c.sendline(cmd)
    def resize(sig, data):
        terminal = shutil.get_terminal_size()
        c.setwinsize(terminal.lines, terminal.columns)
    signal.signal(signal.SIGWINCH, resize)
    c.interact(escape_character=None)
    c.close()
    sys.exit(c.exitstatus)

def package(
    self, name, version, extras = None
):
    canonicalized_name = canonicalize_name(name)
    for package in self.packages:
        if canonicalized_name == package.name and package.version == version:
            return package.clone()
    raise PackageNotFound(f"Package {name} ({version}) not found.")

def download_file(
    url,
    dest,
    session = None,
    chunk_size = 1024,
):
    import requests
    from poetry.puzzle.provider import Indicator
    get = requests.get if not session else session.get
    response = get(url, stream=True, timeout=REQUESTS_TIMEOUT)
    response.raise_for_status()
    set_indicator = False
    with Indicator.context() as update_context:
        update_context(f"Downloading {url}")
        if "Content-Length" in response.headers:
            try:
                total_size = int(response.headers["Content-Length"])
            except ValueError:
                total_size = 0
            fetched_size = 0
            last_percent = 0
            set_indicator = total_size > 1024 * 1024
        with dest.open("wb") as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    if set_indicator:
                        fetched_size += len(chunk)
                        percent = (fetched_size * 100) // total_size
                        if percent > last_percent:
                            last_percent = percent
                            update_context(f"Downloading {url} {percent:3}%")

def _download_link(self, operation, link):
    package = operation.package
    output_dir = self._artifact_cache.get_cache_directory_for_link(link)
    original_archive = self._artifact_cache.get_cached_archive_for_link(
        link, strict=True
    )
    if original_archive is None:
        try:
            original_archive = self._download_archive(operation, link)
        except BaseException:
            cache_directory = self._artifact_cache.get_cache_directory_for_link(
                link
            )
            cached_file = cache_directory.joinpath(link.filename)
            if cached_file.exists():
                cached_file.unlink()
            raise
    archive = self._artifact_cache.get_cached_archive_for_link(
        link,
        strict=False,
        env=self._env,
    )
    assert archive is not None
    if archive.suffix != ".whl":
        message = (
            f"  <fg=blue;options=bold>•</> {self.get_operation_message(operation)}:"
            " <info>Preparing...</info>"
        )
        self._write(operation, message)
        archive = self._chef.prepare(archive, output_dir=output_dir)
    self._populate_hashes_dict(original_archive, package)
    return archive

def activate(self, env):
    activate_script = self._get_activate_script()
    bin_dir = "Scripts" if WINDOWS else "bin"
    activate_path = env.path / bin_dir / activate_script
    if sys.platform == "win32":
        args = None
        if self._name in ("powershell", "pwsh"):
            args = ["-NoExit", "-File", str(activate_path)]
        elif self._name == "cmd":
            args = ["/K", str(activate_path)]
        if args:
            completed_proc = subprocess.run([self.path, *args])
            return completed_proc.returncode
        else:
            return env.execute(self._path)
    import shlex
    terminal = shutil.get_terminal_size()
    with env.temp_environ():
        c = pexpect.spawn(
            self._path, ["-i"], dimensions=(terminal.lines, terminal.columns)
        )
    if self._name in ["zsh", "nu"]:
        c.setecho(False)
        if self._name == "zsh":
            c.sendline(f"emulate bash -c '. {shlex.quote(str(activate_path))}'")
    else:
        c.sendline(
            f"{self._get_source_command()} {shlex.quote(str(activate_path))}"
        )
    def resize(sig, data):
        terminal = shutil.get_terminal_size()
        c.setwinsize(terminal.lines, terminal.columns)
    signal.signal(signal.SIGWINCH, resize)
    c.interact(escape_character=None)
    c.close()
    sys.exit(c.exitstatus)

def load(cls, env, with_dependencies = False):
    from poetry.core.packages.dependency import Dependency
    repo = cls()
    seen = set()
    skipped = set()
    for entry in reversed(env.sys_path):
        if not entry.strip():
            logger.debug(
                "Project environment contains an empty path in <c1>sys_path</>,"
                " ignoring."
            )
            continue
        for distribution in sorted(
            metadata.distributions(  
                path=[entry],
            ),
            key=lambda d: str(d._path),  
        ):
            path = Path(str(distribution._path))  
            if path in skipped:
                continue
            try:
                name = canonicalize_name(distribution.metadata["name"])
            except TypeError:
                logger.warning(
                    (
                        "Project environment contains an invalid distribution"
                        " (<c1>%s</>). Consider removing it manually or recreate"
                        " the environment."
                    ),
                    path,
                )
                skipped.add(path)
                continue
            if name in seen:
                continue
            package = cls.create_package_from_distribution(distribution, env)
            if with_dependencies:
                for require in distribution.metadata.get_all("requires-dist", []):
                    dep = Dependency.create_from_pep_508(require)
                    package.add_dependency(dep)
            seen.add(package.name)
            repo.add_package(package)
    return repo

def _run(self, cmd, **kwargs):
    call = kwargs.pop("call", False)
    input_ = kwargs.pop("input_", None)
    env = kwargs.pop("env", dict(os.environ))
    stderr = kwargs.pop("stderr", subprocess.STDOUT)
    try:
        if input_:
            output = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=stderr,
                input=encode(input_),
                check=True,
                **kwargs,
            ).stdout
        elif call:
            return subprocess.call(
                cmd, stdout=subprocess.PIPE, stderr=stderr, env=env, **kwargs
            )
        else:
            output = subprocess.check_output(cmd, stderr=stderr, env=env, **kwargs)
    except CalledProcessError as e:
        raise EnvCommandError(e, input=input_)
    return decode(output)

def _prepare(
    self, directory, destination, *, editable = False
):
    from subprocess import CalledProcessError
    with ephemeral_environment(self._env.python) as venv:
        env = IsolatedEnv(venv, self._pool)
        builder = ProjectBuilder(
            directory,
            python_executable=env.executable,
            scripts_dir=env.scripts_dir,
            runner=quiet_subprocess_runner,
        )
        env.install(builder.build_system_requires)
        stdout = StringIO()
        error = None
        try:
            with redirect_stdout(stdout):
                env.install(
                    builder.build_system_requires
                    | builder.get_requires_for_build("wheel")
                )
                path = Path(
                    builder.build(
                        "wheel" if not editable else "editable",
                        destination.as_posix(),
                    )
                )
        except BuildBackendException as e:
            message_parts = [str(e)]
            if isinstance(e.exception, CalledProcessError) and (
                e.exception.stdout is not None or e.exception.stderr is not None
            ):
                message_parts.append(
                    e.exception.stderr.decode()
                    if e.exception.stderr is not None
                    else e.exception.stdout.decode()
                )
            error = ChefBuildError("\n\n".join(message_parts))
        if error is not None:
            raise error from None
        return path

def locked_repository(self):
    from poetry.factory import Factory
    from poetry.repositories.lockfile_repository import LockfileRepository
    repository = LockfileRepository()
    if not self.is_locked():
        return repository
    lock_data = self.lock_data
    locked_packages = cast("list[dict[str, Any]]", lock_data["package"])
    if not locked_packages:
        return repository
    for info in locked_packages:
        source = info.get("source", {})
        source_type = source.get("type")
        url = source.get("url")
        if source_type in ["directory", "file"]:
            url = self.lock.parent.joinpath(url).resolve().as_posix()
        name = info["name"]
        package = Package(
            name,
            info["version"],
            info["version"],
            source_type=source_type,
            source_url=url,
            source_reference=source.get("reference"),
            source_resolved_reference=source.get("resolved_reference"),
            source_subdirectory=source.get("subdirectory"),
        )
        package.description = info.get("description", "")
        package.category = info.get("category", "main")
        package.optional = info["optional"]
        metadata = cast("dict[str, Any]", lock_data["metadata"])
        package_files = info.get("files")
        if package_files is not None:
            package.files = package_files
        elif "hashes" in metadata:
            hashes = cast("dict[str, Any]", metadata["hashes"])
            package.files = [{"name": h, "hash": h} for h in hashes[name]]
        elif source_type in {"git", "directory", "url"}:
            package.files = []
        else:
            files = metadata["files"][name]
            if source_type == "file":
                filename = Path(url).name
                package.files = [item for item in files if item["file"] == filename]
            else:
                package.files = files
        package.python_versions = info["python-versions"]
        extras = info.get("extras", {})
        if extras:
            for name, deps in extras.items():
                name = canonicalize_name(name)
                package.extras[name] = []
                for dep in deps:
                    try:
                        dependency = Dependency.create_from_pep_508(dep)
                    except InvalidRequirement:
                        m = re.match(r"^(.+?)(?:\[(.+?)])?(?:\s+\((.+)\))?$", dep)
                        if not m:
                            raise
                        dep_name = m.group(1)
                        extras = m.group(2) or ""
                        constraint = m.group(3) or "*"
                        dependency = Dependency(
                            dep_name, constraint, extras=extras.split(",")
                        )
                    package.extras[name].append(dependency)
        if "marker" in info:
            package.marker = parse_marker(info["marker"])
        else:
            if "requirements" in info:
                dep = Dependency("foo", "0.0.0")
                for name, value in info["requirements"].items():
                    if name == "python":
                        dep.python_versions = value
                    elif name == "platform":
                        dep.platform = value
                split_dep = dep.to_pep_508(False).split(";")
                if len(split_dep) > 1:
                    package.marker = parse_marker(split_dep[1].strip())
        for dep_name, constraint in info.get("dependencies", {}).items():
            root_dir = self.lock.parent
            if package.source_type == "directory":
                assert package.source_url is not None
                root_dir = Path(package.source_url)
            if isinstance(constraint, list):
                for c in constraint:
                    package.add_dependency(
                        Factory.create_dependency(dep_name, c, root_dir=root_dir)
                    )
                continue
            package.add_dependency(
                Factory.create_dependency(dep_name, constraint, root_dir=root_dir)
            )
        if "develop" in info:
            package.develop = info["develop"]
        repository.add_package(package)
    return repository

def _add_dist_info(self, added_files):
    from poetry.core.masonry.builders.wheel import WheelBuilder
    added_files = added_files[:]
    builder = WheelBuilder(self._poetry)
    dist_info = self._env.site_packages.mkdir(Path(builder.dist_info))
    self._debug(
        f"  - Adding the <c2>{dist_info.name}</c2> directory to"
        f" <b>{dist_info.parent}</b>"
    )
    with dist_info.joinpath("METADATA").open("w", encoding="utf-8") as f:
        builder._write_metadata_file(f)
    added_files.append(dist_info.joinpath("METADATA"))
    with dist_info.joinpath("INSTALLER").open("w", encoding="utf-8") as f:
        f.write("poetry")
    added_files.append(dist_info.joinpath("INSTALLER"))
    if self.convert_entry_points():
        with dist_info.joinpath("entry_points.txt").open(
            "w", encoding="utf-8"
        ) as f:
            builder._write_entry_points(f)
        added_files.append(dist_info.joinpath("entry_points.txt"))
    direct_url_json = dist_info.joinpath("direct_url.json")
    direct_url_json.write_text(
        json.dumps(
            {
                "dir_info": {"editable": True},
                "url": self._poetry.file.path.parent.as_uri(),
            }
        )
    )
    added_files.append(direct_url_json)
    record = dist_info.joinpath("RECORD")
    with record.open("w", encoding="utf-8", newline="") as f:
        csv_writer = csv.writer(f)
        for path in added_files:
            hash = self._get_file_hash(path)
            size = path.stat().st_size
            csv_writer.writerow((path, f"sha256={hash}", size))
        csv_writer.writerow((record, "", ""))

def validate_object(obj):
    schema_file = Path(SCHEMA_DIR, "poetry.json")
    schema = json.loads(schema_file.read_text(encoding="utf-8"))
    validator = jsonschema.Draft7Validator(schema)
    validation_errors = sorted(
        validator.iter_errors(obj),
        key=lambda e: e.path,  
    )
    errors = []
    for error in validation_errors:
        message = error.message
        if error.path:
            path = ".".join(str(x) for x in error.absolute_path)
            message = f"[{path}] {message}"
        errors.append(message)
    core_schema = json.loads(
        Path(CORE_SCHEMA_DIR, "poetry-schema.json").read_text(encoding="utf-8")
    )
    if core_schema["additionalProperties"]:
        properties = {*schema["properties"].keys(), *core_schema["properties"].keys()}
        additional_properties = set(obj.keys()) - properties
        for key in additional_properties:
            errors.append(
                f"Additional properties are not allowed ('{key}' was unexpected)"
            )
    return errors

def _get_links(self, package):
    if package.source_type:
        assert package.source_reference is not None
        repository = self._pool.repository(package.source_reference)
    elif not self._pool.has_repository("pypi"):
        repository = self._pool.repositories[0]
    else:
        repository = self._pool.repository("pypi")
    links = repository.find_links_for_package(package)
    hashes = [f["hash"] for f in package.files]
    if not hashes:
        return links
    selected_links = []
    for link in links:
        if not link.hash:
            selected_links.append(link)
            continue
        assert link.hash_name is not None
        h = link.hash_name + ":" + link.hash
        if h not in hashes:
            logger.debug(
                "Skipping %s as %s checksum does not match expected value",
                link.filename,
                link.hash_name,
            )
            continue
        selected_links.append(link)
    if links and not selected_links:
        raise RuntimeError(
            f"Retrieved digest for link {link.filename}({h}) not in poetry.lock"
            f" metadata {hashes}"
        )
    return selected_links

def handle(self):
    from pathlib import Path
    from poetry.core.vcs.git import GitConfig
    from poetry.layouts import layout
    from poetry.utils.env import SystemEnv
    if self.option("src"):
        layout_cls = layout("src")
    else:
        layout_cls = layout("standard")
    path = Path(self.argument("path"))
    if not path.is_absolute():
        path = Path.cwd().joinpath(path)
    name = self.option("name")
    if not name:
        name = path.name
    if path.exists() and list(path.glob("*")):
        raise RuntimeError(
            f"Destination <fg=yellow>{path}</> exists and is not empty"
        )
    readme_format = self.option("readme") or "md"
    config = GitConfig()
    author = None
    if config.get("user.name"):
        author = config["user.name"]
        author_email = config.get("user.email")
        if author_email:
            author += f" <{author_email}>"
    current_env = SystemEnv(Path(sys.executable))
    default_python = "^" + ".".join(str(v) for v in current_env.version_info[:2])
    layout_ = layout_cls(
        name,
        "0.1.0",
        author=author,
        readme_format=readme_format,
        python=default_python,
    )
    layout_.create(path)
    path = path.resolve()
    with suppress(ValueError):
        path = path.relative_to(Path.cwd())
    self.line(
        f"Created package <info>{layout_._package_name}</> in"
        f" <fg=blue>{path.as_posix()}</>"
    )
    return 0

def do_benchmark(number):
    setup = "import __main__ as z"
    print(f"Benchmark when {number = }:")
    print(f"{get_set_bits_count_using_modulo_operator(number) = }")
    timing = timeit("z.get_set_bits_count_using_modulo_operator(25)", setup=setup)
    print(f"timeit() runs in {timing} seconds")
    print(f"{get_set_bits_count_using_brian_kernighans_algorithm(number) = }")
    timing = timeit(
        "z.get_set_bits_count_using_brian_kernighans_algorithm(25)",
        setup=setup,
    )
    print(f"timeit() runs in {timing} seconds")

def armstrong_number(n):
    if not isinstance(n, int) or n < 1:
        return False
    total = 0
    number_of_digits = 0
    temp = n
    while temp > 0:
        number_of_digits += 1
        temp //= 10
    temp = n
    while temp > 0:
        rem = temp % 10
        total += rem**number_of_digits
        temp //= 10
    return n == total

def predict(self, input_arr):
    self.array = input_arr
    self.layer_between_input_and_first_hidden_layer = sigmoid(
        numpy.dot(self.array, self.input_layer_and_first_hidden_layer_weights)
    )
    self.layer_between_first_hidden_layer_and_second_hidden_layer = sigmoid(
        numpy.dot(
            self.layer_between_input_and_first_hidden_layer,
            self.first_hidden_layer_and_second_hidden_layer_weights,
        )
    )
    self.layer_between_second_hidden_layer_and_output = sigmoid(
        numpy.dot(
            self.layer_between_first_hidden_layer_and_second_hidden_layer,
            self.second_hidden_layer_and_output_layer_weights,
        )
    )
    return int(self.layer_between_second_hidden_layer_and_output > 0.6)

def find_missing_number(nums):
    n = len(nums)
    missing_number = n
    for i in range(n):
        missing_number ^= i ^ nums[i]
    return missing_number

def main():
    california = fetch_california_housing()
    data, target = data_handling(california)
    x_train, x_test, y_train, y_test = train_test_split(
        data, target, test_size=0.25, random_state=1
    )
    predictions = xgboost(x_train, y_train, x_test)
    print(f"Mean Absolute Error : {mean_absolute_error(y_test, predictions)}")
    print(f"Mean Square Error  : {mean_squared_error(y_test, predictions)}")

def euler_phi(n):
    s = n
    for x in set(prime_factors(n)):
        s *= (x - 1) / x
    return int(s)

def report_generator(
    df, clustering_variables, fill_missing_report=None
):
    if fill_missing_report:
        df = df.fillna(value=fill_missing_report)
    df["dummy"] = 1
    numeric_cols = df.select_dtypes(np.number).columns
    report = (
        df.groupby(["Cluster"])[  
            numeric_cols
        ]  
        .agg(
            [
                ("sum", np.sum),
                ("mean_with_zeros", lambda x: np.mean(np.nan_to_num(x))),
                ("mean_without_zeros", lambda x: x.replace(0, np.NaN).mean()),
                (
                    "mean_25-75",
                    lambda x: np.mean(
                        np.nan_to_num(
                            sorted(x)[
                                round(len(x) * 25 / 100) : round(len(x) * 75 / 100)
                            ]
                        )
                    ),
                ),
                ("mean_with_na", np.mean),
                ("min", lambda x: x.min()),
                ("5%", lambda x: x.quantile(0.05)),
                ("25%", lambda x: x.quantile(0.25)),
                ("50%", lambda x: x.quantile(0.50)),
                ("75%", lambda x: x.quantile(0.75)),
                ("95%", lambda x: x.quantile(0.95)),
                ("max", lambda x: x.max()),
                ("count", lambda x: x.count()),
                ("stdev", lambda x: x.std()),
                ("mode", lambda x: x.mode()[0]),
                ("median", lambda x: x.median()),
                ("# > 0", lambda x: (x > 0).sum()),
            ]
        )
        .T.reset_index()
        .rename(index=str, columns={"level_0": "Features", "level_1": "Type"})
    )  
    clustersize = report[
        (report["Features"] == "dummy") & (report["Type"] == "count")
    ].copy()  
    clustersize.Type = (
        "ClusterSize"  
    )
    clustersize.Features = "# of Customers"
    clusterproportion = pd.DataFrame(
        clustersize.iloc[:, 2:].values
        / clustersize.iloc[:, 2:].values.sum()  
    )
    clusterproportion[
        "Type"
    ] = "% of Customers"  
    clusterproportion["Features"] = "ClusterProportion"
    cols = clusterproportion.columns.tolist()
    cols = cols[-2:] + cols[:-2]
    clusterproportion = clusterproportion[cols]  
    clusterproportion.columns = report.columns
    a = pd.DataFrame(
        abs(
            report[report["Type"] == "count"].iloc[:, 2:].values
            - clustersize.iloc[:, 2:].values
        )
    )  
    a["Features"] = 0
    a["Type"] = "# of nan"
    a.Features = report[
        report["Type"] == "count"
    ].Features.tolist()  
    cols = a.columns.tolist()
    cols = cols[-2:] + cols[:-2]
    a = a[cols]  
    a.columns = report.columns  
    report = report.drop(
        report[report.Type == "count"].index
    )  
    report = pd.concat(
        [report, a, clustersize, clusterproportion], axis=0
    )  
    report["Mark"] = report["Features"].isin(clustering_variables)
    cols = report.columns.tolist()
    cols = cols[0:2] + cols[-1:] + cols[2:-1]
    report = report[cols]
    sorter1 = {
        "ClusterSize": 9,
        "ClusterProportion": 8,
        "mean_with_zeros": 7,
        "mean_with_na": 6,
        "max": 5,
        "50%": 4,
        "min": 3,
        "25%": 2,
        "75%": 1,
        "# of nan": 0,
        "# > 0": -1,
        "sum_with_na": -2,
    }
    report = (
        report.assign(
            Sorter1=lambda x: x.Type.map(sorter1),
            Sorter2=lambda x: list(reversed(range(len(x)))),
        )
        .sort_values(["Sorter1", "Mark", "Sorter2"], ascending=False)
        .drop(["Sorter1", "Sorter2"], axis=1)
    )
    report.columns.name = ""
    report = report.reset_index()
    report = report.drop(columns=["index"])
    return report

def coulombs_law(q1, q2, radius):
    if radius <= 0:
        raise ValueError("The radius is always a positive non zero integer")
    return round(((8.9875517923 * 10**9) * q1 * q2) / (radius**2), 2)

def bin_exp_mod(a, n, b):
    assert b != 0, "This cannot accept modulo that is == 0"
    if n == 0:
        return 1
    if n % 2 == 1:
        return (bin_exp_mod(a, n - 1, b) * a) % b
    r = bin_exp_mod(a, n / 2, b)
    return (r * r) % b

def binary_exponentiation(a, n):
    if n == 0:
        return 1
    elif n % 2 == 1:
        return binary_exponentiation(a, n - 1) * a
    else:
        b = binary_exponentiation(a, n / 2)
        return b * b

def local_weight_regression(
    x_train, y_train, tau
):
    y_pred = np.zeros(len(x_train))  
    for i, item in enumerate(x_train):
        y_pred[i] = np.dot(item, local_weight(item, x_train, y_train, tau))
    return y_pred

def local_weight_regression(
    x_train, y_train, tau
):
    y_pred = np.zeros(len(x_train))  
    for i, item in enumerate(x_train):
        y_pred[i] = item @ local_weight(item, x_train, y_train, tau)
    return y_pred

def xgboost(
    features, target, test_features
):
    xgb = XGBRegressor(verbosity=0, random_state=42)
    xgb.fit(features, target)
    predictions = xgb.predict(test_features)
    predictions = predictions.reshape(len(predictions), 1)
    return predictions

def jacobi_iteration_method(
    coefficient_matrix,
    constant_matrix,
    init_val,
    iterations,
):
    rows1, cols1 = coefficient_matrix.shape
    rows2, cols2 = constant_matrix.shape
    if rows1 != cols1:
        msg = f"Coefficient matrix dimensions must be nxn but received {rows1}x{cols1}"
        raise ValueError(msg)
    if cols2 != 1:
        msg = f"Constant matrix must be nx1 but received {rows2}x{cols2}"
        raise ValueError(msg)
    if rows1 != rows2:
        msg = (
            "Coefficient and constant matrices dimensions must be nxn and nx1 but "
            f"received {rows1}x{cols1} and {rows2}x{cols2}"
        )
        raise ValueError(msg)
    if len(init_val) != rows1:
        msg = (
            "Number of initial values must be equal to number of rows in coefficient "
            f"matrix but received {len(init_val)} and {rows1}"
        )
        raise ValueError(msg)
    if iterations <= 0:
        raise ValueError("Iterations must be at least 1")
    table = np.concatenate(
        (coefficient_matrix, constant_matrix), axis=1
    )
    rows, cols = table.shape
    strictly_diagonally_dominant(table)
    for _ in range(iterations):
        new_val = []
        for row in range(rows):
            temp = 0
            for col in range(cols):
                if col == row:
                    denom = table[row][col]
                elif col == cols - 1:
                    val = table[row][col]
                else:
                    temp += (-1) * table[row][col] * init_val[col]
            temp = (temp + val) / denom
            new_val.append(temp)
        init_val = new_val
    return [float(i) for i in new_val]

def _unique_indicator(y):
    return np.arange(
        check_array(y, input_name="y", accept_sparse=["csr", "csc", "coo"]).shape[1]
    )

def check_array(
    array,
    accept_sparse=False,
    *,
    accept_large_sparse=True,
    dtype="numeric",
    order=None,
    copy=False,
    force_all_finite=True,
    ensure_2d=True,
    allow_nd=False,
    ensure_min_samples=1,
    ensure_min_features=1,
    estimator=None,
    input_name="",
):
    if isinstance(array, np.matrix):
        raise TypeError(
            "np.matrix is not supported. Please convert to a numpy array with "
            "np.asarray. For more information see: "
            "https://numpy.org/doc/stable/reference/generated/numpy.matrix.html"
        )
    xp, is_array_api_compliant = get_namespace(array)
    array_orig = array
    dtype_numeric = isinstance(dtype, str) and dtype == "numeric"
    dtype_orig = getattr(array, "dtype", None)
    if not is_array_api_compliant and not hasattr(dtype_orig, "kind"):
        dtype_orig = None
    dtypes_orig = None
    pandas_requires_conversion = False
    if hasattr(array, "dtypes") and hasattr(array.dtypes, "__array__"):
        with suppress(ImportError):
            from pandas import SparseDtype
            def is_sparse(dtype):
                return isinstance(dtype, SparseDtype)
            if not hasattr(array, "sparse") and array.dtypes.apply(is_sparse).any():
                warnings.warn(
                    "pandas.DataFrame with sparse columns found."
                    "It will be converted to a dense numpy array."
                )
        dtypes_orig = list(array.dtypes)
        pandas_requires_conversion = any(
            _pandas_dtype_needs_early_conversion(i) for i in dtypes_orig
        )
        if all(isinstance(dtype_iter, np.dtype) for dtype_iter in dtypes_orig):
            dtype_orig = np.result_type(*dtypes_orig)
        elif pandas_requires_conversion and any(d == object for d in dtypes_orig):
            dtype_orig = object
    elif (_is_extension_array_dtype(array) or hasattr(array, "iloc")) and hasattr(
        array, "dtype"
    ):
        pandas_requires_conversion = _pandas_dtype_needs_early_conversion(array.dtype)
        if isinstance(array.dtype, np.dtype):
            dtype_orig = array.dtype
        else:
            dtype_orig = None
    if dtype_numeric:
        if (
            dtype_orig is not None
            and hasattr(dtype_orig, "kind")
            and dtype_orig.kind == "O"
        ):
            dtype = xp.float64
        else:
            dtype = None
    if isinstance(dtype, (list, tuple)):
        if dtype_orig is not None and dtype_orig in dtype:
            dtype = None
        else:
            dtype = dtype[0]
    if pandas_requires_conversion:
        new_dtype = dtype_orig if dtype is None else dtype
        array = array.astype(new_dtype)
        dtype = None
    if dtype is not None and _is_numpy_namespace(xp):
        dtype = np.dtype(dtype)
    if force_all_finite not in (True, False, "allow-nan"):
        raise ValueError(
            'force_all_finite should be a bool or "allow-nan". Got {!r} instead'.format(
                force_all_finite
            )
        )
    if dtype is not None and _is_numpy_namespace(xp):
        dtype = np.dtype(dtype)
    estimator_name = _check_estimator_name(estimator)
    context = " by %s" % estimator_name if estimator is not None else ""
    if hasattr(array, "sparse") and array.ndim > 1:
        with suppress(ImportError):
            from pandas import SparseDtype  
            def is_sparse(dtype):
                return isinstance(dtype, SparseDtype)
            if array.dtypes.apply(is_sparse).all():
                array = array.sparse.to_coo()
                if array.dtype == np.dtype("object"):
                    unique_dtypes = set([dt.subtype.name for dt in array_orig.dtypes])
                    if len(unique_dtypes) > 1:
                        raise ValueError(
                            "Pandas DataFrame with mixed sparse extension arrays "
                            "generated a sparse matrix with object dtype which "
                            "can not be converted to a scipy sparse matrix."
                            "Sparse extension arrays should all have the same "
                            "numeric type."
                        )
    if sp.issparse(array):
        _ensure_no_complex_data(array)
        array = _ensure_sparse_format(
            array,
            accept_sparse=accept_sparse,
            dtype=dtype,
            copy=copy,
            force_all_finite=force_all_finite,
            accept_large_sparse=accept_large_sparse,
            estimator_name=estimator_name,
            input_name=input_name,
        )
    else:
        with warnings.catch_warnings():
            try:
                warnings.simplefilter("error", ComplexWarning)
                if dtype is not None and xp.isdtype(dtype, "integral"):
                    array = _asarray_with_order(array, order=order, xp=xp)
                    if xp.isdtype(array.dtype, ("real floating", "complex floating")):
                        _assert_all_finite(
                            array,
                            allow_nan=False,
                            msg_dtype=dtype,
                            estimator_name=estimator_name,
                            input_name=input_name,
                        )
                    array = xp.astype(array, dtype, copy=False)
                else:
                    array = _asarray_with_order(array, order=order, dtype=dtype, xp=xp)
            except ComplexWarning as complex_warning:
                raise ValueError(
                    "Complex data not supported\n{}\n".format(array)
                ) from complex_warning
        _ensure_no_complex_data(array)
        if ensure_2d:
            if array.ndim == 0:
                raise ValueError(
                    "Expected 2D array, got scalar array instead:\narray={}.\n"
                    "Reshape your data either using array.reshape(-1, 1) if "
                    "your data has a single feature or array.reshape(1, -1) "
                    "if it contains a single sample.".format(array)
                )
            if array.ndim == 1:
                raise ValueError(
                    "Expected 2D array, got 1D array instead:\narray={}.\n"
                    "Reshape your data either using array.reshape(-1, 1) if "
                    "your data has a single feature or array.reshape(1, -1) "
                    "if it contains a single sample.".format(array)
                )
        if dtype_numeric and hasattr(array.dtype, "kind") and array.dtype.kind in "USV":
            raise ValueError(
                "dtype='numeric' is not compatible with arrays of bytes/strings."
                "Convert your data to numeric values explicitly instead."
            )
        if not allow_nd and array.ndim >= 3:
            raise ValueError(
                "Found array with dim %d. %s expected <= 2."
                % (array.ndim, estimator_name)
            )
        if force_all_finite:
            _assert_all_finite(
                array,
                input_name=input_name,
                estimator_name=estimator_name,
                allow_nan=force_all_finite == "allow-nan",
            )
        if copy:
            if _is_numpy_namespace(xp):
                if np.may_share_memory(array, array_orig):
                    array = _asarray_with_order(
                        array, dtype=dtype, order=order, copy=True, xp=xp
                    )
            else:
                array = _asarray_with_order(
                    array, dtype=dtype, order=order, copy=True, xp=xp
                )
    if ensure_min_samples > 0:
        n_samples = _num_samples(array)
        if n_samples < ensure_min_samples:
            raise ValueError(
                "Found array with %d sample(s) (shape=%s) while a"
                " minimum of %d is required%s."
                % (n_samples, array.shape, ensure_min_samples, context)
            )
    if ensure_min_features > 0 and array.ndim == 2:
        n_features = array.shape[1]
        if n_features < ensure_min_features:
            raise ValueError(
                "Found array with %d feature(s) (shape=%s) while"
                " a minimum of %d is required%s."
                % (n_features, array.shape, ensure_min_features, context)
            )
    return array

def _fit_stochastic(
    self,
    X,
    y,
    activations,
    deltas,
    coef_grads,
    intercept_grads,
    layer_units,
    incremental,
):
    params = self.coefs_ + self.intercepts_
    if not incremental or not hasattr(self, "_optimizer"):
        if self.solver == "sgd":
            self._optimizer = SGDOptimizer(
                params,
                self.learning_rate_init,
                self.learning_rate,
                self.momentum,
                self.nesterovs_momentum,
                self.power_t,
            )
        elif self.solver == "adam":
            self._optimizer = AdamOptimizer(
                params,
                self.learning_rate_init,
                self.beta_1,
                self.beta_2,
                self.epsilon,
            )
    if self.early_stopping and incremental:
        raise ValueError("partial_fit does not support early_stopping=True")
    early_stopping = self.early_stopping
    if early_stopping:
        should_stratify = is_classifier(self) and self.n_outputs_ == 1
        stratify = y if should_stratify else None
        X, X_val, y, y_val = train_test_split(
            X,
            y,
            random_state=self._random_state,
            test_size=self.validation_fraction,
            stratify=stratify,
        )
        if is_classifier(self):
            y_val = self._label_binarizer.inverse_transform(y_val)
    else:
        X_val = None
        y_val = None
    n_samples = X.shape[0]
    sample_idx = np.arange(n_samples, dtype=int)
    if self.batch_size == "auto":
        batch_size = min(200, n_samples)
    else:
        if self.batch_size > n_samples:
            warnings.warn(
                "Got `batch_size` less than 1 or larger than "
                "sample size. It is going to be clipped"
            )
        batch_size = np.clip(self.batch_size, 1, n_samples)
    try:
        self.n_iter_ = 0
        for it in range(self.max_iter):
            if self.shuffle:
                sample_idx = shuffle(sample_idx, random_state=self._random_state)
            accumulated_loss = 0.0
            for batch_slice in gen_batches(n_samples, batch_size):
                if self.shuffle:
                    X_batch = _safe_indexing(X, sample_idx[batch_slice])
                    y_batch = y[sample_idx[batch_slice]]
                else:
                    X_batch = X[batch_slice]
                    y_batch = y[batch_slice]
                activations[0] = X_batch
                batch_loss, coef_grads, intercept_grads = self._backprop(
                    X_batch,
                    y_batch,
                    activations,
                    deltas,
                    coef_grads,
                    intercept_grads,
                )
                accumulated_loss += batch_loss * (
                    batch_slice.stop - batch_slice.start
                )
                grads = coef_grads + intercept_grads
                self._optimizer.update_params(params, grads)
            self.n_iter_ += 1
            self.loss_ = accumulated_loss / X.shape[0]
            self.t_ += n_samples
            self.loss_curve_.append(self.loss_)
            if self.verbose:
                print("Iteration %d, loss = %.8f" % (self.n_iter_, self.loss_))
            self._update_no_improvement_count(early_stopping, X_val, y_val)
            self._optimizer.iteration_ends(self.t_)
            if self._no_improvement_count > self.n_iter_no_change:
                if early_stopping:
                    msg = (
                        "Validation score did not improve more than "
                        "tol=%f for %d consecutive epochs."
                        % (self.tol, self.n_iter_no_change)
                    )
                else:
                    msg = (
                        "Training loss did not improve more than tol=%f"
                        " for %d consecutive epochs."
                        % (self.tol, self.n_iter_no_change)
                    )
                is_stopping = self._optimizer.trigger_stopping(msg, self.verbose)
                if is_stopping:
                    break
                else:
                    self._no_improvement_count = 0
            if incremental:
                break
            if self.n_iter_ == self.max_iter:
                warnings.warn(
                    "Stochastic Optimizer: Maximum iterations (%d) "
                    "reached and the optimization hasn't converged yet."
                    % self.max_iter,
                    ConvergenceWarning,
                )
    except KeyboardInterrupt:
        warnings.warn("Training interrupted by user.")
    if early_stopping:
        self.coefs_ = self._best_coefs
        self.intercepts_ = self._best_intercepts
        self.validation_scores_ = self.validation_scores_

def plot_n_features_influence(percentiles, percentile):
    fig, ax1 = plt.subplots(figsize=(10, 6))
    colors = ["r", "g", "b"]
    for i, cls_name in enumerate(percentiles.keys()):
        x = np.array(sorted([n for n in percentiles[cls_name].keys()]))
        y = np.array([percentiles[cls_name][n] for n in x])
        plt.plot(
            x,
            y,
            color=colors[i],
        )
    ax1.yaxis.grid(True, linestyle="-", which="major", color="lightgrey", alpha=0.5)
    ax1.set_axisbelow(True)
    ax1.set_title("Evolution of Prediction Time with #Features")
    ax1.set_xlabel("#Features")
    ax1.set_ylabel("Prediction Time at %d%%-ile (us)" % percentile)
    plt.show()

def plot(self, *, ax=None, name=None, ref_line=True, **kwargs):
    self.ax_, self.figure_, name = self._validate_plot_params(ax=ax, name=name)
    info_pos_label = (
        f"(Positive class: {self.pos_label})" if self.pos_label is not None else ""
    )
    line_kwargs = {}
    if name is not None:
        line_kwargs["label"] = name
    line_kwargs.update(**kwargs)
    ref_line_label = "Perfectly calibrated"
    existing_ref_line = ref_line_label in self.ax_.get_legend_handles_labels()[1]
    if ref_line and not existing_ref_line:
        self.ax_.plot([0, 1], [0, 1], "k:", label=ref_line_label)
    self.line_ = self.ax_.plot(self.prob_pred, self.prob_true, "s-", **line_kwargs)[
        0
    ]
    self.ax_.legend(loc="lower right")
    xlabel = f"Mean predicted probability {info_pos_label}"
    ylabel = f"Fraction of positives {info_pos_label}"
    self.ax_.set(xlabel=xlabel, ylabel=ylabel)
    return self

def transform(self, X):
    X_ordinal, X_valid = self._transform(
        X, handle_unknown="ignore", force_all_finite="allow-nan"
    )
    X_out = np.empty_like(X_ordinal, dtype=np.float64)
    self._transform_X_ordinal(
        X_out,
        X_ordinal,
        ~X_valid,
        slice(None),
        self.encodings_,
        self.target_mean_,
    )
    return X_out

def check_conda_version():
    conda_info_output = execute_command(["conda", "info", "--json"])
    conda_info = json.loads(conda_info_output)
    conda_version = Version(conda_info["conda_version"])
    if Version("22.9.0") < conda_version < Version("23.6"):
        raise RuntimeError(
            f"conda version should be <= 22.9.0 or >= 23.6 got: {conda_version}"
        )

def fit(self, X, y, sample_weight=None, monitor=None):
    if not self.warm_start:
        self._clear_state()
    X, y = self._validate_data(
        X, y, accept_sparse=["csr", "csc", "coo"], dtype=DTYPE, multi_output=True
    )
    sample_weight_is_none = sample_weight is None
    sample_weight = _check_sample_weight(sample_weight, X)
    y = column_or_1d(y, warn=True)
    if is_classifier(self):
        y = self._validate_y(y, sample_weight)
    else:
        y = self._validate_y(y)
    self._check_params()
    if self.n_iter_no_change is not None:
        stratify = y if is_classifier(self) else None
        X, X_val, y, y_val, sample_weight, sample_weight_val = train_test_split(
            X,
            y,
            sample_weight,
            random_state=self.random_state,
            test_size=self.validation_fraction,
            stratify=stratify,
        )
        if is_classifier(self):
            if self._n_classes != np.unique(y).shape[0]:
                raise ValueError(
                    "The training data after the early stopping split "
                    "is missing some classes. Try using another random "
                    "seed."
                )
    else:
        X_val = y_val = sample_weight_val = None
    if not self._is_initialized():
        self._init_state()
        if self.init_ == "zero":
            raw_predictions = np.zeros(
                shape=(X.shape[0], self._loss.K), dtype=np.float64
            )
        else:
            if sample_weight_is_none:
                self.init_.fit(X, y)
            else:
                msg = (
                    "The initial estimator {} does not support sample "
                    "weights.".format(self.init_.__class__.__name__)
                )
                try:
                    self.init_.fit(X, y, sample_weight=sample_weight)
                except TypeError as e:
                    if "unexpected keyword argument 'sample_weight'" in str(e):
                        raise ValueError(msg) from e
                    else:  
                        raise
                except ValueError as e:
                    if (
                        "pass parameters to specific steps of "
                        "your pipeline using the "
                        "stepname__parameter"
                        in str(e)
                    ):  
                        raise ValueError(msg) from e
                    else:  
                        raise
            raw_predictions = self._loss.get_init_raw_predictions(X, self.init_)
        begin_at_stage = 0
        self._rng = check_random_state(self.random_state)
    else:
        if self.n_estimators < self.estimators_.shape[0]:
            raise ValueError(
                "n_estimators=%d must be larger or equal to "
                "estimators_.shape[0]=%d when "
                "warm_start==True" % (self.n_estimators, self.estimators_.shape[0])
            )
        begin_at_stage = self.estimators_.shape[0]
        X = check_array(
            X,
            dtype=DTYPE,
            order="C",
            accept_sparse="csr",
            force_all_finite=False,
        )
        raw_predictions = self._raw_predict(X)
        self._resize_state()
    n_stages = self._fit_stages(
        X,
        y,
        raw_predictions,
        sample_weight,
        self._rng,
        X_val,
        y_val,
        sample_weight_val,
        begin_at_stage,
        monitor,
    )
    if n_stages != self.estimators_.shape[0]:
        self.estimators_ = self.estimators_[:n_stages]
        self.train_score_ = self.train_score_[:n_stages]
        if hasattr(self, "oob_improvement_"):
            self.oob_improvement_ = self.oob_improvement_[:n_stages]
            self.oob_scores_ = self.oob_scores_[:n_stages]
            self.oob_score_ = self.oob_scores_[-1]
    self.n_estimators_ = n_stages
    return self

def _init_centroids(
    self,
    X,
    x_squared_norms,
    init,
    random_state,
    init_size=None,
    n_centroids=None,
    sample_weight=None,
):
    n_samples = X.shape[0]
    n_clusters = self.n_clusters if n_centroids is None else n_centroids
    if init_size is not None and init_size < n_samples:
        init_indices = random_state.randint(0, n_samples, init_size)
        X = X[init_indices]
        x_squared_norms = x_squared_norms[init_indices]
        n_samples = X.shape[0]
        sample_weight = sample_weight[init_indices]
    if isinstance(init, str) and init == "k-means++":
        centers, _ = _kmeans_plusplus(
            X,
            n_clusters,
            random_state=random_state,
            x_squared_norms=x_squared_norms,
            sample_weight=sample_weight,
        )
    elif isinstance(init, str) and init == "random":
        seeds = random_state.choice(
            n_samples,
            size=n_clusters,
            replace=False,
            p=sample_weight / sample_weight.sum(),
        )
        centers = X[seeds]
    elif _is_arraylike_not_scalar(self.init):
        centers = init
    elif callable(init):
        centers = init(X, n_clusters, random_state=random_state)
        centers = check_array(centers, dtype=X.dtype, copy=False, order="C")
        self._validate_center_shape(X, centers)
    if sp.issparse(centers):
        centers = centers.toarray()
    return centers

def transform(self, X):
    check_is_fitted(self)
    X = self._validate_data(X, reset=False, accept_sparse=False, ensure_2d=True)
    n_samples, n_features = X.shape
    n_splines = self.bsplines_[0].c.shape[1]
    degree = self.degree
    scipy_1_10 = sp_version >= parse_version("1.10.0")
    if scipy_1_10:
        use_sparse = self.sparse_output
        kwargs_extrapolate = {"extrapolate": self.bsplines_[0].extrapolate}
    else:
        use_sparse = self.sparse_output and not self.bsplines_[0].extrapolate
        kwargs_extrapolate = dict()
    n_out = self.n_features_out_ + n_features * (1 - self.include_bias)
    if X.dtype in FLOAT_DTYPES:
        dtype = X.dtype
    else:
        dtype = np.float64
    if use_sparse:
        output_list = []
    else:
        XBS = np.zeros((n_samples, n_out), dtype=dtype, order=self.order)
    for i in range(n_features):
        spl = self.bsplines_[i]
        if self.extrapolation in ("continue", "error", "periodic"):
            if self.extrapolation == "periodic":
                n = spl.t.size - spl.k - 1
                x = spl.t[spl.k] + (X[:, i] - spl.t[spl.k]) % (
                    spl.t[n] - spl.t[spl.k]
                )
            else:
                x = X[:, i]
            if use_sparse:
                XBS_sparse = BSpline.design_matrix(
                    x, spl.t, spl.k, **kwargs_extrapolate
                )
                if self.extrapolation == "periodic":
                    XBS_sparse = XBS_sparse.tolil()
                    XBS_sparse[:, :degree] += XBS_sparse[:, -degree:]
                    XBS_sparse = XBS_sparse[:, :-degree]
            else:
                XBS[:, (i * n_splines) : ((i + 1) * n_splines)] = spl(x)
        else:  
            xmin, xmax = spl.t[degree], spl.t[-degree - 1]
            f_min, f_max = spl(xmin), spl(xmax)
            mask = (xmin <= X[:, i]) & (X[:, i] <= xmax)
            if use_sparse:
                mask_inv = ~mask
                x = X[:, i].copy()
                x[mask_inv] = spl.t[self.degree]
                XBS_sparse = BSpline.design_matrix(x, spl.t, spl.k)
                if np.any(mask_inv):
                    XBS_sparse = XBS_sparse.tolil()
                    XBS_sparse[mask_inv, :] = 0
            else:
                XBS[mask, (i * n_splines) : ((i + 1) * n_splines)] = spl(X[mask, i])
        if self.extrapolation == "error":
            if (use_sparse and np.any(np.isnan(XBS_sparse.data))) or (
                not use_sparse
                and np.any(
                    np.isnan(XBS[:, (i * n_splines) : ((i + 1) * n_splines)])
                )
            ):
                raise ValueError(
                    "X contains values beyond the limits of the knots."
                )
        elif self.extrapolation == "constant":
            mask = X[:, i] < xmin
            if np.any(mask):
                if use_sparse:
                    XBS_sparse = XBS_sparse.tolil()
                    XBS_sparse[mask, :degree] = f_min[:degree]
                else:
                    XBS[mask, (i * n_splines) : (i * n_splines + degree)] = f_min[
                        :degree
                    ]
            mask = X[:, i] > xmax
            if np.any(mask):
                if use_sparse:
                    XBS_sparse = XBS_sparse.tolil()
                    XBS_sparse[mask, -degree:] = f_max[-degree:]
                else:
                    XBS[
                        mask,
                        ((i + 1) * n_splines - degree) : ((i + 1) * n_splines),
                    ] = f_max[-degree:]
        elif self.extrapolation == "linear":
            fp_min, fp_max = spl(xmin, nu=1), spl(xmax, nu=1)
            if degree <= 1:
                degree += 1
            for j in range(degree):
                mask = X[:, i] < xmin
                if np.any(mask):
                    linear_extr = f_min[j] + (X[mask, i] - xmin) * fp_min[j]
                    if use_sparse:
                        XBS_sparse = XBS_sparse.tolil()
                        XBS_sparse[mask, j] = linear_extr
                    else:
                        XBS[mask, i * n_splines + j] = linear_extr
                mask = X[:, i] > xmax
                if np.any(mask):
                    k = n_splines - 1 - j
                    linear_extr = f_max[k] + (X[mask, i] - xmax) * fp_max[k]
                    if use_sparse:
                        XBS_sparse = XBS_sparse.tolil()
                        XBS_sparse[mask, k : k + 1] = linear_extr[:, None]
                    else:
                        XBS[mask, i * n_splines + k] = linear_extr
        if use_sparse:
            if not sparse.isspmatrix_csr(XBS_sparse):
                XBS_sparse = XBS_sparse.tocsr()
            output_list.append(XBS_sparse)
    if use_sparse:
        max_int32 = np.iinfo(np.int32).max
        all_int32 = True
        for mat in output_list:
            all_int32 &= mat.indices.dtype == np.int32
        if (
            sp_version < parse_version("1.9.2")
            and self.n_features_out_ > max_int32
            and all_int32
        ):
            raise ValueError(
                "In scipy versions `<1.9.2`, the function `scipy.sparse.hstack`"
                " produces negative columns when:\n1. The output shape contains"
                " `n_cols` too large to be represented by a 32bit signed"
                " integer.\n. All sub-matrices to be stacked have indices of"
                " dtype `np.int32`.\nTo avoid this error, either use a version"
                " of scipy `>=1.9.2` or alter the `SplineTransformer`"
                " transformer to produce fewer than 2^31 output features"
            )
        XBS = sparse.hstack(output_list)
    elif self.sparse_output:
        XBS = sparse.csr_matrix(XBS)
    if self.include_bias:
        return XBS
    else:
        indices = [j for j in range(XBS.shape[1]) if (j + 1) % n_splines != 0]
        return XBS[:, indices]

def remove_unnecessary_package_from_lock_file(build_metadata_list, build_name, package):
    build_metadata = None
    for metadata in build_metadata_list:
        if metadata["build_name"] == build_name:
            build_metadata = metadata
            break
    if build_metadata is None:
        raise ValueError(f"Could not find build metadata for {build_name}")
    folder_path = Path(build_metadata["folder"])
    platform = build_metadata["platform"]
    lock_file_basename = build_name
    if not lock_file_basename.endswith(platform):
        lock_file_basename = f"{lock_file_basename}_{platform}"
    lock_file_path = folder_path / f"{lock_file_basename}_conda.lock"
    with open(lock_file_path, "r") as f_read_only:
        lock_file_content = f_read_only.readlines()
        with open(lock_file_path, "w") as f_write:
            for line in lock_file_content:
                if package in line:
                    logger.debug(f"Removing {package} from {build_name} lock file")
                    logger.debug(f"Removed line: {line}")
                    continue
                f_write.write(line)

def _check_params_vs_input(self, X, default_n_init=None):
    if X.shape[0] < self.n_clusters:
        raise ValueError(
            f"n_samples={X.shape[0]} should be >= n_clusters={self.n_clusters}."
        )
    self._tol = _tolerance(X, self.tol)
    self._n_init = self.n_init
    if self._n_init == "warn":
        warnings.warn(
            (
                "The default value of `n_init` will change from "
                f"{default_n_init} to 'auto' in 1.4. Set the value of `n_init`"
                " explicitly to suppress the warning"
            ),
            FutureWarning,
        )
        self._n_init = default_n_init
    if self._n_init == "auto":
        if self.init == "k-means++":
            self._n_init = 1
        else:
            self._n_init = default_n_init
    if _is_arraylike_not_scalar(self.init) and self._n_init != 1:
        warnings.warn(
            (
                "Explicit initial center position passed: performing only"
                f" one init in {self.__class__.__name__} instead of "
                f"n_init={self._n_init}."
            ),
            RuntimeWarning,
            stacklevel=2,
        )
        self._n_init = 1

def check_classification_targets(y):
    y_type = type_of_target(y, input_name="y")
    if y_type not in [
        "binary",
        "multiclass",
        "multiclass-multioutput",
        "multilabel-indicator",
        "multilabel-sequences",
    ]:
        raise ValueError("Unknown label type: %r" % y_type)

def start(
    self, stop_after_crawl = True, install_signal_handlers = True
):
    from twisted.internet import reactor
    if stop_after_crawl:
        d = self.join()
        if d.called:
            return
        d.addBoth(self._stop_reactor)
    resolver_class = load_object(self.settings["DNS_RESOLVER"])
    resolver = create_instance(resolver_class, self.settings, self, reactor=reactor)
    resolver.install_on_reactor()
    tp = reactor.getThreadPool()
    tp.adjustPoolsize(maxthreads=self.settings.getint("REACTOR_THREADPOOL_MAXSIZE"))
    reactor.addSystemEventTrigger("before", "shutdown", self.stop)
    if install_signal_handlers:
        reactor.addSystemEventTrigger(
            "after", "startup", install_shutdown_handlers, self._signal_shutdown
        )
    reactor.run()  

def from_crawler(cls, crawler):
    interval = crawler.settings.getfloat("LOGSTATS_INTERVAL")
    try:
        ext_stats = crawler.settings.getdict("PERIODIC_LOG_STATS")
    except (TypeError, ValueError):
        ext_stats = (
            {"enabled": True}
            if crawler.settings.getbool("PERIODIC_LOG_STATS")
            else None
        )
    try:
        ext_delta = crawler.settings.getdict("PERIODIC_LOG_DELTA")
    except (TypeError, ValueError):
        ext_delta = (
            {"enabled": True}
            if crawler.settings.getbool("PERIODIC_LOG_DELTA")
            else None
        )
    ext_timing_enabled = crawler.settings.getbool(
        "PERIODIC_LOG_TIMING_ENABLED", False
    )
    if not interval:
        raise NotConfigured
    if not (ext_stats or ext_delta or ext_timing_enabled):
        raise NotConfigured
    o = cls(
        crawler.stats,
        interval,
        ext_stats,
        ext_delta,
        ext_timing_enabled,
    )
    crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
    crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
    return o

def __init__(
    self,
    uri,
    access_key=None,
    secret_key=None,
    acl=None,
    endpoint_url=None,
    region_name=None,
    *,
    feed_options=None,
    session_token=None,
):
    if not is_botocore_available():
        raise NotConfigured("missing botocore library")
    u = urlparse(uri)
    self.bucketname = u.hostname
    self.access_key = u.username or access_key
    self.secret_key = u.password or secret_key
    self.session_token = session_token
    self.keyname = u.path[1:]  
    self.acl = acl
    self.endpoint_url = endpoint_url
    self.region_name = region_name
    if IS_BOTO3_AVAILABLE:
        import boto3.session
        session = boto3.session.Session()
        self.s3_client = session.client(
            "s3",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            aws_session_token=self.session_token,
            endpoint_url=self.endpoint_url,
            region_name=self.region_name,
        )
    else:
        warnings.warn(
            "`botocore` usage has been deprecated for S3 feed "
            "export, please use `boto3` to avoid problems",
            category=ScrapyDeprecationWarning,
        )
        import botocore.session
        session = botocore.session.get_session()
        self.s3_client = session.create_client(
            "s3",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            aws_session_token=self.session_token,
            endpoint_url=self.endpoint_url,
            region_name=self.region_name,
        )
    if feed_options and feed_options.get("overwrite", True) is False:
        logger.warning(
            "S3 does not support appending to files. To "
            "suppress this warning, remove the overwrite "
            "option from your FEEDS setting or set it to True."
        )

def _get_commands_from_entry_points(inproject, group="scrapy.commands"):
    cmds = {}
    for entry_point in entry_points().get(group, {}):
        obj = entry_point.load()
        if inspect.isclass(obj):
            cmds[entry_point.name] = obj()
        else:
            raise Exception(f"Invalid entry point {entry_point.name}")
    return cmds

def spider_closed(self, spider):
    task = getattr(self, "task", False)
    if task and task.active():
        task.cancel()
    task_no_item = getattr(self, "task_no_item", False)
    if task_no_item.running:
        task_no_item.stop()

def inside_project():
    scrapy_module = os.environ.get("SCRAPY_SETTINGS_MODULE")
    if scrapy_module is not None:
        try:
            import_module(scrapy_module)
        except ImportError as exc:
            warnings.warn(
                f"Cannot import scrapy settings module {scrapy_module}: {exc}"
            )
        else:
            return True
    return bool(closest_scrapy_cfg())

def crawl(self, *args, **kwargs):
    if self.crawling:
        raise RuntimeError("Crawling already taking place")
    self.crawling = True
    try:
        self.spider = self._create_spider(*args, **kwargs)
        self.engine = self._create_engine()
        self.addons.check_configuration(self)
        start_requests = iter(self.spider.start_requests())
        yield self.engine.open_spider(self.spider, start_requests)
        yield defer.maybeDeferred(self.engine.start)
    except Exception:
        self.crawling = False
        if self.engine is not None:
            yield self.engine.close()
        raise

def param_allowed(self, stat_name, include, exclude):
    if not include and not exclude:
        return True
    for p in exclude:
        if p in stat_name:
            return False
    for p in include:
        if p in stat_name:
            return True
    return False

def _get_commands_from_entry_points(inproject, group="scrapy.commands"):
    cmds = {}
    for entry_point in entry_points(group):
        obj = entry_point.load()
        if inspect.isclass(obj):
            cmds[entry_point.name] = obj()
        else:
            raise Exception(f"Invalid entry point {entry_point.name}")
    return cmds

def from_crawler(cls, crawler):
    interval = crawler.settings.getfloat("LOGSTATS_INTERVAL")
    try:
        ext_stats = crawler.settings.getdict("PERIODIC_LOG_STATS")
    except ValueError:
        ext_stats = (
            {"enabled": True}
            if crawler.settings.getbool("PERIODIC_LOG_STATS")
            else None
        )
    try:
        ext_delta = crawler.settings.getdict("PERIODIC_LOG_DELTA")
    except ValueError:
        ext_delta = (
            {"enabled": True}
            if crawler.settings.getdict("PERIODIC_LOG_DELTA")
            else None
        )
    ext_timing_enabled = crawler.settings.getbool(
        "PERIODIC_LOG_TIMING_ENABLED", False
    )
    if not interval:
        raise NotConfigured
    if not (ext_stats or ext_delta or ext_timing_enabled):
        raise NotConfigured
    o = cls(
        crawler.stats,
        interval,
        ext_stats,
        ext_delta,
        ext_timing_enabled,
    )
    crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
    crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
    return o

def _start_new_batch(self, batch_id, uri, feed_options, spider, uri_template):
    storage = self._get_storage(uri, feed_options)
    file = storage.open(spider)
    if "postprocessing" in feed_options:
        file = PostProcessingManager(
            feed_options["postprocessing"], file, feed_options
        )
    exporter = self._get_exporter(
        file=file,
        format=feed_options["format"],
        fields_to_export=feed_options["fields"],
        encoding=feed_options["encoding"],
        indent=feed_options["indent"],
        **feed_options["item_export_kwargs"],
    )
    slot = FeedSlot(
        storage=storage,
        uri=uri,
        format=feed_options["format"],
        store_empty=feed_options["store_empty"],
        batch_id=batch_id,
        uri_template=uri_template,
        filter=self.filters[uri_template],
        feed_options=feed_options,
        spider=spider,
        exporters=self.exporters,
        settings=self.settings,
        crawler=getattr(self, "crawler", None),
    )
    return slot

def jmespath(self, query, **kwargs):
    return self.selector.jmespath(query, **kwargs)

def __call__(self, parser, namespace, values, option_string=None):
    value = str(values).encode("utf-8").decode("utf-8")
    value = value[1::] if re.match(r"^\$(.+)", value) else value
    setattr(namespace, self.dest, value)

def __call__(self, parser, namespace, values, option_string=None):
    value = str(values).encode("utf-8").decode("utf-8")
    items = re.findall(r"\$(.+)", value)
    value = items[0] if items else value
    setattr(namespace, self.dest, value)

def update_task_state(self, key, state, info):
    try:
        if state == celery_states.SUCCESS:
            self.success(key, info)
        elif state in (celery_states.FAILURE, celery_states.REVOKED):
            self.fail(key, info)
        elif state in (celery_states.STARTEDstate, celery_states.PENDING):
            pass
        else:
            self.log.info("Unexpected state for %s: %s", key, state)
    except Exception:
        self.log.exception("Error syncing the Celery executor, ignoring it.")

def poll_job_in_queue(self, location, jenkins_server):
    try_count = 0
    location += "/api/json"
    self.log.info("Polling jenkins queue at the url %s", location)
    while try_count < self.max_try_before_job_appears:
        try:
            location_answer = jenkins_request_with_headers(
                jenkins_server, Request(method="POST", url=location)
            )
        except (HTTPError, JenkinsException):
            self.log.warning("polling failed, retrying", exc_info=True)
            try_count += 1
            time.sleep(self.sleep_time)
            continue
        if location_answer is not None:
            json_response = json.loads(location_answer["body"])
            if (
                "executable" in json_response
                and json_response["executable"] is not None
                and "number" in json_response["executable"]
            ):
                build_number = json_response["executable"]["number"]
                self.log.info("Job executed on Jenkins side with the build number %s", build_number)
                return build_number
        try_count += 1
        time.sleep(self.sleep_time)
    raise AirflowException(
        f"The job hasn't been executed after polling the queue {self.max_try_before_job_appears} times"
    )

async def run(self):
    async with self.hook.async_conn as client:
        waiter = self.hook.get_waiter("batch_job_complete", deferrable=True, client=client)
        attempt = 0
        while attempt < self.max_retries:
            attempt = attempt + 1
            try:
                await waiter.wait(
                    jobs=[self.job_id],
                    WaiterConfig={
                        "Delay": self.poll_interval,
                        "MaxAttempts": 1,
                    },
                )
                break
            except WaiterError as error:
                if "terminal failure" in str(error):
                    yield TriggerEvent(
                        {"status": "failure", "message": f"Delete Cluster Failed: {error}"}
                    )
                    break
                self.log.info(
                    "Job status is %s. Retrying attempt %s/%s",
                    error.last_response["jobs"][0]["status"],
                    attempt,
                    self.max_retries,
                )
                await asyncio.sleep(int(self.poll_interval))
    if attempt >= self.max_retries:
        yield TriggerEvent({"status": "failure", "message": "Job Failed - max attempts reached."})
    else:
        yield TriggerEvent({"status": "success", "job_id": self.job_id})

def get_counter(self, name, attributes = None):
    key = _generate_key_name(name, attributes)
    if key in self.map.keys():
        return self.map[key]
    else:
        new_counter = self._create_counter(name)
        self.map[key] = new_counter
        return new_counter

def _stream_logs_to_output(self):
    if not self.service:
        raise Exception("The 'service' should be initialized before!")
    logs = self.cli.service_logs(
        self.service["ID"], follow=True, stdout=True, stderr=True, is_tty=self.tty
    )
    line = ""
    while True:
        try:
            log = next(logs)
        except StopIteration:
            break
        else:
            try:
                log = log.decode()
            except UnicodeDecodeError:
                continue
            if log == "\n":
                self.log.info(line)
                line = ""
            else:
                line += log
    if line:
        self.log.info(line)

def run(
    self,
    sql,
    autocommit = False,
    parameters = None,
    handler = None,
    split_statements = True,
    return_last = True,
):
    self.descriptions = []
    if isinstance(sql, str):
        if split_statements:
            sql_list = [self.strip_sql_string(s) for s in self.split_sql_string(sql)]
        else:
            sql_list = [self.strip_sql_string(sql)]
    else:
        sql_list = [self.strip_sql_string(s) for s in sql]
    if sql_list:
        self.log.debug("Executing following statements against Databricks DB: %s", sql_list)
    else:
        raise ValueError("List of SQL statements is empty")
    results = []
    for sql_statement in sql_list:
        with closing(self.get_conn()) as conn:
            self.set_autocommit(conn, autocommit)
            with closing(conn.cursor()) as cur:
                self._run_command(cur, sql_statement, parameters)
                if handler is not None:
                    result = handler(cur)
                    if return_single_query_results(sql, return_last, split_statements):
                        results = [result]
                        self.descriptions = [cur.description]
                    else:
                        results.append(result)
                        self.descriptions.append(cur.description)
        self._sql_conn = None
    if handler is None:
        return None
    if return_single_query_results(sql, return_last, split_statements):
        return results[-1]
    else:
        return results

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
        dag = self.get_dag()
        info = self.task_instance_scheduling_decisions(session)
        tis = info.tis
        schedulable_tis = info.schedulable_tis
        changed_tis = info.changed_tis
        finished_tis = info.finished_tis
        unfinished = _UnfinishedStates.calculate(info.unfinished_tis)
        if unfinished.should_schedule:
            are_runnable_tasks = schedulable_tis or changed_tis
            if not are_runnable_tasks:
                are_runnable_tasks, changed_by_upstream = self._are_premature_tis(
                    unfinished.tis, finished_tis, session
                )
                if changed_by_upstream:  
                    unfinished = unfinished.recalculate()
    leaf_task_ids = {t.task_id for t in dag.leaves}
    leaf_tis = [ti for ti in tis if ti.task_id in leaf_task_ids if ti.state != TaskInstanceState.REMOVED]
    if dag.teardowns:
        teardown_task_ids = [t.task_id for t in dag.teardowns]
        upstream_of_teardowns = [t.task_id for t in dag.tasks_upstream_of_teardowns]
        teardown_tis = [ti for ti in tis if ti.task_id in teardown_task_ids]
        on_failure_fail_tis = [ti for ti in teardown_tis if getattr(ti.task, "on_failure_fail_dagrun")]
        tis_upstream_of_teardowns = [ti for ti in tis if ti.task_id in upstream_of_teardowns]
        leaf_tis = list(set(leaf_tis) - set(teardown_tis))
        leaf_tis.extend(on_failure_fail_tis)
        leaf_tis.extend(tis_upstream_of_teardowns)
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

def _emit_true_scheduling_delay_stats_for_finished_state(self, finished_tis):
    if self.state == State.RUNNING:
        return
    if self.external_trigger:
        return
    if not finished_tis:
        return
    try:
        dag = self.get_dag()
        if not dag.timetable.periodic:
            return
        ordered_tis_by_start_date = [ti for ti in finished_tis if ti.start_date]
        ordered_tis_by_start_date.sort(key=lambda ti: ti.start_date, reverse=False)
        first_start_date = ordered_tis_by_start_date[0].start_date if ordered_tis_by_start_date else None
        if first_start_date:
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

def __init__(
    self,
    vault_conn_id = default_conn_name,
    auth_type = None,
    auth_mount_point = None,
    kv_engine_version = None,
    role_id = None,
    kubernetes_role = None,
    kubernetes_jwt_path = None,
    token_path = None,
    gcp_key_path = None,
    gcp_scopes = None,
    azure_tenant_id = None,
    azure_resource = None,
    radius_host = None,
    radius_port = None,
    **kwargs,
):
    super().__init__()
    self.connection = self.get_connection(vault_conn_id)
    if not auth_type:
        auth_type = self.connection.extra_dejson.get("auth_type") or "token"
    if not auth_mount_point:
        auth_mount_point = self.connection.extra_dejson.get("auth_mount_point")
    if not kv_engine_version:
        conn_version = self.connection.extra_dejson.get("kv_engine_version")
        try:
            kv_engine_version = int(conn_version) if conn_version else DEFAULT_KV_ENGINE_VERSION
        except ValueError:
            raise VaultError(f"The version is not an int: {conn_version}. ")
    client_kwargs = self.connection.extra_dejson.get("client_kwargs", {})
    if kwargs:
        client_kwargs = merge_dicts(client_kwargs, kwargs)
    if auth_type == "approle":
        if role_id:
            warnings.warn(
                """The usage of role_id for AppRole authentication has been deprecated.
                    Please use connection login.""",
                DeprecationWarning,
                stacklevel=2,
            )
        elif self.connection.extra_dejson.get("role_id"):
            role_id = self.connection.extra_dejson.get("role_id")
            warnings.warn(
                """The usage of role_id in connection extra for AppRole authentication has been
                    deprecated. Please use connection login.""",
                DeprecationWarning,
                stacklevel=2,
            )
        elif self.connection.login:
            role_id = self.connection.login
    if auth_type == "aws_iam":
        if not role_id:
            role_id = self.connection.extra_dejson.get("role_id")
    azure_resource, azure_tenant_id = (
        self._get_azure_parameters_from_connection(azure_resource, azure_tenant_id)
        if auth_type == "azure"
        else (None, None)
    )
    gcp_key_path, gcp_keyfile_dict, gcp_scopes = (
        self._get_gcp_parameters_from_connection(gcp_key_path, gcp_scopes)
        if auth_type == "gcp"
        else (None, None, None)
    )
    kubernetes_jwt_path, kubernetes_role = (
        self._get_kubernetes_parameters_from_connection(kubernetes_jwt_path, kubernetes_role)
        if auth_type == "kubernetes"
        else (None, None)
    )
    radius_host, radius_port = (
        self._get_radius_parameters_from_connection(radius_host, radius_port)
        if auth_type == "radius"
        else (None, None)
    )
    key_id = self.connection.extra_dejson.get("key_id")
    if not key_id:
        key_id = self.connection.login
    if self.connection.conn_type == "vault":
        conn_protocol = "http"
    elif self.connection.conn_type == "vaults":
        conn_protocol = "https"
    elif self.connection.conn_type == "http":
        conn_protocol = "http"
    elif self.connection.conn_type == "https":
        conn_protocol = "https"
    else:
        raise VaultError("The url schema must be one of ['http', 'https', 'vault', 'vaults' ]")
    url = f"{conn_protocol}://{self.connection.host}"
    if self.connection.port:
        url += f":{self.connection.port}"
    mount_point = self.connection.schema if self.connection.schema else "secret"
    client_kwargs.update(
        **dict(
            url=url,
            auth_type=auth_type,
            auth_mount_point=auth_mount_point,
            mount_point=mount_point,
            kv_engine_version=kv_engine_version,
            token=self.connection.password,
            token_path=token_path,
            username=self.connection.login,
            password=self.connection.password,
            key_id=self.connection.login,
            secret_id=self.connection.password,
            role_id=role_id,
            kubernetes_role=kubernetes_role,
            kubernetes_jwt_path=kubernetes_jwt_path,
            gcp_key_path=gcp_key_path,
            gcp_keyfile_dict=gcp_keyfile_dict,
            gcp_scopes=gcp_scopes,
            azure_tenant_id=azure_tenant_id,
            azure_resource=azure_resource,
            radius_host=radius_host,
            radius_secret=self.connection.password,
            radius_port=radius_port,
        )
    )
    self.vault_client = _VaultClient(**client_kwargs)

def end(self):
    if TYPE_CHECKING:
        assert self.task_queue
        assert self.result_queue
        assert self.kube_scheduler
    self.log.info("Shutting down Kubernetes executor")
    self.log.debug("Flushing task_queue...")
    self._flush_task_queue()
    self.log.debug("Flushing result_queue...")
    self._flush_result_queue()
    self.task_queue.join()
    self.result_queue.join()
    if self.kube_scheduler:
        self.kube_scheduler.terminate()
    self._manager.shutdown()

def execute(self, context):
    self.log.info('Executing: %s', self.sql)
    hook = VerticaHook(vertica_conn_id=self.vertica_conn_id)
    hook.run(sql=self.sql)

def _get_secret(self, path_prefix, secret_id):
    if path_prefix:
        secrets_path = self.build_path(path_prefix, secret_id, self.sep)
    else:
        secrets_path = secret_id
    try:
        response = self.client.get_secret_value(
            SecretId=secrets_path,
        )
        return response.get('SecretString')
    except self.client.exceptions.ResourceNotFoundException:
        self.log.debug(
            "An error occurred (ResourceNotFoundException) when calling the "
            "get_secret_value operation: "
            "Secret %s not found.",
            secret_id,
        )
        return None
    except self.client.exceptions.AccessDeniedException:
        self.log.debug(
            "An error occurred (AccessDeniedException) when calling the get_secret_value operation",
            exc_info=True,
        )
        return None

def _task_instance_exists(session, source_table, dag_run, task_instance):
    if 'run_id' not in task_instance.c:
        source_to_ti_join_cond = and_(
            source_table.c.dag_id == task_instance.c.dag_id,
            source_table.c.task_id == task_instance.c.task_id,
            source_table.c.execution_date == task_instance.c.execution_date,
        )
        ti_to_dr_join_cond = and_(
            source_table.c.dag_id == task_instance.c.dag_id,
            source_table.c.execution_date == task_instance.c.execution_date,
        )
    else:
        source_to_ti_join_cond = and_(
            source_table.c.dag_id == task_instance.c.dag_id,
            source_table.c.task_id == task_instance.c.task_id,
        )
        ti_to_dr_join_cond = and_(
            source_table.c.dag_id == task_instance.c.dag_id,
            dag_run.c.run_id == task_instance.c.run_id,
            source_table.c.execution_date == dag_run.c.execution_date,
        )
    exists_subquery = (
        session.query(text('1'))
        .select_from(task_instance.join(dag_run, onclause=ti_to_dr_join_cond))
        .filter(source_to_ti_join_cond)
    )
    return exists_subquery

def create_pool(name, slots, description, session=None):
    if not (name and name.strip()):
        raise AirflowBadRequest("Pool name shouldn't be empty")
    try:
        slots = int(slots)
    except ValueError:
        raise AirflowBadRequest(f"Bad value for `slots`: {slots}")
    pool_name_length = Pool.pool.property.columns[0].type.length
    if len(name) > pool_name_length:
        raise AirflowBadRequest("Pool name can't be more than %d characters" % pool_name_length)
    session.expire_on_commit = False
    pool = session.query(Pool).filter_by(pool=name).first()
    if pool is None:
        pool = Pool(pool=name, slots=slots, description=description)
        session.add(pool)
    else:
        pool.slots = slots
        pool.description = description
    session.commit()
    return pool

def wrapper(*args, **kwargs):
    bound_args = function_signature.bind(*args, **kwargs)
    def get_key_name():
        if 'wildcard_key' in bound_args.arguments:
            return 'wildcard_key'
        if 'key' in bound_args.arguments:
            return 'key'
        raise ValueError('Missing key parameter!')
    key_name = get_key_name()
    if key_name and 'bucket_name' not in bound_args.arguments:
        bound_args.arguments['bucket_name'], bound_args.arguments[key_name] = S3Hook.parse_s3_url(
            bound_args.arguments[key_name]
        )
    return func(*bound_args.args, **bound_args.kwargs)

def manage_slas(self, dag, session = None):
    self.log.info("Running SLA Checks for %s", dag.dag_id)
    if not any(isinstance(ti.sla, timedelta) for ti in dag.tasks):
        self.log.info("Skipping SLA check for %s because no tasks in DAG have SLAs", dag)
        return
    qry = (
        session.query(TI.task_id, func.max(TI.execution_date).label('max_ti'))
        .with_hint(TI, 'USE INDEX (PRIMARY)', dialect_name='mysql')
        .filter(TI.dag_id == dag.dag_id)
        .filter(or_(TI.state == State.SUCCESS, TI.state == State.SKIPPED))
        .filter(TI.task_id.in_(dag.task_ids))
        .group_by(TI.task_id)
        .subquery('sq')
    )
    max_tis = (
        session.query(TI)
        .filter(
            TI.dag_id == dag.dag_id,
            TI.task_id == qry.c.task_id,
            TI.execution_date == qry.c.max_ti,
        )
        .all()
    )
    ts = timezone.utcnow()
    for ti in max_tis:
        task = dag.get_task(ti.task_id)
        if task.sla and not isinstance(task.sla, timedelta):
            raise TypeError(
                f"SLA is expected to be timedelta object, got "
                f"{type(task.sla)} in {task.dag_id}:{task.task_id}"
            )
        dttm = dag.following_schedule(ti.execution_date)
        while dttm < timezone.utcnow():
            following_schedule = dag.following_schedule(dttm)
            if following_schedule + task.sla < timezone.utcnow():
                session.merge(
                    SlaMiss(task_id=ti.task_id, dag_id=ti.dag_id, execution_date=dttm, timestamp=ts)
                )
            dttm = dag.following_schedule(dttm)
    session.commit()
    slas = (
        session.query(SlaMiss)
        .filter(SlaMiss.notification_sent == False, SlaMiss.dag_id == dag.dag_id)  
        .all()
    )
    if slas:  
        sla_dates = [sla.execution_date for sla in slas]
        fetched_tis = (
            session.query(TI)
            .filter(TI.state != State.SUCCESS, TI.execution_date.in_(sla_dates), TI.dag_id == dag.dag_id)
            .all()
        )
        blocking_tis = []
        for ti in fetched_tis:
            if ti.task_id in dag.task_ids:
                ti.task = dag.get_task(ti.task_id)
                blocking_tis.append(ti)
            else:
                session.delete(ti)
                session.commit()
        task_list = "\n".join(sla.task_id + ' on ' + sla.execution_date.isoformat() for sla in slas)
        blocking_task_list = "\n".join(
            ti.task_id + ' on ' + ti.execution_date.isoformat() for ti in blocking_tis
        )
        email_sent = False
        notification_sent = False
        if dag.sla_miss_callback:
            self.log.info('Calling SLA miss callback')
            try:
                dag.sla_miss_callback(dag, task_list, blocking_task_list, slas, blocking_tis)
                notification_sent = True
            except Exception:  
                self.log.exception("Could not call sla_miss_callback for DAG %s", dag.dag_id)
        email_content = f"""\
            Here's a list of tasks that missed their SLAs:
            <pre><code>{task_list}\n<code></pre>
            Blocking tasks:
            <pre><code>{blocking_task_list}<code></pre>
            Airflow Webserver URL: {conf.get(section='webserver', key='base_url')}
            """
        tasks_missed_sla = []
        for sla in slas:
            try:
                task = dag.get_task(sla.task_id)
            except TaskNotFound:
                self.log.warning(
                    "Task %s doesn't exist in DAG anymore, skipping SLA miss notification.", sla.task_id
                )
                continue
            tasks_missed_sla.append(task)
        emails = set()
        for task in tasks_missed_sla:
            if task.email:
                if isinstance(task.email, str):
                    emails |= set(get_email_address_list(task.email))
                elif isinstance(task.email, (list, tuple)):
                    emails |= set(task.email)
        if emails:
            try:
                send_email(emails, f"[airflow] SLA miss on DAG={dag.dag_id}", email_content)
                email_sent = True
                notification_sent = True
            except Exception:  
                Stats.incr('sla_email_notification_failure')
                self.log.exception("Could not send SLA Miss email notification for DAG %s", dag.dag_id)
        if notification_sent:
            for sla in slas:
                sla.email_sent = email_sent
                sla.notification_sent = True
                session.merge(sla)
        session.commit()

def gantt(self, session=None):
    dag_id = request.args.get('dag_id')
    dag = current_app.dag_bag.get_dag(dag_id)
    demo_mode = conf.getboolean('webserver', 'demo_mode')
    root = request.args.get('root')
    if root:
        dag = dag.sub_dag(task_ids_or_regex=root, include_upstream=True, include_downstream=False)
    dt_nr_dr_data = get_date_time_num_runs_dag_runs_form_data(request, session, dag)
    dttm = dt_nr_dr_data['dttm']
    form = DateTimeWithNumRunsWithDagRunsForm(data=dt_nr_dr_data)
    form.execution_date.choices = dt_nr_dr_data['dr_choices']
    tis = [ti for ti in dag.get_task_instances(dttm, dttm) if ti.start_date and ti.state]
    tis = sorted(tis, key=lambda ti: ti.start_date)
    ti_fails = list(
        itertools.chain(
            *[
                (
                    session.query(TaskFail)
                    .filter(
                        TaskFail.dag_id == ti.dag_id,
                        TaskFail.task_id == ti.task_id,
                        TaskFail.execution_date == ti.execution_date,
                    )
                    .all()
                )
                for ti in tis
            ]
        )
    )
    gantt_bar_items = []
    tasks = []
    for ti in tis:
        end_date = ti.end_date or timezone.utcnow()
        try_count = ti.prev_attempted_tries
        gantt_bar_items.append((ti.task_id, ti.start_date, end_date, ti.state, try_count))
        task_dict = alchemy_to_dict(ti)
        task_dict['extraLinks'] = dag.get_task(ti.task_id).extra_links
        tasks.append(task_dict)
    tf_count = 0
    try_count = 1
    prev_task_id = ""
    for failed_task_instance in ti_fails:
        end_date = failed_task_instance.end_date or timezone.utcnow()
        start_date = failed_task_instance.start_date or end_date
        if tf_count != 0 and failed_task_instance.task_id == prev_task_id:
            try_count += 1
        else:
            try_count = 1
        prev_task_id = failed_task_instance.task_id
        gantt_bar_items.append(
            (failed_task_instance.task_id, start_date, end_date, State.FAILED, try_count)
        )
        tf_count += 1
        task = dag.get_task(failed_task_instance.task_id)
        task_dict = alchemy_to_dict(failed_task_instance)
        task_dict['state'] = State.FAILED
        task_dict['operator'] = task.task_type
        task_dict['try_number'] = try_count
        task_dict['extraLinks'] = task.extra_links
        tasks.append(task_dict)
    data = {
        'taskNames': [ti.task_id for ti in tis],
        'tasks': tasks,
        'height': len(tis) * 25 + 25,
    }
    session.commit()
    return self.render_template(
        'airflow/gantt.html',
        dag=dag,
        execution_date=dttm.isoformat(),
        form=form,
        data=data,
        base_date='',
        demo_mode=demo_mode,
        root=root,
    )

def _check_value(self, action, value):
    executor = conf.get('core', 'EXECUTOR')
    if value == 'celery' and executor != ExecutorLoader.CELERY_EXECUTOR:
        message = f'celery subcommand works only with CeleryExecutor, your current executor: {executor}'
        raise ArgumentError(action, message)
    if value == 'kubernetes':
        try:
            from kubernetes.client import models
            if not models:
                message = "kubernetes subcommand requires that ' \
                              'you run pip install 'apache-airflow[cncf.kubernetes]'"
                raise ArgumentError(action, message)
        except Exception:  
            message = 'kubernetes subcommand requires that you pip install the kubernetes python client'
            raise ArgumentError(action, message)
    if action.choices is not None and value not in action.choices:
        check_legacy_command(action, value)
    super()._check_value(action, value)

def update_state(self, session=None):
    dag = self.get_dag()
    ready_tis = []
    tis = [ti for ti in self.get_task_instances(session=session,
                                                state=State.task_states + (State.SHUTDOWN,))]
    self.log.debug("number of tis tasks for %s: %s task(s)", self, len(tis))
    for ti in tis:
        ti.task = dag.get_task(ti.task_id)
    start_dttm = timezone.utcnow()
    unfinished_tasks = [t for t in tis if t.state in State.unfinished()]
    finished_tasks = [t for t in tis if t.state in State.finished() + [State.UPSTREAM_FAILED]]
    none_depends_on_past = all(not t.task.depends_on_past for t in unfinished_tasks)
    none_task_concurrency = all(t.task.task_concurrency is None
                                for t in unfinished_tasks)
    if unfinished_tasks:
        scheduleable_tasks = [ut for ut in unfinished_tasks if ut.state in SCHEDULEABLE_STATES]
        if none_depends_on_past and none_task_concurrency:
            self.log.debug(
                "number of scheduleable tasks for %s: %s task(s)",
                self, len(scheduleable_tasks))
            ready_tis, changed_tis = self._get_ready_tis(scheduleable_tasks, finished_tasks, session)
            self.log.debug("ready tis length for %s: %s task(s)", self, len(ready_tis))
            are_runnable_tasks = ready_tis or self._are_premature_tis(
                unfinished_tasks, finished_tasks, session) or changed_tis
        else:
            for ti in scheduleable_tasks:
                if ti.are_dependencies_met(
                    dep_context=DepContext(flag_upstream_failed=True),
                    session=session
                ):
                    self.log.debug('Queuing task: %s', ti)
                    ready_tis.append(ti)
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

def _print_stat(self):
    if self.print_stats_interval > 0 and (
            timezone.utcnow() -
            self.last_stat_print_time).total_seconds() > self.print_stats_interval:
        if self._file_paths:
            self._log_file_processing_stats(self._file_paths)
        self.last_stat_print_time = timezone.utcnow()

def do_setup():
    write_version()
    setup(
        name='apache-airflow',
        description='Programmatically author, schedule and monitor data pipelines',
        long_description=long_description,
        long_description_content_type='text/markdown',
        license='Apache License 2.0',
        version=version,
        packages=find_packages(exclude=['tests*']),
        package_data={'': ['airflow/alembic.ini', "airflow/git_version"]},
        include_package_data=True,
        zip_safe=False,
        scripts=['airflow/bin/airflow'],
        install_requires=[
            'alembic>=1.0, <2.0',
            'cached_property~=1.5',
            'configparser>=3.5.0, <3.6.0',
            'croniter>=0.3.17, <0.4',
            'dill>=0.2.2, <0.3',
            'dumb-init>=1.2.2',
            'flask>=1.0, <2.0',
            'flask-appbuilder>=1.12.5, <2.0.0',
            'flask-caching>=1.3.3, <1.4.0',
            'flask-login>=0.3, <0.5',
            'flask-swagger==0.2.13',
            'flask-wtf>=0.14.2, <0.15',
            'funcsigs==1.0.0',
            'gitpython>=2.0.2',
            'gunicorn>=19.5.0, <20.0',
            'iso8601>=0.1.12',
            'json-merge-patch==0.2',
            'jinja2>=2.10.1, <2.11.0',
            'lazy_object_proxy~=1.3',
            'markdown>=2.5.2, <3.0',
            'pandas>=0.17.1, <1.0.0',
            'pendulum==1.4.4',
            'psutil>=4.2.0, <6.0.0',
            'pygments>=2.0.1, <3.0',
            'python-daemon>=2.1.1, <2.2',
            'python-dateutil>=2.3, <3',
            'requests>=2.20.0, <3',
            'setproctitle>=1.1.8, <2',
            'sqlalchemy~=1.3',
            'tabulate>=0.7.5, <0.9',
            'tenacity==4.12.0',
            'text-unidecode==1.2',
            'typing;python_version<"3.5"',
            'thrift>=0.9.2',
            'tzlocal>=1.4',
            'unicodecsv>=0.14.1',
            'werkzeug>=0.14.1, <0.15.0',
            'zope.deprecation>=4.0, <5.0',
        ],
        setup_requires=[
            'docutils>=0.14, <1.0',
        ],
        extras_require={
            'all': devel_all,
            'devel_ci': devel_ci,
            'all_dbs': all_dbs,
            'atlas': atlas,
            'async': async_packages,
            'aws': aws,
            'azure': azure,
            'cassandra': cassandra,
            'celery': celery,
            'cgroups': cgroups,
            'cloudant': cloudant,
            'crypto': crypto,
            'dask': dask,
            'databricks': databricks,
            'datadog': datadog,
            'devel': devel_minreq,
            'devel_hadoop': devel_hadoop,
            'doc': doc,
            'docker': docker,
            'druid': druid,
            'elasticsearch': elasticsearch,
            'gcp': gcp,
            'gcp_api': gcp,  
            'github_enterprise': flask_oauth,
            'google_auth': flask_oauth,
            'grpc': grpc,
            'hdfs': hdfs,
            'hive': hive,
            'jdbc': jdbc,
            'jira': jira,
            'kerberos': kerberos,
            'kubernetes': kubernetes,
            'ldap': ldap,
            'mongo': mongo,
            'mssql': mssql,
            'mysql': mysql,
            'oracle': oracle,
            'papermill': papermill,
            'password': password,
            'pinot': pinot,
            'postgres': postgres,
            'qds': qds,
            'rabbitmq': rabbitmq,
            'redis': redis,
            'salesforce': salesforce,
            'samba': samba,
            'sendgrid': sendgrid,
            'segment': segment,
            'slack': slack,
            'snowflake': snowflake,
            'ssh': ssh,
            'statsd': statsd,
            'vertica': vertica,
            'webhdfs': webhdfs,
            'winrm': winrm
        },
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.5',
            'Topic :: System :: Monitoring',
        ],
        author='Apache Software Foundation',
        author_email='dev@airflow.apache.org',
        url='http://airflow.apache.org/',
        download_url=(
            'https://dist.apache.org/repos/dist/release/airflow/' + version),
        cmdclass={
            'test': Tox,
            'extra_clean': CleanCommand,
            'compile_assets': CompileAssets
        },
        python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*',
    )

def update_admin_perm_view(self):
    pvms = self.get_session.query(sqla_models.PermissionView).all()
    pvms = [p for p in pvms if p.permission and p.view_menu]
    admin = self.find_role('Admin')
    existing_perms_vms = set(admin.permissions)
    for p in pvms:
        if p not in existing_perms_vms:
            existing_perms_vms.add(p)
    admin.permissions = list(existing_perms_vms)
    self.get_session.commit()

def execute(self, context):
    hive = HiveCliHook(hive_cli_conn_id=self.hive_cli_conn_id)
    logging.info("Extracting data from Hive")
    hive_table = 'druid.' + context['task_instance_key_str'].replace('.', '_')
    sql = self.sql.strip().strip(';')
    hql = """\
        set mapred.output.compress=false;
        set hive.exec.compress.output=false;
        DROP TABLE IF EXISTS {hive_table};
        CREATE TABLE {hive_table}
        ROW FORMAT DELIMITED FIELDS TERMINATED BY  '\t'
        STORED AS TEXTFILE
        TBLPROPERTIES ('serialization.null.format' = '')
        AS
        {sql}
        """.format(**locals())
    logging.info("Running command:\n {}".format(hql))
    hive.run_cli(hql)
    m = HiveMetastoreHook(self.metastore_conn_id)
    t = m.get_table(hive_table)
    columns = [col.name for col in t.sd.cols]
    hdfs_uri = m.get_table(hive_table).sd.location
    pos = hdfs_uri.find('/user')
    static_path = hdfs_uri[pos:]
    schema, table = hive_table.split('.')
    druid = DruidHook(druid_ingest_conn_id=self.druid_ingest_conn_id)
    logging.info("Inserting rows into Druid")
    logging.info("HDFS path: " + static_path)
    druid.load_from_hdfs(
        datasource=self.druid_datasource,
        intervals=self.intervals,
        static_path=static_path, ts_dim=self.ts_dim,
        columns=columns, num_shards=self.num_shards, target_partition_size=self.target_partition_size,
        metric_spec=self.metric_spec, hadoop_dependency_coordinates=self.hadoop_dependency_coordinates)
    logging.info("Load seems to have succeeded!")
    logging.info(
        "Cleaning up by dropping the temp "
        "Hive table {}".format(hive_table))
    hql = "DROP TABLE IF EXISTS {}".format(hive_table)
    hive.run_cli(hql)

def run_and_check(self, session, prepped_request, extra_options):
    stream = extra_options.get("stream", False)
    verify = extra_options.get("verify", False)
    proxies = extra_options.get("proxies", {})
    cert = extra_options.get("cert", None)
    timeout = extra_options.get("timeout", None)
    allow_redirects = extra_options.get("allow_redirects", True)
    response = session.send(prepped_request,
                            stream=stream,
                            verify=verify,
                            proxies=proxies,
                            cert=cert,
                            timeout=timeout,
                            allow_redirects=allow_redirects)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logging.error("HTTP error: " + response.reason)
        if self.method != 'GET':
            logging.error(response.text)
        raise AirflowException(str(response.status_code)+":"+response.reason)
    return response

def __init__(
        self, sql,
        presto_conn_id='presto_default',
        *args, **kwargs):
    super(PrestoCheckOperator, self).__init__(sql, *args, **kwargs)
    self.presto_conn_id = presto_conn_id
    self.sql = sql

def __init__(
        self, host=None, login=None,
        psw=None, db=None, port=None, postgres_conn_id=None):
    if not postgres_conn_id:
        self.host = host
        self.login = login
        self.psw = psw
        self.db = db
        self.port = port
    else:
        session = settings.Session()
        db = session.query(
            Connection).filter(
                Connection.conn_id == postgres_conn_id)
        if db.count() == 0:
            raise Exception("The mysql_dbid you provided isn't defined")
        else:
            db = db.all()[0]
        self.host = db.host
        self.login = db.login
        self.psw = db.password
        self.db = db.schema
        self.port = db.port
        session.commit()
        session.close()

def get_sources(
    *,
    ctx,
    src,
    quiet,
    verbose,
    include,
    exclude,
    extend_exclude,
    force_exclude,
    report,
    stdin_filename,
):
    sources = set()
    if exclude is None:
        exclude = re_compile_maybe_verbose(DEFAULT_EXCLUDES)
        gitignore = get_gitignore(ctx.obj["root"])
    else:
        gitignore = None
    for s in src:
        if s == "-" and stdin_filename:
            p = Path(stdin_filename)
            is_stdin = True
        else:
            p = Path(s)
            is_stdin = False
        if is_stdin or p.is_file():
            normalized_path = normalize_path_maybe_ignore(p, ctx.obj["root"], report)
            if normalized_path is None:
                continue
            normalized_path = "/" + normalized_path
            if force_exclude:
                force_exclude_match = force_exclude.search(normalized_path)
            else:
                force_exclude_match = None
            if force_exclude_match and force_exclude_match.group(0):
                report.path_ignored(p, "matches the --force-exclude regular expression")
                continue
            if is_stdin:
                p = Path(f"{STDIN_PLACEHOLDER}{str(p)}")
            if p.suffix == ".ipynb" and not jupyter_dependencies_are_installed(
                verbose=verbose, quiet=quiet
            ):
                continue
            sources.add(p)
        elif p.is_dir():
            sources.update(
                gen_python_files(
                    p.iterdir(),
                    ctx.obj["root"],
                    include,
                    exclude,
                    extend_exclude,
                    force_exclude,
                    report,
                    gitignore,
                    verbose=verbose,
                    quiet=quiet,
                )
            )
        elif s == "-":
            sources.add(p)
        else:
            err(f"invalid path: {s}")
    return sources

def main(
    ctx,
    line_length,
    check,
    diff,
    fast,
    pyi,
    py36,
    skip_string_normalization,
    quiet,
    include,
    exclude,
    src,
):
    sources = []
    try:
        include_regex = re.compile(include)
    except re.error:
        err(f"Invalid regular expression for include given: {include!r}")
        ctx.exit(2)
    try:
        exclude_regex = re.compile(exclude)
    except re.error:
        err(f"Invalid regular expression for exclude given: {exclude!r}")
        ctx.exit(2)
    root = find_project_root(src)
    for s in src:
        p = Path(s)
        if p.is_dir():
            sources.extend(
                gen_python_files_in_dir(p, root, include_regex, exclude_regex)
            )
        elif p.is_file():
            sources.append(p)
        elif s == "-":
            sources.append(Path("-"))
        else:
            err(f"invalid path: {s}")
    if check and not diff:
        write_back = WriteBack.NO
    elif diff:
        write_back = WriteBack.DIFF
    else:
        write_back = WriteBack.YES
    mode = FileMode.AUTO_DETECT
    if py36:
        mode |= FileMode.PYTHON36
    if pyi:
        mode |= FileMode.PYI
    if skip_string_normalization:
        mode |= FileMode.NO_STRING_NORMALIZATION
    report = Report(check=check, quiet=quiet)
    if len(sources) == 0:
        out("No paths given. Nothing to do 😴")
        ctx.exit(0)
        return
    elif len(sources) == 1:
        reformat_one(
            src=sources[0],
            line_length=line_length,
            fast=fast,
            write_back=write_back,
            mode=mode,
            report=report,
        )
    else:
        loop = asyncio.get_event_loop()
        executor = ProcessPoolExecutor(max_workers=os.cpu_count())
        try:
            loop.run_until_complete(
                schedule_formatting(
                    sources=sources,
                    line_length=line_length,
                    fast=fast,
                    write_back=write_back,
                    mode=mode,
                    report=report,
                    loop=loop,
                    executor=executor,
                )
            )
        finally:
            shutdown(loop)
        if not quiet:
            out("All done! ✨ 🍰 ✨")
            click.echo(str(report))
    ctx.exit(report.return_code)

def get_content_type(filename):
    mime, encoding = mimetypes.guess_type(filename, strict=False)
    if mime:
        content_type = mime
        if encoding:
            content_type = f'{mime}; charset={encoding}'
        return content_type

def report_speed(self):
    now = time()
    if now - self._prev_time >= self._update_interval:
        downloaded = self.status.downloaded
        try:
            speed = ((downloaded - self._prev_bytes)
                     / (now - self._prev_time))
        except ZeroDivisionError:
            speed = 0
        if not self.status.total_size:
            self._status_line = PROGRESS_NO_CONTENT_LENGTH.format(
                downloaded=humanize_bytes(downloaded),
                speed=humanize_bytes(speed),
            )
        else:
            try:
                percentage = downloaded / self.status.total_size * 100
            except ZeroDivisionError:
                percentage = 0
            if not speed:
                eta = '-:--:--'
            else:
                s = int((self.status.total_size - downloaded) / speed)
                h, s = divmod(s, 60 * 60)
                m, s = divmod(s, 60)
                eta = f'{h}:{m:0>2}:{s:0>2}'
            self._status_line = PROGRESS.format(
                percentage=percentage,
                downloaded=humanize_bytes(downloaded),
                speed=humanize_bytes(speed),
                eta=eta,
            )
        self._prev_time = now
        self._prev_bytes = downloaded
    self.output.write(
        f'{CLEAR_LINE} {SPINNER[self._spinner_pos]} {self._status_line}'
    )
    self.output.flush()
    self._spinner_pos = (self._spinner_pos + 1
                         if self._spinner_pos + 1 != len(SPINNER)
                         else 0)

def format_body(self, body, mime):
    maybe_json = [
        'json',
        'javascript',
        'text',
    ]
    if (any(token in mime for token in maybe_json) or
            self.kwargs['explicit_json']):
        try:
            obj = json.loads(body)
        except ValueError:
            pass  
        else:
            body = json.dumps(
                obj=obj,
                sort_keys=True,
                ensure_ascii=False,
                indent=DEFAULT_INDENT
            )
    return body

def tokenize(string):
    backslash = '\\'
    tokens = ['']
    characters = iter(string)
    for char in characters:
        if char == backslash:
            next_char = next(characters, '')
            if next_char in self.special_characters:
                tokens.extend([Escaped(next_char), ''])
            else:
                tokens[-1] += char + next_char
        else:
            tokens[-1] += char
    return tokens

def tokenize(s):
    backslash = '\\'
    tokens = ['']
    s = iter(s)
    for c in s:
        if c == backslash:
            nc = next(s, '')
            if nc in self.special_characters:
                tokens.extend([Escaped(nc), ''])
            else:
                tokens[-1] += c + nc
        else:
            tokens[-1] += c
    return tokens

def get_response(session_name, requests_kwargs, config_dir, read_only=False):
    if os.path.sep in session_name:
        path = os.path.expanduser(session_name)
    else:
        hostname = (
            requests_kwargs['headers'].get('Host', None)
            or urlsplit(requests_kwargs['url']).netloc.split('@')[-1]
        )
        assert re.match('^[a-zA-Z0-9_.:-]+$', hostname)
        hostname = hostname.replace(':', '_')
        path = os.path.join(config_dir,
                            SESSIONS_DIR_NAME,
                            hostname,
                            session_name + '.json')
    session = Session(path)
    session.load()
    request_headers = requests_kwargs.get('headers', {})
    merged_headers = session.headers.copy()
    merged_headers.update(request_headers)
    requests_kwargs['headers'] = merged_headers
    session.update_headers(request_headers)
    auth = requests_kwargs.get('auth', None)
    if auth:
        session.auth = auth
    elif session.auth:
        requests_kwargs['auth'] = session.auth
    requests_session = requests.Session()
    requests_session.cookies = session.cookies
    try:
        response = requests_session.request(**requests_kwargs)
    except Exception:
        raise
    else:
        if session.is_new or not read_only:
            session.cookies = requests_session.cookies
            session.save()
        return response

async def __call__(self, scope, receive, send):
    if AsyncExitStack:
        dependency_exception = None
        async with AsyncExitStack() as stack:
            scope[self.context_name] = stack
            try:
                await self.app(scope, receive, send)
            except Exception as e:
                dependency_exception = e
                raise e
        if dependency_exception:
            raise dependency_exception
    else:
        await self.app(scope, receive, send)  

async def __call__(  
    self, request
):
    authorization = request.headers.get("Authorization")
    scheme, param = get_authorization_scheme_param(authorization)
    if self.realm:
        unauthorized_headers = {"WWW-Authenticate": f'Basic realm="{self.realm}"'}
    else:
        unauthorized_headers = {"WWW-Authenticate": "Basic"}
    invalid_user_credentials_exc = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers=unauthorized_headers,
    )
    if not authorization or scheme.lower() != "basic":
        if self.auto_error:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers=unauthorized_headers,
            )
        else:
            return None
    try:
        data = b64decode(param).decode("ascii")
    except (ValueError, UnicodeDecodeError, binascii.Error):
        raise invalid_user_credentials_exc
    username, separator, password = data.partition(":")
    if not separator:
        raise invalid_user_credentials_exc
    return HTTPBasicCredentials(username=username, password=password)

def get_experts(settings):
    (
        issues_commentors,
        issues_last_month_commentors,
        issues_authors,
    ) = get_issues_experts(settings=settings)
    (
        discussions_commentors,
        discussions_last_month_commentors,
        discussions_authors,
    ) = get_discussions_experts(settings=settings)
    commentors = issues_commentors + discussions_commentors
    last_month_commentors = (
        issues_last_month_commentors + discussions_last_month_commentors
    )
    authors = {**issues_authors, **discussions_authors}
    return commentors, last_month_commentors, authors

def delete(
    self,
    path,
    *,
    response_model = None,
    status_code = None,
    tags = None,
    dependencies = None,
    summary = None,
    description = None,
    response_description = "Successful Response",
    responses = None,
    deprecated = None,
    operation_id = None,
    response_model_include = None,
    response_model_exclude = None,
    response_model_by_alias = True,
    response_model_exclude_unset = False,
    response_model_exclude_defaults = False,
    response_model_exclude_none = False,
    include_in_schema = True,
    response_class = Default(JSONResponse),
    name = None,
    callbacks = None,
    openapi_extra = None,
    generate_unique_id_function = Default(
        generate_unique_id
    ),
):
    return self.router.delete(
        path,
        response_model=response_model,
        status_code=status_code,
        tags=tags,
        dependencies=dependencies,
        summary=summary,
        description=description,
        response_description=response_description,
        responses=responses,
        deprecated=deprecated,
        response_model_include=response_model_include,
        response_model_exclude=response_model_exclude,
        response_model_by_alias=response_model_by_alias,
        operation_id=operation_id,
        response_model_exclude_unset=response_model_exclude_unset,
        response_model_exclude_defaults=response_model_exclude_defaults,
        response_model_exclude_none=response_model_exclude_none,
        include_in_schema=include_in_schema,
        response_class=response_class,
        name=name,
        callbacks=callbacks,
        openapi_extra=openapi_extra,
        generate_unique_id_function=generate_unique_id_function,
    )

def get_dependant(
    *,
    path,
    call,
    name = None,
    security_scopes = None,
    use_cache = True,
):
    path_param_names = get_path_param_names(path)
    endpoint_signature = get_typed_signature(call)
    signature_params = endpoint_signature.parameters
    dependant = Dependant(
        call=call,
        name=name,
        path=path,
        security_scopes=security_scopes,
        use_cache=use_cache,
    )
    for param_name, param in signature_params.items():
        if isinstance(param.default, params.Depends):
            sub_dependant = get_param_sub_dependant(
                param=param, path=path, security_scopes=security_scopes
            )
            dependant.dependencies.append(sub_dependant)
            continue
        if add_non_field_param_to_dependency(param=param, dependant=dependant):
            continue
        param_field = get_param_field(
            param=param, default_field_info=params.Query, param_name=param_name
        )
        if param_name in path_param_names:
            assert is_scalar_field(
                field=param_field
            ), "Path params must be of one of the supported types"
            if isinstance(param.default, params.Path):
                ignore_default = False
            else:
                ignore_default = True
            param_field = get_param_field(
                param=param,
                param_name=param_name,
                default_field_info=params.Path,
                force_type=params.ParamTypes.path,
                ignore_default=ignore_default,
            )
            add_param_to_fields(field=param_field, dependant=dependant)
        elif is_scalar_field(field=param_field):
            add_param_to_fields(field=param_field, dependant=dependant)
        elif isinstance(
            param.default, (params.Query, params.Header)
        ) and is_scalar_sequence_field(param_field):
            add_param_to_fields(field=param_field, dependant=dependant)
        else:
            field_info = param_field.field_info
            assert isinstance(
                field_info, params.Body
            ), f"Param: {param_field.name} can only be a request body, using Body()"
            dependant.body_params.append(param_field)
    return dependant

def deep_dict_update(main_dict, update_dict):
    for key in update_dict:
        if (
            key in main_dict
            and isinstance(main_dict[key], dict)
            and isinstance(update_dict[key], dict)
        ):
            deep_dict_update(main_dict[key], update_dict[key])
        else:
            main_dict[key] = update_dict[key]

def generate_encoders_by_class_tuples(
    type_encoder_map
):
    encoders_by_classes = defaultdict(list)
    for type_, encoder in type_encoder_map.items():
        encoders_by_classes[encoder].append(type_)
    encoders_by_class_tuples = {}
    for encoder, classes in encoders_by_classes.items():
        encoders_by_class_tuples[encoder] = tuple(classes)
    return encoders_by_class_tuples

def get_dependant(
    *,
    path,
    call,
    name = None,
    security_scopes = None,
    use_cache = True,
):
    path_param_names = get_path_param_names(path)
    endpoint_signature = get_typed_signature(call)
    signature_params = endpoint_signature.parameters
    if is_gen_callable(call) or is_async_gen_callable(call):
        check_dependency_contextmanagers()
    dependant = Dependant(call=call, name=name, path=path, use_cache=use_cache)
    for param_name, param in signature_params.items():
        if isinstance(param.default, params.Depends):
            sub_dependant = get_param_sub_dependant(
                param=param, path=path, security_scopes=security_scopes
            )
            dependant.dependencies.append(sub_dependant)
    for param_name, param in signature_params.items():
        if isinstance(param.default, params.Depends):
            continue
        if add_non_field_param_to_dependency(param=param, dependant=dependant):
            continue
        param_field = get_param_field(
            param=param, default_field_info=params.Query, param_name=param_name
        )
        if param_name in path_param_names:
            assert is_scalar_field(
                field=param_field
            ), "Path params must be of one of the supported types"
            if isinstance(param.default, params.Path):
                ignore_default = False
            else:
                ignore_default = True
            param_field = get_param_field(
                param=param,
                param_name=param_name,
                default_field_info=params.Path,
                force_type=params.ParamTypes.path,
                ignore_default=ignore_default,
            )
            add_param_to_fields(field=param_field, dependant=dependant)
        elif is_scalar_field(field=param_field):
            add_param_to_fields(field=param_field, dependant=dependant)
        elif isinstance(
            param.default, (params.Query, params.Header)
        ) and is_scalar_sequence_field(param_field):
            add_param_to_fields(field=param_field, dependant=dependant)
        else:
            field_info = get_field_info(param_field)
            assert isinstance(
                field_info, params.Body
            ), f"Param: {param_field.name} can only be a request body, using Body(...)"
            dependant.body_params.append(param_field)
    return dependant

def get_path_param_names(path):
    return {item.strip("{}") for item in re.findall("{[^}]*}", path)}

def _find_error_handler(self, e):
    exc_class, code = self._get_exc_class_and_code(type(e))
    for c in [code, None]:
        for name in chain(request.blueprints, [None]):
            handler_map = self.error_handler_spec[name][c]
            if not handler_map:
                continue
            for cls in exc_class.__mro__:
                handler = handler_map.get(cls)
                if handler is not None:
                    return handler
    return None

def handle_user_exception(self, e):
    if isinstance(e, BadRequestKeyError):
        if self.debug or self.config["TRAP_BAD_REQUEST_ERRORS"]:
            e.show_exception = True
            if e.args[0] not in e.get_description():
                e.description = f"KeyError: {e.args[0]!r}"
        elif not hasattr(BadRequestKeyError, "show_exception"):
            e.args = ()
    if isinstance(e, HTTPException) and not self.trap_http_exception(e):
        return self.handle_http_exception(e)
    handler = self._find_error_handler(e)
    if handler is None:
        raise
    return handler(e)

def json(self):
    if __debug__:
        _assert_have_json()
    if self.mimetype == 'application/json':
        request_charset = self.mimetype_params.get('charset')
        if request_charset is not None:
            j = json.loads(self.data, encoding=request_charset )
        else:
            j = json.loads(self.data)
        return j

def agg_list_like(self):
    from pandas.core.groupby.generic import (
        DataFrameGroupBy,
        SeriesGroupBy,
    )
    from pandas.core.reshape.concat import concat
    obj = self.obj
    arg = cast(List[AggFuncTypeBase], self.f)
    if getattr(obj, "axis", 0) == 1:
        raise NotImplementedError("axis other than 0 is not supported")
    if not isinstance(obj, SelectionMixin):
        selected_obj = obj
    elif obj._selected_obj.ndim == 1:
        selected_obj = obj._selected_obj
    else:
        selected_obj = obj._obj_with_exclusions
    results = []
    keys = []
    is_groupby = isinstance(obj, (DataFrameGroupBy, SeriesGroupBy))
    if is_groupby:
        context_manager = com.temp_setattr(obj, "as_index", True)
    else:
        context_manager = nullcontext()
    with context_manager:
        if selected_obj.ndim == 1:
            for a in arg:
                colg = obj._gotitem(selected_obj.name, ndim=1, subset=selected_obj)
                if isinstance(colg, (ABCSeries, ABCDataFrame)):
                    new_res = colg.aggregate(
                        a, self.axis, *self.args, **self.kwargs
                    )
                else:
                    new_res = colg.aggregate(a, *self.args, **self.kwargs)
                results.append(new_res)
                name = com.get_callable_name(a) or a
                keys.append(name)
        else:
            indices = []
            for index, col in enumerate(selected_obj):
                colg = obj._gotitem(col, ndim=1, subset=selected_obj.iloc[:, index])
                if isinstance(colg, (ABCSeries, ABCDataFrame)):
                    new_res = colg.aggregate(
                        arg, self.axis, *self.args, **self.kwargs
                    )
                else:
                    new_res = colg.aggregate(arg, *self.args, **self.kwargs)
                results.append(new_res)
                indices.append(index)
            keys = selected_obj.columns.take(indices)
    try:
        return concat(results, keys=keys, axis=1, sort=False)
    except TypeError as err:
        from pandas import Series
        result = Series(results, index=keys, name=obj.name)
        if is_nested_object(result):
            raise ValueError(
                "cannot combine transform and aggregation operations"
            ) from err
        return result

def reorder_arrays(
    arrays, arr_columns, columns, length
):
    if columns is not None:
        if not columns.equals(arr_columns):
            new_arrays = [None] * len(columns)
            indexer = arr_columns.get_indexer(columns)
            for i, k in enumerate(indexer):
                if k == -1:
                    arr = np.empty(length, dtype=object)
                    arr.fill(np.nan)
                else:
                    arr = arrays[k]
                new_arrays[i] = arr
            arrays = new_arrays  
            arr_columns = columns
    return arrays, arr_columns

def agg_list_like(self):
    from pandas.core.groupby.generic import (
        DataFrameGroupBy,
        SeriesGroupBy,
    )
    from pandas.core.reshape.concat import concat
    obj = self.obj
    arg = cast(List[AggFuncTypeBase], self.f)
    if getattr(obj, "axis", 0) == 1:
        raise NotImplementedError("axis other than 0 is not supported")
    if not isinstance(obj, SelectionMixin):
        selected_obj = obj
    elif obj._selected_obj.ndim == 1:
        selected_obj = obj._selected_obj
    else:
        selected_obj = obj._obj_with_exclusions
    results = []
    keys = []
    is_groupby = isinstance(obj, (DataFrameGroupBy, SeriesGroupBy))
    if is_groupby:
        context_manager = com.temp_setattr(obj, "as_index", True)
    else:
        context_manager = nullcontext()
    with context_manager:
        if selected_obj.ndim == 1:
            for a in arg:
                colg = obj._gotitem(selected_obj.name, ndim=1, subset=selected_obj)
                if isinstance(colg, (ABCSeries, ABCDataFrame)):
                    new_res = colg.aggregate(
                        a, self.axis, *self.args, **self.kwargs
                    )
                else:
                    new_res = colg.aggregate(a, *self.args, **self.kwargs)
                results.append(new_res)
                name = com.get_callable_name(a) or a
                keys.append(name)
        else:
            indices = []
            for index, col in enumerate(selected_obj):
                colg = obj._gotitem(col, ndim=1, subset=selected_obj.iloc[:, index])
                if isinstance(colg, (ABCSeries, ABCDataFrame)):
                    new_res = colg.aggregate(
                        arg, self.axis, *self.args, **self.kwargs
                    )
                else:
                    new_res = colg.aggregate(arg, *self.args, **self.kwargs)
                results.append(new_res)
                indices.append(index)
            keys = selected_obj.columns.take(indices)
    try:
        concatenated = concat(results, keys=keys, axis=1, sort=False)
    except TypeError as err:
        from pandas import Series
        result = Series(results, index=keys, name=obj.name)
        if is_nested_object(result):
            raise ValueError(
                "cannot combine transform and aggregation operations"
            ) from err
        return result
    else:
        index_size = concatenated.index.size
        full_ordered_index = next(
            result.index for result in results if result.index.size == index_size
        )
        return concatenated.reindex(full_ordered_index, copy=False)

def reindex(
    self, target, method=None, level=None, limit=None, tolerance=None
):
    preserve_names = not hasattr(target, "name")
    target = ensure_has_len(target)  
    if not isinstance(target, Index) and len(target) == 0:
        if level is not None and self._is_multi:
            idx = self.levels[level]  
        else:
            idx = self
        target = idx[:0]
    else:
        target = ensure_index(target)
    if level is not None and (
        isinstance(self, ABCMultiIndex) or isinstance(target, ABCMultiIndex)
    ):
        if method is not None:
            raise TypeError("Fill method not supported if level passed")
        target, indexer, _ = self._join_level(
            target, level, how="right", keep_order=not self._is_multi
        )
    else:
        if self.equals(target):
            indexer = None
        else:
            if self._index_as_unique:
                indexer = self.get_indexer(
                    target, method=method, limit=limit, tolerance=tolerance
                )
            elif self._is_multi:
                raise ValueError("cannot handle a non-unique multi-index!")
            else:
                if method is not None or limit is not None:
                    raise ValueError(
                        "cannot reindex a non-unique index "
                        "with a method or limit"
                    )
                indexer, _ = self.get_indexer_non_unique(target)
            if not self.is_unique:
                raise ValueError("cannot reindex on an axis with duplicate labels")
    target = self._wrap_reindex_result(target, indexer, preserve_names)
    return target, indexer

def _align_series(
    self,
    other,
    join="outer",
    axis=None,
    level=None,
    copy = True,
    fill_value=None,
    method=None,
    limit=None,
    fill_axis=0,
):
    is_series = isinstance(self, ABCSeries)
    if (not is_series and axis is None) or axis not in [None, 0, 1]:
        raise ValueError("Must specify axis=0 or 1")
    if is_series and axis == 1:
        raise ValueError("cannot align series to a series other than axis 0")
    if not axis:
        if self.index.equals(other.index):
            join_index, lidx, ridx = None, None, None
        else:
            join_index, lidx, ridx = self.index.join(
                other.index, how=join, level=level, return_indexers=True
            )
        if is_series:
            left = self._reindex_indexer(join_index, lidx, copy)
        elif lidx is None:
            left = self.copy() if copy else self
        else:
            data = algos.take_nd(
                self.values,
                lidx,
                allow_fill=True,
                fill_value=None,
            )
            left = self._constructor(
                data=data, columns=self.columns, index=join_index
            )
        right = other._reindex_indexer(join_index, ridx, copy)
    else:
        fdata = self._mgr
        join_index = self.axes[1]
        lidx, ridx = None, None
        if not join_index.equals(other.index):
            join_index, lidx, ridx = join_index.join(
                other.index, how=join, level=level, return_indexers=True
            )
        if lidx is not None:
            bm_axis = self._get_block_manager_axis(1)
            fdata = fdata.reindex_indexer(join_index, lidx, axis=bm_axis)
        if copy and fdata is self._mgr:
            fdata = fdata.copy()
        left = self._constructor(fdata)
        if ridx is None:
            right = other
        else:
            right = other.reindex(join_index, level=level)
    fill_na = notna(fill_value) or (method is not None)
    if fill_na:
        left = left.fillna(fill_value, method=method, limit=limit, axis=fill_axis)
        right = right.fillna(fill_value, method=method, limit=limit)
    if is_series or (not is_series and axis == 0):
        left, right = _align_as_utc(left, right, join_index)
    return (
        left.__finalize__(self),
        right.__finalize__(other),
    )

def _read(
    filepath_or_buffer, kwds
):
    if (
        kwds.get("date_parser", None) is not None
        and kwds.get("parse_dates", None) is None
    ):
        kwds["parse_dates"] = True
    elif kwds.get("parse_dates", None) is None:
        kwds["parse_dates"] = False
    iterator = kwds.get("iterator", False)
    chunksize = kwds.get("chunksize", None)
    if kwds.get("engine") == "pyarrow":
        if iterator:
            raise ValueError(
                "The 'iterator' option is not supported with the 'pyarrow' engine"
            )
        if chunksize is not None:
            raise ValueError(
                "The 'chunksize' option is not supported with the 'pyarrow' engine"
            )
    else:
        chunksize = validate_integer("chunksize", kwds.get("chunksize", None), 1)
    nrows = kwds.get("nrows", None)
    _validate_names(kwds.get("names", None))
    parser = TextFileReader(filepath_or_buffer, **kwds)
    if chunksize or iterator:
        return parser
    with parser:
        return parser.read(nrows)

def _translate(self):
    ROW_HEADING_CLASS = "row_heading"
    COL_HEADING_CLASS = "col_heading"
    INDEX_NAME_CLASS = "index_name"
    DATA_CLASS = "data"
    BLANK_CLASS = "blank"
    BLANK_VALUE = "&nbsp;"
    ctx = self.ctx  
    cell_context = self.cell_context  
    cellstyle_map = defaultdict(list)
    table_styles = self.table_styles or []
    caption = self.caption
    hidden_index = self.hidden_index
    hidden_columns = self.hidden_columns
    uuid = self.uuid
    idx_lengths = _get_level_lengths(self.index)
    col_lengths = _get_level_lengths(self.columns, hidden_columns)
    n_rlvls = self.data.index.nlevels
    n_clvls = self.data.columns.nlevels
    rlabels = self.data.index.tolist()
    clabels = self.data.columns.tolist()
    if n_rlvls == 1:
        rlabels = [[x] for x in rlabels]
    if n_clvls == 1:
        clabels = [[x] for x in clabels]
    clabels = list(zip(*clabels))
    head = []
    for r in range(n_clvls):
        row_es = [
            {
                "type": "th",
                "value": BLANK_VALUE,
                "display_value": BLANK_VALUE,
                "is_visible": not hidden_index,
                "class": " ".join([BLANK_CLASS]),
            }
        ] * (n_rlvls - 1)
        name = self.data.columns.names[r]
        cs = [
            BLANK_CLASS if name is None else INDEX_NAME_CLASS,
            f"level{r}",
        ]
        name = BLANK_VALUE if name is None else name
        row_es.append(
            {
                "type": "th",
                "value": name,
                "display_value": name,
                "class": " ".join(cs),
                "is_visible": not hidden_index,
            }
        )
        if clabels:
            for c, value in enumerate(clabels[r]):
                es = {
                    "type": "th",
                    "value": value,
                    "display_value": value,
                    "class": f"{COL_HEADING_CLASS} level{r} col{c}",
                    "is_visible": _is_visible(c, r, col_lengths),
                }
                colspan = col_lengths.get((r, c), 0)
                if colspan > 1:
                    es["attributes"] = f'colspan="{colspan}"'
                row_es.append(es)
            head.append(row_es)
    if (
        self.data.index.names
        and com.any_not_none(*self.data.index.names)
        and not hidden_index
    ):
        index_header_row = []
        for c, name in enumerate(self.data.index.names):
            cs = [INDEX_NAME_CLASS, f"level{c}"]
            name = "" if name is None else name
            index_header_row.append(
                {"type": "th", "value": name, "class": " ".join(cs)}
            )
        index_header_row.extend(
            [
                {
                    "type": "th",
                    "value": BLANK_VALUE,
                    "class": " ".join([BLANK_CLASS, f"col{c}"]),
                }
                for c in range(len(clabels[0]))
                if c not in hidden_columns
            ]
        )
        head.append(index_header_row)
    body = []
    for r, row_tup in enumerate(self.data.itertuples()):
        row_es = []
        for c, value in enumerate(rlabels[r]):
            rid = [
                ROW_HEADING_CLASS,
                f"level{c}",
                f"row{r}",
            ]
            es = {
                "type": "th",
                "is_visible": (_is_visible(r, c, idx_lengths) and not hidden_index),
                "value": value,
                "display_value": value,
                "id": "_".join(rid[1:]),
                "class": " ".join(rid),
            }
            rowspan = idx_lengths.get((c, r), 0)
            if rowspan > 1:
                es["attributes"] = f'rowspan="{rowspan}"'
            row_es.append(es)
        for c, value in enumerate(row_tup[1:]):
            formatter = self._display_funcs[(r, c)]
            row_dict = {
                "type": "td",
                "value": value,
                "display_value": formatter(value),
                "is_visible": (c not in hidden_columns),
                "attributes": "",
            }
            props = []
            if self.cell_ids or (r, c) in ctx:
                row_dict["id"] = f"row{r}_col{c}"
                props.extend(ctx[r, c])
            cls = ""
            if (r, c) in cell_context:
                cls = " " + cell_context[r, c]
            row_dict["class"] = f"{DATA_CLASS} row{r} col{c}{cls}"
            row_es.append(row_dict)
            if props:  
                cellstyle_map[tuple(props)].append(f"row{r}_col{c}")
        body.append(row_es)
    cellstyle = [
        {"props": list(props), "selectors": selectors}
        for props, selectors in cellstyle_map.items()
    ]
    table_attr = self.table_attributes
    use_mathjax = get_option("display.html.use_mathjax")
    if not use_mathjax:
        table_attr = table_attr or ""
        if 'class="' in table_attr:
            table_attr = table_attr.replace('class="', 'class="tex2jax_ignore ')
        else:
            table_attr += ' class="tex2jax_ignore"'
    d = {
        "head": head,
        "cellstyle": cellstyle,
        "body": body,
        "uuid": uuid,
        "table_styles": _format_table_styles(table_styles),
        "caption": caption,
        "table_attributes": table_attr,
    }
    if self.tooltips:
        d = self.tooltips._translate(self.data, self.uuid, d)
    return d

def __init__(
    self,
    data,
    precision = None,
    table_styles = None,
    uuid = None,
    caption = None,
    table_attributes = None,
    cell_ids = True,
    na_rep = None,
    uuid_len = 5,
):
    if not isinstance(data, (pd.Series, pd.DataFrame)):
        raise TypeError("``data`` must be a Series or DataFrame")
    if data.ndim == 1:
        data = data.to_frame()
    if not data.index.is_unique or not data.columns.is_unique:
        raise ValueError("style is not supported for non-unique indices.")
    assert isinstance(data, DataFrame)
    self.data = data
    self.index = data.index
    self.columns = data.columns
    if precision is None:
        precision = get_option("display.precision")
    self.precision = precision
    self.table_styles = table_styles
    if not isinstance(uuid_len, int) or not uuid_len >= 0:
        raise TypeError("``uuid_len`` must be an integer in range [0, 32].")
    self.uuid_len = min(32, uuid_len)
    self.uuid = (uuid or uuid4().hex[: self.uuid_len]) + "_"
    self.caption = caption
    self.table_attributes = table_attributes
    self.cell_ids = cell_ids
    self.na_rep = na_rep
    self.hidden_index = False
    self.hidden_columns = []
    self.ctx = defaultdict(list)
    self.cell_context = {}
    self._todo = []
    self.tooltips = None
    self._display_funcs = defaultdict(lambda: self._default_display_func)

def maybe_upcast(
    values,
    fill_value = np.nan,
    dtype = None,
    copy = False,
):
    if not is_scalar(fill_value) and not is_object_dtype(values.dtype):
        raise ValueError("fill_value must be a scalar")
    if is_extension_array_dtype(values):
        if copy:
            values = values.copy()
    else:
        if dtype is None:
            dtype = values.dtype
        new_dtype, fill_value = maybe_promote(dtype, fill_value)
        if new_dtype != values.dtype:
            values = values.astype(new_dtype)
        elif copy:
            values = values.copy()
    return values, fill_value

def _cat_compare_op(op):
    opname = f"__{op.__name__}__"
    def func(self, other):
        if is_list_like(other) and len(other) != len(self):
            raise ValueError("Lengths must match.")
        if not self.ordered:
            if opname in ["__lt__", "__gt__", "__le__", "__ge__"]:
                raise TypeError(
                    "Unordered Categoricals can only compare equality or not"
                )
        if isinstance(other, Categorical):
            msg = "Categoricals can only be compared if 'categories' are the same."
            if len(self.categories) != len(other.categories):
                raise TypeError(msg + " Categories are different lengths")
            elif self.ordered and not (self.categories == other.categories).all():
                raise TypeError(msg)
            elif not set(self.categories) == set(other.categories):
                raise TypeError(msg)
            if not (self.ordered == other.ordered):
                raise TypeError(
                    "Categoricals can only be compared if 'ordered' is the same"
                )
            if not self.ordered and not self.categories.equals(other.categories):
                other_codes = _get_codes_for_values(other, self.categories)
            else:
                other_codes = other._codes
            f = getattr(self._codes, opname)
            ret = f(other_codes)
            mask = (self._codes == -1) | (other_codes == -1)
            if mask.any():
                if opname == "__ne__":
                    ret[(self._codes == -1) & (other_codes == -1)] = True
                else:
                    ret[mask] = False
            return ret
        if is_scalar(other):
            if other in self.categories:
                i = self.categories.get_loc(other)
                ret = getattr(self._codes, opname)(i)
                if opname not in {"__eq__", "__ge__", "__gt__"}:
                    mask = self._codes == -1
                    ret[mask] = False
                return ret
            else:
                return ops.invalid_comparison(self, other, op)
        else:
            if opname not in ["__eq__", "__ne__"]:
                raise TypeError(
                    f"Cannot compare a Categorical for op {opname} with "
                    f"type {type(other)}.\nIf you want to compare values, "
                    "use 'np.asarray(cat) <op> other'."
                )
            if isinstance(other, ExtensionArray) and needs_i8_conversion(other.dtype):
                return op(other, self)
            return getattr(np.array(self), opname)(np.array(other))
    func.__name__ = opname
    return func

def interpolate(
    self,
    method = "linear",
    axis = 0,
    limit = None,
    inplace = False,
    limit_direction = "forward",
    limit_area = None,
    downcast = None,
    **kwargs,
):
    inplace = validate_bool_kwarg(inplace, "inplace")
    axis = self._get_axis_number(axis)
    index = self._get_axis(axis)
    if isinstance(self.index, MultiIndex) and method != "linear":
        raise ValueError(
            "Only `method=linear` interpolation is supported on MultiIndexes."
        )
    if method in ["backfill", "bfill", "pad", "ffill"]:
        return self.fillna(
            method=method,
            axis=axis,
            inplace=inplace,
            limit=limit,
            downcast=downcast,
        )
    if axis == 0:
        df = self
    else:
        df = self.T
    if self.ndim == 2 and np.all(self.dtypes == np.dtype(object)):
        raise TypeError(
            "Cannot interpolate with all object-dtype columns "
            "in the DataFrame. Try setting at least one "
            "column to a numeric dtype."
        )
    if method == "linear":
        index = np.arange(len(df.index))
    else:
        methods = {"index", "values", "nearest", "time"}
        is_numeric_or_datetime = (
            is_numeric_dtype(index.dtype)
            or is_datetime64_any_dtype(index.dtype)
            or is_timedelta64_dtype(index.dtype)
        )
        if method not in methods and not is_numeric_or_datetime:
            raise ValueError(
                "Index column must be numeric or datetime type when "
                f"using {method} method other than linear. "
                "Try setting a numeric or datetime index column before "
                "interpolating."
            )
    if isna(index).any():
        raise NotImplementedError(
            "Interpolation with NaNs in the index "
            "has not been implemented. Try filling "
            "those NaNs before interpolating."
        )
    data = df._mgr
    new_data = data.interpolate(
        method=method,
        axis=self._info_axis_number,
        index=index,
        limit=limit,
        limit_direction=limit_direction,
        limit_area=limit_area,
        inplace=inplace,
        downcast=downcast,
        **kwargs,
    )
    result = self._constructor(new_data)
    if axis == 1:
        result = result.T
    if inplace:
        return self._update_inplace(result)
    else:
        return result.__finalize__(self, method="interpolate")

def maybe_upcast_putmask(result, mask, other):
    if not isinstance(result, np.ndarray):
        raise ValueError("The result input must be a ndarray.")
    if not is_scalar(other):
        raise ValueError("other must be a scalar")
    if mask.any():
        if result.dtype.kind in ["m", "M"]:
            if is_scalar(other):
                if isna(other):
                    other = result.dtype.type("nat")
                elif is_integer(other):
                    other = np.array(other, dtype=result.dtype)
            elif is_integer_dtype(other):
                other = np.array(other, dtype=result.dtype)
        def changeit():
            try:
                om = other[mask]
            except (IndexError, TypeError):
                pass
            else:
                om_at = om.astype(result.dtype)
                if (om == om_at).all():
                    new_result = result.values.copy()
                    new_result[mask] = om_at
                    result[:] = new_result
                    return result, False
            r, _ = maybe_upcast(result, fill_value=other, copy=True)
            np.place(r, mask, other)
            return r, True
        new_dtype, _ = maybe_promote(result.dtype, other)
        if new_dtype != result.dtype:
            if is_scalar(other) or (isinstance(other, np.ndarray) and other.ndim < 1):
                if isna(other):
                    return changeit()
            else:
                if isna(other).any():
                    return changeit()
        try:
            np.place(result, mask, other)
        except TypeError:
            return changeit()
    return result, False

def __getitem__(self, key):
    key = com.apply_if_callable(key, self)
    if key is Ellipsis:
        return self
    key_is_scalar = is_scalar(key)
    if isinstance(key, (list, tuple)):
        key = unpack_1tuple(key)
    if key_is_scalar or isinstance(self.index, MultiIndex):
        try:
            result = self.index.get_value(self, key)
            return result
        except InvalidIndexError:
            if not isinstance(self.index, MultiIndex):
                raise
        except (KeyError, ValueError):
            if isinstance(key, tuple) and isinstance(self.index, MultiIndex):
                pass
            else:
                raise
    if not key_is_scalar:
        if is_iterator(key):
            key = list(key)
        if com.is_bool_indexer(key):
            key = check_bool_indexer(self.index, key)
            key = np.asarray(key, dtype=bool)
            return self._get_values(key)
    return self._get_with(key)

def _shallow_copy(self, values=None, **kwargs):
    if values is not None:
        names = kwargs.pop("names", kwargs.pop("name", self.names))
        kwargs.pop("freq", None)
        return MultiIndex.from_tuples(values, names=names, **kwargs)
    result = self.copy(**kwargs)
    result._cache = self._cache.copy()
    if "levels" in result._cache:
        del result._cache["levels"]
    return result

def _setitem_with_indexer(self, indexer, value):
    from pandas import Series
    info_axis = self.obj._info_axis_number
    take_split_path = self.obj._is_mixed_type
    if not take_split_path and self.obj._data.blocks:
        (blk,) = self.obj._data.blocks
        if 1 < blk.ndim:  
            val = list(value.values()) if isinstance(value, dict) else value
            take_split_path = not blk._can_hold_element(val)
    if isinstance(indexer, tuple) and len(indexer) == len(self.obj.axes):
        for i, ax in zip(indexer, self.obj.axes):
            if isinstance(ax, ABCMultiIndex) and not (
                is_integer(i) or com.is_null_slice(i)
            ):
                take_split_path = True
                break
    if isinstance(indexer, tuple):
        nindexer = []
        for i, idx in enumerate(indexer):
            if isinstance(idx, dict):
                key, _ = convert_missing_indexer(idx)
                if self.ndim > 1 and i == self.obj._info_axis_number:
                    len_non_info_axes = (
                        len(_ax) for _i, _ax in enumerate(self.obj.axes) if _i != i
                    )
                    if any(not l for l in len_non_info_axes):
                        if not is_list_like_indexer(value):
                            raise ValueError(
                                "cannot set a frame with no "
                                "defined index and a scalar"
                            )
                        self.obj[key] = value
                        return
                    self.obj[key] = _infer_fill_value(value)
                    new_indexer = convert_from_missing_indexer_tuple(
                        indexer, self.obj.axes
                    )
                    self._setitem_with_indexer(new_indexer, value)
                    return
                index = self.obj._get_axis(i)
                labels = index.insert(len(index), key)
                self.obj._data = self.obj.reindex(labels, axis=i)._data
                self.obj._maybe_update_cacher(clear=True)
                self.obj._is_copy = None
                nindexer.append(labels.get_loc(key))
            else:
                nindexer.append(idx)
        indexer = tuple(nindexer)
    else:
        indexer, missing = convert_missing_indexer(indexer)
        if missing:
            self._setitem_with_indexer_missing(indexer, value)
            return
    item_labels = self.obj._get_axis(info_axis)
    if take_split_path:
        assert self.ndim == 2
        assert info_axis == 1
        if not isinstance(indexer, tuple):
            indexer = _tuplify(self.ndim, indexer)
        if isinstance(value, ABCSeries):
            value = self._align_series(indexer, value)
        info_idx = indexer[info_axis]
        if is_integer(info_idx):
            info_idx = [info_idx]
        labels = item_labels[info_idx]
        if len(labels) == 1 and isinstance(
            self.obj[labels[0]].axes[0], ABCMultiIndex
        ):
            item = labels[0]
            obj = self.obj[item]
            index = obj.index
            idx = indexer[:info_axis][0]
            plane_indexer = tuple([idx]) + indexer[info_axis + 1 :]
            lplane_indexer = length_of_indexer(plane_indexer[0], index)
            if is_list_like_indexer(value) and lplane_indexer != len(value):
                raise ValueError(
                    "cannot set using a multi-index "
                    "selection indexer with a different "
                    "length than the value"
                )
        else:
            plane_indexer = indexer[:info_axis] + indexer[info_axis + 1 :]
            plane_axis = self.obj.axes[:info_axis][0]
            lplane_indexer = length_of_indexer(plane_indexer[0], plane_axis)
        def setter(item, v):
            s = self.obj[item]
            pi = plane_indexer[0] if lplane_indexer == 1 else plane_indexer
            if isinstance(pi, tuple) and all(
                com.is_null_slice(idx) or com.is_full_slice(idx, len(self.obj))
                for idx in pi
            ):
                s = v
            else:
                s._consolidate_inplace()
                s = s.copy()
                s._data = s._data.setitem(indexer=pi, value=v)
                s._maybe_update_cacher(clear=True)
            self.obj[item] = s
        if is_list_like_indexer(value) and getattr(value, "ndim", 1) > 0:
            if isinstance(value, ABCDataFrame):
                sub_indexer = list(indexer)
                multiindex_indexer = isinstance(labels, ABCMultiIndex)
                for item in labels:
                    if item in value:
                        sub_indexer[info_axis] = item
                        v = self._align_series(
                            tuple(sub_indexer), value[item], multiindex_indexer
                        )
                    else:
                        v = np.nan
                    setter(item, v)
            elif np.ndim(value) == 2:
                value = np.array(value, dtype=object)
                if len(labels) != value.shape[1]:
                    raise ValueError(
                        "Must have equal len keys and value "
                        "when setting with an ndarray"
                    )
                for i, item in enumerate(labels):
                    setter(item, value[:, i].tolist())
            elif _can_do_equal_len(
                labels, value, plane_indexer, lplane_indexer, self.obj
            ):
                setter(labels[0], value)
            else:
                if len(labels) != len(value):
                    raise ValueError(
                        "Must have equal len keys and value "
                        "when setting with an iterable"
                    )
                for item, v in zip(labels, value):
                    setter(item, v)
        else:
            for item in labels:
                setter(item, value)
    else:
        if isinstance(indexer, tuple):
            indexer = maybe_convert_ix(*indexer)
            if (
                len(indexer) > info_axis
                and is_integer(indexer[info_axis])
                and all(
                    com.is_null_slice(idx)
                    for i, idx in enumerate(indexer)
                    if i != info_axis
                )
                and item_labels.is_unique
            ):
                self.obj[item_labels[indexer[info_axis]]] = value
                return
        if isinstance(value, (ABCSeries, dict)):
            value = self._align_series(indexer, Series(value))
        elif isinstance(value, ABCDataFrame):
            value = self._align_frame(indexer, value)
        self.obj._check_is_chained_assignment_possible()
        self.obj._consolidate_inplace()
        self.obj._data = self.obj._data.setitem(indexer=indexer, value=value)
        self.obj._maybe_update_cacher(clear=True)

def __contains__(self, other):
    if super().__contains__(other):
        return True
    try:
        return np.isnan(other) and self.hasnans
    except ValueError:
        try:
            return len(other) <= 1 and other.item() in self
        except AttributeError:
            return len(other) <= 1 and other in self
        except TypeError:
            pass
    except TypeError:
        pass
    return False

def create_axes(
    self,
    axes,
    obj,
    validate = True,
    nan_rep=None,
    data_columns=None,
    min_itemsize=None,
):
    if axes is None:
        try:
            axes = _AXES_MAP[type(obj)]
        except KeyError:
            group = self.group._v_name
            raise TypeError(
                f"cannot properly create the storer for: [group->{group},"
                f"value->{type(obj)}]"
            )
    axes = [obj._get_axis_number(a) for a in axes]
    if self.infer_axes():
        existing_table = self.copy()
        existing_table.infer_axes()
        axes = [a.axis for a in existing_table.index_axes]
        data_columns = existing_table.data_columns
        nan_rep = existing_table.nan_rep
        self.encoding = existing_table.encoding
        self.errors = existing_table.errors
        self.info = copy.copy(existing_table.info)
    else:
        existing_table = None
    if len(axes) != self.ndim - 1:
        raise ValueError(
            "currently only support ndim-1 indexers in an AppendableTable"
        )
    new_non_index_axes = []
    new_data_columns = []
    if nan_rep is None:
        nan_rep = "nan"
    index_axes_map = dict()
    for i, a in enumerate(obj.axes):
        if i in axes:
            name = obj._AXIS_NAMES[i]
            new_index = _convert_index(name, a, self.encoding, self.errors)
            new_index.axis = i
            index_axes_map[i] = new_index
        else:
            append_axis = list(a)
            if existing_table is not None:
                indexer = len(new_non_index_axes)
                exist_axis = existing_table.non_index_axes[indexer][1]
                if not array_equivalent(
                    np.array(append_axis), np.array(exist_axis)
                ):
                    if array_equivalent(
                        np.array(sorted(append_axis)), np.array(sorted(exist_axis))
                    ):
                        append_axis = exist_axis
            info = _get_info(self.info, i)
            info["names"] = list(a.names)
            info["type"] = type(a).__name__
            new_non_index_axes.append((i, append_axis))
    self.non_index_axes = new_non_index_axes
    new_index_axes = [index_axes_map[a] for a in axes]
    for j, iax in enumerate(new_index_axes):
        iax.set_pos(j)
        iax.update_info(self.info)
    j = len(new_index_axes)
    for a in new_index_axes:
        a.maybe_set_size(min_itemsize=min_itemsize)
    for a in new_non_index_axes:
        obj = _reindex_axis(obj, a[0], a[1])
    def get_blk_items(mgr, blocks):
        return [mgr.items.take(blk.mgr_locs) for blk in blocks]
    transposed = new_index_axes[0].axis == 1
    block_obj = self.get_object(obj, transposed)._consolidate()
    blocks = block_obj._data.blocks
    blk_items = get_blk_items(block_obj._data, blocks)
    if len(new_non_index_axes):
        axis, axis_labels = new_non_index_axes[0]
        data_columns = self.validate_data_columns(data_columns, min_itemsize)
        if len(data_columns):
            mgr = block_obj.reindex(
                Index(axis_labels).difference(Index(data_columns)), axis=axis
            )._data
            blocks = list(mgr.blocks)
            blk_items = get_blk_items(mgr, blocks)
            for c in data_columns:
                mgr = block_obj.reindex([c], axis=axis)._data
                blocks.extend(mgr.blocks)
                blk_items.extend(get_blk_items(mgr, mgr.blocks))
    if existing_table is not None:
        by_items = {
            tuple(b_items.tolist()): (b, b_items)
            for b, b_items in zip(blocks, blk_items)
        }
        new_blocks = []
        new_blk_items = []
        for ea in existing_table.values_axes:
            items = tuple(ea.values)
            try:
                b, b_items = by_items.pop(items)
                new_blocks.append(b)
                new_blk_items.append(b_items)
            except (IndexError, KeyError):
                jitems = ",".join(pprint_thing(item) for item in items)
                raise ValueError(
                    f"cannot match existing table structure for [{jitems}] "
                    "on appending data"
                )
        blocks = new_blocks
        blk_items = new_blk_items
    vaxes = []
    for i, (b, b_items) in enumerate(zip(blocks, blk_items)):
        klass = DataCol
        name = None
        if data_columns and len(b_items) == 1 and b_items[0] in data_columns:
            klass = DataIndexableCol
            name = b_items[0]
            if not (name is None or isinstance(name, str)):
                raise ValueError("cannot have non-object label DataIndexableCol")
            new_data_columns.append(name)
        if existing_table is not None and validate:
            try:
                existing_col = existing_table.values_axes[i]
            except (IndexError, KeyError):
                raise ValueError(
                    f"Incompatible appended table [{blocks}]"
                    f"with existing table [{existing_table.values_axes}]"
                )
        else:
            existing_col = None
        col = klass.create_for_block(i=i, name=name, version=self.version)
        col.values = list(b_items)
        col.set_atom(
            block=b,
            existing_col=existing_col,
            min_itemsize=min_itemsize,
            nan_rep=nan_rep,
            encoding=self.encoding,
            errors=self.errors,
            info=self.info,
        )
        col.set_pos(j)
        vaxes.append(col)
        j += 1
    self.nan_rep = nan_rep
    self.data_columns = new_data_columns
    self.values_axes = vaxes
    self.index_axes = new_index_axes
    self.validate_min_itemsize(min_itemsize)
    self.metadata = [c.name for c in self.values_axes if c.metadata is not None]
    if validate:
        self.validate(existing_table)

def _comp_method_SERIES(cls, op, special):
    op_name = _get_op_name(op, special)
    def na_op(x, y):
        if is_object_dtype(x.dtype):
            result = comp_method_OBJECT_ARRAY(op, x, y)
        else:
            method = getattr(x, op_name)
            with np.errstate(all="ignore"):
                result = method(y)
            if result is NotImplemented:
                return invalid_comparison(x, y, op)
        return result
    def wrapper(self, other):
        res_name = get_op_result_name(self, other)
        other = lib.item_from_zerodim(other)
        finalizer = (
            lambda x: x.__finalize__(self)
            if isinstance(other, (np.ndarray, ABCIndexClass))
            else x
        )
        if isinstance(other, list):
            other = np.asarray(other)
        if isinstance(other, ABCDataFrame):  
            return NotImplemented
        if isinstance(other, ABCSeries) and not self._indexed_same(other):
            raise ValueError("Can only compare identically-labeled Series objects")
        elif isinstance(
            other, (np.ndarray, ABCExtensionArray, ABCIndexClass, ABCSeries)
        ):
            if len(self) != len(other):
                raise ValueError("Lengths must match to compare")
        lvalues = extract_array(self, extract_numpy=True)
        rvalues = extract_array(other, extract_numpy=True)
        if should_extension_dispatch(lvalues, rvalues):
            res_values = dispatch_to_extension_op(op, lvalues, rvalues)
        elif is_scalar(rvalues) and isna(rvalues):
            if op is operator.ne:
                res_values = np.ones(len(lvalues), dtype=bool)
            else:
                res_values = np.zeros(len(lvalues), dtype=bool)
        else:
            with np.errstate(all="ignore"):
                res_values = na_op(lvalues, rvalues)
            if is_scalar(res_values):
                raise TypeError(
                    "Could not compare {typ} type with Series".format(typ=type(rvalues))
                )
        result = self._constructor(res_values, index=self.index)
        result = finalizer(result)
        result.name = res_name
        return result
    wrapper.__name__ = op_name
    return wrapper

def _bool_method_SERIES(cls, op, special):
    op_name = _get_op_name(op, special)
    def na_op(x, y):
        try:
            result = op(x, y)
        except TypeError:
            assert not isinstance(y, (list, ABCSeries, ABCIndexClass))
            if isinstance(y, np.ndarray):
                assert not (is_bool_dtype(x.dtype) and is_bool_dtype(y.dtype))
                x = ensure_object(x)
                y = ensure_object(y)
                result = libops.vec_binop(x, y, op)
            else:
                assert lib.is_scalar(y)
                if not isna(y):
                    y = bool(y)
                try:
                    result = libops.scalar_binop(x, y, op)
                except (
                    TypeError,
                    ValueError,
                    AttributeError,
                    OverflowError,
                    NotImplementedError,
                ):
                    raise TypeError(
                        "cannot compare a dtyped [{dtype}] array "
                        "with a scalar of type [{typ}]".format(
                            dtype=x.dtype, typ=type(y).__name__
                        )
                    )
        return result
    fill_int = lambda x: x.fillna(0)
    def fill_bool(x, left=None):
        x = x.fillna(False)
        if left is None or is_bool_dtype(left.dtype):
            x = x.astype(bool)
        return x
    def wrapper(self, other):
        is_self_int_dtype = is_integer_dtype(self.dtype)
        self, other = _align_method_SERIES(self, other, align_asobject=True)
        res_name = get_op_result_name(self, other)
        finalizer = (
            lambda x: x.__finalize__(self)
            if not isinstance(other, (ABCSeries, ABCIndexClass))
            else x
        )
        if isinstance(other, ABCDataFrame):
            return NotImplemented
        elif should_extension_dispatch(self, other):
            lvalues = extract_array(self, extract_numpy=True)
            rvalues = extract_array(other, extract_numpy=True)
            res_values = dispatch_to_extension_op(op, lvalues, rvalues)
            result = self._constructor(res_values, index=self.index, name=res_name)
            return finalizer(result)
        elif isinstance(other, (ABCSeries, ABCIndexClass)):
            is_other_int_dtype = is_integer_dtype(other.dtype)
            other = other if is_other_int_dtype else fill_bool(other, self)
        elif is_list_like(other):
            if not isinstance(other, np.ndarray):
                other = construct_1d_object_array_from_listlike(other)
            is_other_int_dtype = is_integer_dtype(other.dtype)
            other = type(self)(other)
            other = other if is_other_int_dtype else fill_bool(other, self)
        else:
            is_other_int_dtype = lib.is_integer(other)
        ovalues = lib.values_from_object(other)
        filler = fill_int if is_self_int_dtype and is_other_int_dtype else fill_bool
        res_values = na_op(self.values, ovalues)
        unfilled = self._constructor(res_values, index=self.index, name=res_name)
        filled = filler(unfilled)
        return finalizer(filled)
    wrapper.__name__ = op_name
    return wrapper

def wrapper(self, other, axis=None):
    if axis is not None:
        self._get_axis_number(axis)
    res_name = get_op_result_name(self, other)
    if isinstance(other, list):
        other = np.asarray(other)
    if isinstance(other, ABCDataFrame):  
        return NotImplemented
    elif isinstance(other, ABCSeries) and not self._indexed_same(other):
        raise ValueError("Can only compare identically-labeled Series objects")
    elif is_categorical_dtype(self):
        res_values = dispatch_to_extension_op(op, self, other)
        return self._constructor(res_values, index=self.index, name=res_name)
    elif is_datetime64_dtype(self) or is_datetime64tz_dtype(self):
        from pandas.core.arrays import DatetimeArray
        res_values = dispatch_to_extension_op(op, DatetimeArray(self), other)
        return self._constructor(res_values, index=self.index, name=res_name)
    elif is_timedelta64_dtype(self):
        from pandas.core.arrays import TimedeltaArray
        res_values = dispatch_to_extension_op(op, TimedeltaArray(self), other)
        return self._constructor(res_values, index=self.index, name=res_name)
    elif is_extension_array_dtype(self) or (
        is_extension_array_dtype(other) and not is_scalar(other)
    ):
        res_values = dispatch_to_extension_op(op, self, other)
        return self._constructor(res_values, index=self.index).rename(res_name)
    elif isinstance(other, ABCSeries):
        res_values = na_op(self.values, other.values)
        return self._constructor(
            res_values, index=self.index, name=res_name
        ).rename(res_name)
    elif isinstance(other, (np.ndarray, ABCIndexClass)):
        if other.ndim != 0 and len(self) != len(other):
            raise ValueError("Lengths must match to compare")
        res_values = na_op(self.values, np.asarray(other))
        result = self._constructor(res_values, index=self.index)
        return result.__finalize__(self).rename(res_name)
    elif is_scalar(other) and isna(other):
        if op is operator.ne:
            res_values = np.ones(len(self), dtype=bool)
        else:
            res_values = np.zeros(len(self), dtype=bool)
        return self._constructor(
            res_values, index=self.index, name=res_name, dtype="bool"
        )
    else:
        values = self.to_numpy()
        with np.errstate(all="ignore"):
            res = na_op(values, other)
        if is_scalar(res):
            raise TypeError(
                "Could not compare {typ} type with Series".format(typ=type(other))
            )
        res_values = extract_array(res, extract_numpy=True)
        return self._constructor(
            res_values, index=self.index, name=res_name, dtype="bool"
        )

def process_input(self, data, input_prompt, lineno):
    decorator, input, rest = data
    image_file = None
    image_directive = None
    is_verbatim = decorator=='@verbatim' or self.is_verbatim
    is_doctest = (decorator is not None and \
                     decorator.startswith('@doctest')) or self.is_doctest
    is_suppress = decorator=='@suppress' or self.is_suppress
    is_okexcept = decorator=='@okexcept' or self.is_okexcept
    is_okwarning = decorator=='@okwarning' or self.is_okwarning
    is_savefig = decorator is not None and \
                     decorator.startswith('@savefig')
    input_lines = input.split('\n')
    if len(input_lines) > 1:
       if input_lines[-1] != "":
           input_lines.append('') 
    continuation = '   %s:'%''.join(['.']*(len(str(lineno))+2))
    if is_savefig:
        image_file, image_directive = self.process_image(decorator)
    ret = []
    is_semicolon = False
    if is_suppress and self.hold_count:
        store_history = False
    else:
        store_history = True
    with warnings.catch_warnings(record=True) as ws:
        for i, line in enumerate(input_lines):
            if line.endswith(';'):
                is_semicolon = True
            if i == 0:
                if is_verbatim:
                    self.process_input_line('')
                    self.IP.execution_count += 1 
                else:
                    self.process_input_line(line, store_history=store_history)
                formatted_line = '%s %s'%(input_prompt, line)
            else:
                if not is_verbatim:
                    self.process_input_line(line, store_history=store_history)
                formatted_line = '%s %s'%(continuation, line)
            if not is_suppress:
                ret.append(formatted_line)
    if not is_suppress and len(rest.strip()) and is_verbatim:
        ret.append(rest)
    self.cout.seek(0)
    output = self.cout.read()
    if not is_suppress and not is_semicolon:
        ret.append(output)
    elif is_semicolon: 
        ret.append('')
    filename = self.state.document.current_source
    lineno = self.state.document.current_line
    if not is_okexcept and "Traceback" in output:
        s =  "\nException in %s at block ending on line %s\n" % (filename, lineno)
        sys.stdout.write('\n\n>>>'+'-'*73)
        sys.stdout.write(s)
        sys.stdout.write(output)
        sys.stdout.write('<<<' + '-'*73+'\n\n')
    if not is_okwarning:
        import textwrap
        for w in ws:
            s =  "\nWarning in %s at block ending on line %s\n" % (filename, lineno)
            sys.stdout.write('\n\n>>>'+'-'*73)
            sys.stdout.write(s)
            sys.stdout.write('-'*76+'\n')
            s=warnings.formatwarning(w.message, w.category,
                                     w.filename, w.lineno, w.line)
            sys.stdout.write('\n'.join(textwrap.wrap(s,80)))
            sys.stdout.write('\n<<<' + '-'*73+'\n')
    self.cout.truncate(0)
    return (ret, input_lines, output, is_doctest, decorator, image_file,
                image_directive)

def process_input(self, data, input_prompt, lineno):
    decorator, input, rest = data
    image_file = None
    image_directive = None
    is_verbatim = decorator=='@verbatim' or self.is_verbatim
    is_doctest = (decorator is not None and \
                     decorator.startswith('@doctest')) or self.is_doctest
    is_suppress = decorator=='@suppress' or self.is_suppress
    is_okexcept = decorator=='@okexcept' or self.is_okexcept
    is_okwarning = decorator=='@okwarning' or self.is_okwarning
    is_savefig = decorator is not None and \
                     decorator.startswith('@savefig')
    input_lines = input.split('\n')
    if len(input_lines) > 1:
       if input_lines[-1] != "":
           input_lines.append('') 
    continuation = '   %s:'%''.join(['.']*(len(str(lineno))+2))
    if is_savefig:
        image_file, image_directive = self.process_image(decorator)
    ret = []
    is_semicolon = False
    if is_suppress and self.hold_count:
        store_history = False
    else:
        store_history = True
    with warnings.catch_warnings(record=True) as ws:
        for i, line in enumerate(input_lines):
            if line.endswith(';'):
                is_semicolon = True
            if i == 0:
                if is_verbatim:
                    self.process_input_line('')
                    self.IP.execution_count += 1 
                else:
                    self.process_input_line(line, store_history=store_history)
                formatted_line = '%s %s'%(input_prompt, line)
            else:
                if not is_verbatim:
                    self.process_input_line(line, store_history=store_history)
                formatted_line = '%s %s'%(continuation, line)
            if not is_suppress:
                ret.append(formatted_line)
    if not is_suppress and len(rest.strip()) and is_verbatim:
        ret.append(rest)
    self.cout.seek(0)
    output = self.cout.read()
    if not is_suppress and not is_semicolon:
        ret.append(output)
    elif is_semicolon: 
        ret.append('')
    filename = self.state.document.current_source
    lineno = self.state.document.current_line
    try:
        lineno -= 1
    except:
        pass
    if not is_okexcept and "Traceback" in output:
        s =  "\nException in %s at line %s:\n" % (filename, lineno)
        sys.stdout.write('\n\n>>>'+'-'*73)
        sys.stdout.write(s)
        sys.stdout.write(output)
        sys.stdout.write('<<<' + '-'*73+'\n\n')
    if not is_okwarning:
        for w in ws:
            s =  "\nWarning raised in %s at line %s:\n" % (filename, lineno)
            sys.stdout.write('\n\n>>>'+'-'*73)
            sys.stdout.write(s)
            sys.stdout.write('-'*76+'\n')
            s=warnings.formatwarning(w.message, w.category,
                                     w.filename, w.lineno, w.line)
            sys.stdout.write(s)
            sys.stdout.write('\n<<<' + '-'*73+'\n\n')
    self.cout.truncate(0)
    return (ret, input_lines, output, is_doctest, decorator, image_file,
                image_directive)

def __init__(self, data=None, aes=None):
    self.data = data
    if aes is None:
        self.aes = make_aes()
    else:
        self.aes = aes
    self.legend = {}

def _write_lock_file(self, repo, force = False):
    if force or (self._update and self._write_lock):
        updated_lock = self._locker.set_lock_data(self._package, repo.packages)
        if updated_lock:
            self._io.write_line("")
            self._io.write_line("<info>Writing lock file</>")

def _do_install(self, local_repo):
    locked_repository = Repository()
    if self._update:
        if self._locker.is_locked() and not self._lock:
            locked_repository = self._locker.locked_repository(True)
            if not self._whitelist:
                for pkg in locked_repository.packages:
                    self._whitelist.append(pkg.name)
        for extra in self._extras:
            if extra not in self._package.extras:
                raise ValueError("Extra [{}] is not specified.".format(extra))
        self._io.write_line("<info>Updating dependencies</>")
        solver = Solver(
            self._package,
            self._pool,
            self._installed_repository,
            locked_repository,
            self._io,
            remove_untracked=self._remove_untracked,
        )
        ops = solver.solve(use_latest=self._whitelist)
    else:
        self._io.write_line("<info>Installing dependencies from lock file</>")
        locked_repository = self._locker.locked_repository(True)
        if not self._locker.is_fresh():
            self._io.write_line(
                "<warning>"
                "Warning: The lock file is not up to date with "
                "the latest changes in pyproject.toml. "
                "You may be getting outdated dependencies. "
                "Run update to update them."
                "</warning>"
            )
        for extra in self._extras:
            if extra not in self._locker.lock_data.get("extras", {}):
                raise ValueError("Extra [{}] is not specified.".format(extra))
        ops = self._get_operations_from_lock(locked_repository)
    self._populate_local_repo(local_repo, ops)
    if self._update:
        self._write_lock_file(local_repo)
        if self._lock:
            return 0
    root = self._package
    if not self.is_dev_mode():
        root = root.clone()
        del root.dev_requires[:]
    if self._io.is_verbose():
        self._io.write_line("")
        self._io.write_line(
            "<info>Finding the necessary packages for the current system</>"
        )
    pool = Pool(ignore_repository_names=True)
    repo = Repository()
    for package in local_repo.packages + locked_repository.packages:
        if not repo.has_package(package):
            repo.add_package(package)
    pool.add_repository(repo)
    whitelist = []
    for pkg in locked_repository.packages:
        whitelist.append(pkg.name)
    solver = Solver(
        root,
        pool,
        self._installed_repository,
        locked_repository,
        NullIO(),
        remove_untracked=self._remove_untracked,
    )
    with solver.use_environment(self._env):
        ops = solver.solve(use_latest=whitelist)
    self._filter_operations(ops, local_repo)
    self._io.write_line("")
    actual_ops = [op for op in ops if not op.skipped]
    if not actual_ops and (self._execute_operations or self._dry_run):
        self._io.write_line("No dependencies to install or update")
    if actual_ops and (self._execute_operations or self._dry_run):
        installs = []
        updates = []
        uninstalls = []
        skipped = []
        for op in ops:
            if op.skipped:
                skipped.append(op)
                continue
            if op.job_type == "install":
                installs.append(
                    "{}:{}".format(
                        op.package.pretty_name, op.package.full_pretty_version
                    )
                )
            elif op.job_type == "update":
                updates.append(
                    "{}:{}".format(
                        op.target_package.pretty_name,
                        op.target_package.full_pretty_version,
                    )
                )
            elif op.job_type == "uninstall":
                uninstalls.append(op.package.pretty_name)
        self._io.write_line("")
        self._io.write_line(
            "Package operations: "
            "<info>{}</> install{}, "
            "<info>{}</> update{}, "
            "<info>{}</> removal{}"
            "{}".format(
                len(installs),
                "" if len(installs) == 1 else "s",
                len(updates),
                "" if len(updates) == 1 else "s",
                len(uninstalls),
                "" if len(uninstalls) == 1 else "s",
                ", <info>{}</> skipped".format(len(skipped))
                if skipped and self.is_verbose()
                else "",
            )
        )
    self._io.write_line("")
    for op in ops:
        self._execute(op)

def solve(self, use_latest=None):  
    provider = Provider(self._package, self._pool, self._io)
    locked = {}
    for package in self._locked.packages:
        locked[package.name] = package
    try:
        result = resolve_version(self._package, provider, locked=locked, use_latest=use_latest)
    except SolveFailure as e:
        raise SolverProblemError(e)
    packages = result.packages
    requested = self._package.all_requires
    for package in packages:
        category, optional, python, platform = self._get_tags_for_package(
            package, packages, requested
        )
        package.category = category
        package.optional = optional
        requirements = {}
        if python is not None and python != '*':
            requirements['python'] = python
        if platform is not None and platform != '*':
            requirements['platform'] = platform
        package.requirements = requirements
    operations = []
    for package in packages:
        installed = False
        for pkg in self._installed.packages:
            if package.name == pkg.name:
                installed = True
                if package.version != pkg.version:
                    operations.append(Update(pkg, package))
                else:
                    operations.append(
                        Install(package).skip('Already installed')
                    )
                break
        if not installed:
            operations.append(Install(package))
    for pkg in self._locked.packages:
        remove = True
        for package in packages:
            if pkg.name == package.name:
                remove = False
                break
        if remove:
            skip = True
            for installed in self._installed.packages:
                if installed.name == pkg.name:
                    skip = False
                    break
            op = Uninstall(pkg)
            if skip:
                op.skip('Not currently installed')
            operations.append(op)
    requested_names = [r.name for r in self._package.all_requires]
    return sorted(
        operations,
        key=lambda o: (
            1 if not o.package.name not in requested_names else 0,
            o.package.name
        )
    )

def lower_upper_decomposition(table):
    rows, columns = np.shape(table)
    if rows != columns:
        msg = (
            "'table' has to be of square shaped array but got a "
            f"{rows}x{columns} array:\n{table}"
        )
        raise ValueError(msg)
    lower = np.zeros((rows, columns))
    upper = np.zeros((rows, columns))
    for i in range(columns):
        for j in range(i):
            total = sum(lower[i][k] * upper[k][j] for k in range(j))
            if upper[j][j] == 0:
                raise ArithmeticError("No LU decomposition exists")
            lower[i][j] = (table[i][j] - total) / upper[j][j]
        lower[i][i] = 1
        for j in range(i, columns):
            total = sum(lower[i][k] * upper[k][j] for k in range(j))
            upper[i][j] = table[i][j] - total
    return lower, upper

def get_amazon_product_data(product = "laptop"):
    url = f"https://www.amazon.in/laptop/s?k={product}"
    header = {
        "User-Agent": """Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36
        (KHTML, like Gecko)Chrome/44.0.2403.157 Safari/537.36""",
        "Accept-Language": "en-US, en;q=0.5",
    }
    soup = BeautifulSoup(requests.get(url, headers=header).text)
    data_frame = DataFrame(
        columns=[
            "Product Title",
            "Product Link",
            "Current Price of the product",
            "Product Rating",
            "MRP of the product",
            "Discount",
        ]
    )
    for item, _ in zip_longest(
        soup.find_all(
            "div",
            attrs={"class": "s-result-item", "data-component-type": "s-search-result"},
        ),
        soup.find_all("div", attrs={"class": "a-row a-size-base a-color-base"}),
    ):
        try:
            product_title = item.h2.text
            product_link = "https://www.amazon.in/" + item.h2.a["href"]
            product_price = item.find("span", attrs={"class": "a-offscreen"}).text
            try:
                product_rating = item.find("span", attrs={"class": "a-icon-alt"}).text
            except AttributeError:
                product_rating = "Not available"
            try:
                product_mrp = (
                    "₹"
                    + item.find(
                        "span", attrs={"class": "a-price a-text-price"}
                    ).text.split("₹")[1]
                )
            except AttributeError:
                product_mrp = ""
            try:
                discount = float(
                    (
                        (
                            float(product_mrp.strip("₹").replace(",", ""))
                            - float(product_price.strip("₹").replace(",", ""))
                        )
                        / float(product_mrp.strip("₹").replace(",", ""))
                    )
                    * 100
                )
            except ValueError:
                discount = float("nan")
        except AttributeError:
            pass
        data_frame.loc[len(data_frame.index)] = [
            product_title,
            product_link,
            product_price,
            product_rating,
            product_mrp,
            discount,
        ]
    data_frame.loc[
        data_frame["Current Price of the product"] > data_frame["MRP of the product"],
        "MRP of the product",
    ] = " "
    data_frame.loc[
        data_frame["Current Price of the product"] > data_frame["MRP of the product"],
        "Discount",
    ] = " "
    data_frame.index += 1
    return data_frame

def climb_stairs(n):
    assert (
        isinstance(n, int) and n > 0
    ), f"n needs to be positive integer, your input {n}"
    if n == 1:
        return 1
    dp = [0] * (n + 1)
    dp[0], dp[1] = (1, 1)
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]

def make_tree():
    return Node(1, Node(2, Node(4), Node(5)), Node(3))

def password_generator(length=8):
    chars = tuple(ascii_letters) + tuple(digits) + tuple(punctuation)
    return "".join(choice(chars) for x in range(length))

def _subsum(
    digit_pos_to_extract, denominator_addend, precision
):
    sum = 0.0
    for sum_index in range(digit_pos_to_extract + precision):
        denominator = 8 * sum_index + denominator_addend
        exponential_term = 0.0
        if sum_index < digit_pos_to_extract:
            exponential_term = pow(
                16, digit_pos_to_extract - 1 - sum_index, denominator
            )
        else:
            exponential_term = pow(16, digit_pos_to_extract - 1 - sum_index)
        sum += exponential_term / denominator
    return sum

def arithmetic_right_shift(number, shift_amount):
    if number >= 0:  
        binary_number = "0" + str(bin(number)).strip("-")[2:]
    else:  
        binary_number_length = len(bin(number)[3:])  
        binary_number = bin(abs(number) - (1 << binary_number_length))[3:]
        binary_number = (
            ("1" + "0" * (binary_number_length - len(binary_number)) + binary_number)
            if number < 0
            else "0"
        )
    if shift_amount >= len(binary_number):
        return "0b" + binary_number[0] * len(binary_number)
    return (
        "0b"
        + binary_number[0] * shift_amount
        + binary_number[: len(binary_number) - shift_amount]
    )

def main():
    while True:
        print(" Linear Discriminant Analysis ".center(100, "*"))
        print("*" * 100, "\n")
        print("First of all we should specify the number of classes that")
        print("we want to generate as training dataset")
        n_classes = 0
        while True:
            try:
                user_input = int(
                    input("Enter the number of classes (Data Groupings): ").strip()
                )
                if user_input > 0:
                    n_classes = user_input
                    break
                else:
                    print(
                        f"Your entered value is {user_input} , Number of classes "
                        f"should be positive!"
                    )
                    continue
            except ValueError:
                print("Your entered value is not numerical!")
        print("-" * 100)
        std_dev = 1.0  
        while True:
            try:
                user_sd = float(
                    input(
                        "Enter the value of standard deviation"
                        "(Default value is 1.0 for all classes): "
                    ).strip()
                    or "1.0"
                )
                if user_sd >= 0.0:
                    std_dev = user_sd
                    break
                else:
                    print(
                        f"Your entered value is {user_sd}, Standard deviation should "
                        f"not be negative!"
                    )
                    continue
            except ValueError:
                print("Your entered value is not numerical!")
        print("-" * 100)
        counts = []  
        for i in range(n_classes):
            while True:
                try:
                    user_count = int(
                        input(f"Enter The number of instances for class_{i+1}: ")
                    )
                    if user_count > 0:
                        counts.append(user_count)
                        break
                    else:
                        print(
                            f"Your entered value is {user_count}, Number of "
                            f"instances should be positive!"
                        )
                        continue
                except ValueError:
                    print("Your entered value is not numerical!")
        print("-" * 100)
        user_means = []
        for a in range(n_classes):
            while True:
                try:
                    user_mean = float(
                        input(f"Enter the value of mean for class_{a+1}: ")
                    )
                    if isinstance(user_mean, float):
                        user_means.append(user_mean)
                        break
                    print(f"You entered an invalid value: {user_mean}")
                except ValueError:
                    print("Your entered value is not numerical!")
        print("-" * 100)
        print("Standard deviation: ", std_dev)
        for i, count in enumerate(counts, 1):
            print(f"Number of instances in class_{i} is: {count}")
        print("-" * 100)
        for i, user_mean in enumerate(user_means, 1):
            print(f"Mean of class_{i} is: {user_mean}")
        print("-" * 100)
        x = [
            gaussian_distribution(user_means[j], std_dev, counts[j])
            for j in range(n_classes)
        ]
        print("Generated Normal Distribution: \n", x)
        print("-" * 100)
        y = y_generator(n_classes, counts)
        print("Generated Corresponding Ys: \n", y)
        print("-" * 100)
        actual_means = [calculate_mean(counts[k], x[k]) for k in range(n_classes)]
        for i, actual_mean in enumerate(actual_means, 1):
            print(f"Actual(Real) mean of class_{i} is: {actual_mean}")
        print("-" * 100)
        probabilities = (
            calculate_probabilities(counts[i], sum(counts)) for i in range(n_classes)
        )
        for i, probability in enumerate(probabilities, 1):
            print("Probability of class_{} is: {}".format(i, probability))
        print("-" * 100)
        variance = calculate_variance(x, actual_means, sum(counts))
        print("Variance: ", variance)
        print("-" * 100)
        pre_indexes = predict_y_values(x, actual_means, variance, probabilities)
        print("-" * 100)
        print(f"Accuracy: {accuracy(y, pre_indexes)}")
        print("-" * 100)
        print(" DONE ".center(100, "+"))
        if input("Press any key to restart or 'q' for quit: ").strip().lower() == "q":
            print("\n" + "GoodBye!".center(100, "-") + "\n")
            break
        system("cls" if name == "nt" else "clear")

def longestSub(ARRAY): 			
    ARRAY_LENGTH = len(ARRAY)
    if(ARRAY_LENGTH <= 1):  	
        return ARRAY
    PIVOT=ARRAY[0]
    LONGEST_SUB=[]				
    for i in range(1,ARRAY_LENGTH):			
        if (ARRAY[i] < PIVOT):				
            TEMPORARY_ARRAY = [ element for element in ARRAY[i:] if element >= ARRAY[i] ]	
            TEMPORARY_ARRAY = longestSub(TEMPORARY_ARRAY)									
            if ( len(TEMPORARY_ARRAY) > len(LONGEST_SUB) ):									
                LONGEST_SUB = TEMPORARY_ARRAY
    TEMPORARY_ARRAY = [ element for element in ARRAY[1:] if element >= PIVOT ]				
    TEMPORARY_ARRAY = [PIVOT] + longestSub(TEMPORARY_ARRAY)									
    if ( len(TEMPORARY_ARRAY) > len(LONGEST_SUB) ):											
        return TEMPORARY_ARRAY
    else:																					
        return LONGEST_SUB

def _alpha_grid(
    X,
    y,
    Xy=None,
    l1_ratio=1.0,
    fit_intercept=True,
    eps=1e-3,
    n_alphas=100,
    copy_X=True,
):
    if l1_ratio == 0:
        raise ValueError(
            "Automatic alpha grid generation is not supported for"
            " l1_ratio=0. Please supply a grid by providing "
            "your estimator with the appropriate `alphas=` "
            "argument."
        )
    n_samples = len(y)
    sparse_center = False
    if Xy is None:
        X_sparse = sparse.isspmatrix(X)
        sparse_center = X_sparse and fit_intercept
        X = check_array(
            X, accept_sparse="csc", copy=(copy_X and fit_intercept and not X_sparse)
        )
        if not X_sparse:
            X, y, _, _, _ = _preprocess_data(X, y, fit_intercept, copy=False)
        Xy = safe_sparse_dot(X.T, y, dense_output=True)
        if sparse_center:
            _, _, X_offset, _, X_scale = _preprocess_data(X, y, fit_intercept)
            mean_dot = X_offset * np.sum(y)
    if Xy.ndim == 1:
        Xy = Xy[:, np.newaxis]
    if sparse_center:
        if fit_intercept:
            Xy -= mean_dot[:, np.newaxis]
    alpha_max = np.sqrt(np.sum(Xy**2, axis=1)).max() / (n_samples * l1_ratio)
    if alpha_max <= np.finfo(float).resolution:
        alphas = np.empty(n_alphas)
        alphas.fill(np.finfo(float).resolution)
        return alphas
    return np.logspace(np.log10(alpha_max * eps), np.log10(alpha_max), num=n_alphas)[
        ::-1
    ]

def _get_column_indices(X, key):
    n_columns = X.shape[1]
    key_dtype = _determine_key_type(key)
    if isinstance(key, (list, tuple)) and not key:
        return []
    elif key_dtype in ("bool", "int"):
        try:
            idx = _safe_indexing(np.arange(n_columns), key)
        except IndexError as e:
            raise ValueError(
                "all features must be in [0, {}] or [-{}, 0]".format(
                    n_columns - 1, n_columns
                )
            ) from e
        return np.atleast_1d(idx).tolist()
    elif key_dtype == "str":
        try:
            all_columns = X.columns
        except AttributeError:
            raise ValueError(
                "Specifying the columns using strings is only "
                "supported for pandas DataFrames"
            )
        if isinstance(key, str):
            columns = [key]
        elif isinstance(key, slice):
            start, stop = key.start, key.stop
            if start is not None:
                start = all_columns.get_loc(start)
            if stop is not None:
                stop = all_columns.get_loc(stop) + 1
            else:
                stop = n_columns + 1
            return list(range(n_columns)[slice(start, stop)])
        else:
            columns = list(key)
        try:
            column_indices = []
            for col in columns:
                col_idx = all_columns.get_loc(col)
                if not isinstance(col_idx, numbers.Integral):
                    raise ValueError(
                        f"Selected columns, {columns}, are not unique in dataframe"
                    )
                column_indices.append(col_idx)
        except KeyError as e:
            raise ValueError("A given column is not a column of the dataframe") from e
        return column_indices
    else:
        raise ValueError(
            "No valid specification of the columns. Only a "
            "scalar, list or slice of all integers or all "
            "strings, or boolean mask is allowed"
        )

def _assert_all_finite(
    X, allow_nan=False, msg_dtype=None, estimator_name=None, input_name=""
):
    if _get_config()["assume_finite"]:
        return
    X = np.asanyarray(X)
    is_float = X.dtype.kind in "fc"
    if is_float:
        with np.errstate(over="ignore"):
            first_pass_isfinite = np.isfinite(np.sum(X))
        if first_pass_isfinite:
            return
        use_cython = X.data.contiguous and X.dtype.type in {np.float32, np.float64}
        if use_cython:
            out = cy_isfinite(X.reshape(-1), allow_nan=allow_nan)
            has_nan_error = False if allow_nan else out == FiniteStatus.has_nan
            has_inf = out == FiniteStatus.has_infinite
        else:
            has_inf = np.isinf(X).any()
            has_nan_error = False if allow_nan else np.isnan(X).any()
        if has_inf or has_nan_error:
            if has_nan_error:
                type_err = "NaN"
            else:
                msg_dtype = msg_dtype if msg_dtype is not None else X.dtype
                type_err = f"infinity or a value too large for {msg_dtype!r}"
            padded_input_name = input_name + " " if input_name else ""
            msg_err = f"Input {padded_input_name}contains {type_err}."
            if estimator_name and input_name == "X" and has_nan_error:
                msg_err += (
                    f"\n{estimator_name} does not accept missing values"
                    " encoded as NaN natively. For supervised learning, you might want"
                    " to consider sklearn.ensemble.HistGradientBoostingClassifier and"
                    " Regressor which accept missing values encoded as NaNs natively."
                    " Alternatively, it is possible to preprocess the data, for"
                    " instance by using an imputer transformer in a pipeline or drop"
                    " samples with missing values. See"
                    " https://scikit-learn.org/stable/modules/impute.html"
                    " You can find a list of all estimators that handle NaN values"
                    " at the following page:"
                    " https://scikit-learn.org/stable/modules/impute.html"
                    "#estimators-that-handle-nan-values"
                )
            raise ValueError(msg_err)
    elif X.dtype == np.dtype("object") and not allow_nan:
        if _object_dtype_isnan(X).any():
            raise ValueError("Input contains NaN")

def make_s_curve(n_samples=100, *, noise=0.0, random_state=None):
    generator = check_random_state(random_state)
    t = 3 * np.pi * (generator.uniform(size=(1, n_samples)) - 0.5)
    x = np.sin(t)
    y = 2.0 * generator.uniform(size=(1, n_samples))
    z = np.sign(t) * (np.cos(t) - 1)
    X = np.concatenate((x, y, z))
    X += noise * generator.standard_normal(size=(3, n_samples))
    X = X.T
    t = np.squeeze(t)
    return X, t

def _fit(self, X, compute_sources=False):
    X = self._validate_data(X, copy=self.whiten, dtype=FLOAT_DTYPES,
                            ensure_min_samples=2).T
    fun_args = {} if self.fun_args is None else self.fun_args
    random_state = check_random_state(self.random_state)
    alpha = fun_args.get('alpha', 1.0)
    if not 1 <= alpha <= 2:
        raise ValueError('alpha must be in [1,2]')
    if self.fun == 'logcosh':
        g = _logcosh
    elif self.fun == 'exp':
        g = _exp
    elif self.fun == 'cube':
        g = _cube
    elif callable(self.fun):
        def g(x, fun_args):
            return self.fun(x, **fun_args)
    else:
        exc = ValueError if isinstance(self.fun, str) else TypeError
        raise exc(
            "Unknown function %r;"
            " should be one of 'logcosh', 'exp', 'cube' or callable"
            % self.fun
        )
    n_samples, n_features = X.shape
    n_components = self.n_components
    if not self.whiten and n_components is not None:
        n_components = None
        warnings.warn('Ignoring n_components with whiten=False.')
    if n_components is None:
        n_components = min(n_samples, n_features)
    if (n_components > min(n_samples, n_features)):
        n_components = min(n_samples, n_features)
        warnings.warn(
            'n_components is too large: it will be set to %s'
            % n_components
        )
    if self.whiten:
        X_mean = X.mean(axis=-1)
        X -= X_mean[:, np.newaxis]
        u, d, _ = linalg.svd(X, full_matrices=False, check_finite=False)
        del _
        K = (u / d).T[:n_components]  
        del u, d
        X1 = np.dot(K, X)
        X1 *= np.sqrt(n_features)
    else:
        X1 = as_float_array(X, copy=False)  
    w_init = self.w_init
    if w_init is None:
        w_init = np.asarray(random_state.normal(
            size=(n_components, n_components)), dtype=X1.dtype)
    else:
        w_init = np.asarray(w_init)
        if w_init.shape != (n_components, n_components):
            raise ValueError(
                'w_init has invalid shape -- should be %(shape)s'
                % {'shape': (n_components, n_components)})
    kwargs = {'tol': self.tol,
              'g': g,
              'fun_args': fun_args,
              'max_iter': self.max_iter,
              'w_init': w_init}
    if self.algorithm == 'parallel':
        W, n_iter = _ica_par(X1, **kwargs)
    elif self.algorithm == 'deflation':
        W, n_iter = _ica_def(X1, **kwargs)
    else:
        raise ValueError('Invalid algorithm: must be either `parallel` or'
                         ' `deflation`.')
    del X1
    if compute_sources:
        if self.whiten:
            S = np.linalg.multi_dot([W, K, X]).T
        else:
            S = np.dot(W, X).T
    else:
        S = None
    self.n_iter_ = n_iter
    if self.whiten:
        self.components_ = np.dot(W, K)
        self.mean_ = X_mean
        self.whitening_ = K
    else:
        self.components_ = W
    self.mixing_ = linalg.pinv(self.components_, check_finite=False)
    self._unmixing = W
    return S

def cross_validate(estimator, X, y=None, *, groups=None, scoring=None, cv=None,
                   n_jobs=None, verbose=0, fit_params=None,
                   pre_dispatch='2*n_jobs', return_train_score=False,
                   return_estimator=False, error_score=np.nan):
    X, y, groups = indexable(X, y, groups)
    cv = check_cv(cv, y, classifier=is_classifier(estimator))
    scorers, _ = _check_multimetric_scoring(estimator, scoring=scoring)
    parallel = Parallel(n_jobs=n_jobs, verbose=verbose,
                        pre_dispatch=pre_dispatch)
    results = parallel(
        delayed(_fit_and_score)(
            clone(estimator), X, y, scorers, train, test, verbose, None,
            fit_params, return_train_score=return_train_score,
            return_times=True, return_estimator=return_estimator,
            error_score=error_score)
        for train, test in cv.split(X, y, groups))
    results = _aggregate_score_dicts(results)
    if return_estimator:
        fitted_estimators = results["estimator"]
    ret = {}
    ret['fit_time'] = results["fit_time"]
    ret['score_time'] = results["score_time"]
    if return_estimator:
        ret['estimator'] = fitted_estimators
    test_scores = _aggregate_score_dicts(results["test_scores"])
    if return_train_score:
        train_scores = _aggregate_score_dicts(results["train_scores"])
    for name in test_scores:
        ret['test_%s' % name] = test_scores[name]
        if return_train_score:
            key = 'train_%s' % name
            ret[key] = train_scores[name]
    return ret

def _check_sample_weight(sample_weight, X, dtype=None):
    n_samples = _num_samples(X)
    if dtype is not None and dtype not in [np.float32, np.float64]:
        dtype = np.float64
    if sample_weight is None or isinstance(sample_weight, numbers.Number):
        if sample_weight is None:
            sample_weight = np.ones(n_samples, dtype=dtype)
        else:
            sample_weight = np.full(n_samples, sample_weight,
                                    dtype=dtype)
    else:
        if dtype is None:
            dtype = [np.float64, np.float32]
        sample_weight = check_array(
            sample_weight, accept_sparse=False, ensure_2d=False, dtype=dtype,
            order="C"
        )
        if sample_weight.ndim != 1:
            raise ValueError("Sample weights must be 1D array or scalar")
        if sample_weight.shape != (n_samples,):
            raise ValueError("sample_weight.shape == {}, expected {}!"
                             .format(sample_weight.shape, (n_samples,)))
    return sample_weight

def roc_curve(y_true, y_score, pos_label=None, sample_weight=None,
              drop_intermediate=True):
    fps, tps, thresholds = _binary_clf_curve(
        y_true, y_score, pos_label=pos_label, sample_weight=sample_weight)
    if drop_intermediate and len(fps) > 2:
        optimal_idxs = np.where(np.r_[True,
                                      np.logical_or(np.diff(fps, 2),
                                                    np.diff(tps, 2)),
                                      True])[0]
        fps = fps[optimal_idxs]
        tps = tps[optimal_idxs]
        thresholds = thresholds[optimal_idxs]
    if tps.size == 0 or fps[0] != 0 or tps[0] != 0:
        tps = np.r_[0, tps]
        fps = np.r_[0, fps]
        thresholds = np.r_[thresholds[0] + 1, thresholds]
    if fps[-1] <= 0:
        warnings.warn("No negative samples in y_true, "
                      "false positive value should be meaningless",
                      UndefinedMetricWarning)
        fpr = np.repeat(np.nan, fps.shape)
    else:
        fpr = fps / fps[-1]
    if tps[-1] <= 0:
        warnings.warn("No positive samples in y_true, "
                      "true positive value should be meaningless",
                      UndefinedMetricWarning)
        tpr = np.repeat(np.nan, tps.shape)
    else:
        tpr = tps / tps[-1]
    return fpr, tpr, thresholds

def check_classifiers_train(name, Classifier):
    X_m, y_m = make_blobs(n_samples=300, random_state=0)
    X_m, y_m = shuffle(X_m, y_m, random_state=7)
    X_m = StandardScaler().fit_transform(X_m)
    y_b = y_m[y_m != 2]
    X_b = X_m[y_m != 2]
    for (X, y) in [(X_m, y_m), (X_b, y_b)]:
        classes = np.unique(y)
        n_classes = len(classes)
        n_samples, n_features = X.shape
        classifier = Classifier()
        if name in ['BernoulliNB', 'MultinomialNB']:
            X -= X.min()
        set_testing_parameters(classifier)
        set_random_state(classifier)
        assert_raises(ValueError, classifier.fit, X, y[:-1])
        classifier.fit(X, y)
        classifier.fit(X.tolist(), y.tolist())
        assert_true(hasattr(classifier, "classes_"))
        y_pred = classifier.predict(X)
        assert_equal(y_pred.shape, (n_samples,))
        if name not in ['BernoulliNB', 'MultinomialNB']:
            assert_greater(accuracy_score(y, y_pred), 0.83)
        assert_raises(ValueError, classifier.predict, X.T)
        if hasattr(classifier, "decision_function"):
            try:
                decision = classifier.decision_function(X)
                if n_classes is 2:
                    assert_equal(decision.shape, (n_samples,))
                    dec_pred = (decision.ravel() > 0).astype(np.int)
                    assert_array_equal(dec_pred, y_pred)
                if (n_classes is 3 and not isinstance(classifier, BaseLibSVM)):
                    assert_equal(decision.shape, (n_samples, n_classes))
                    assert_array_equal(np.argmax(decision, axis=1), y_pred)
                assert_raises(ValueError,
                              classifier.decision_function, X.T)
                assert_raises(ValueError,
                              classifier.decision_function, X.T)
            except NotImplementedError:
                pass
        if hasattr(classifier, "predict_proba"):
            y_prob = classifier.predict_proba(X)
            assert_equal(y_prob.shape, (n_samples, n_classes))
            assert_array_equal(np.argmax(y_prob, axis=1), y_pred)
            assert_array_almost_equal(np.sum(y_prob, axis=1),
                                      np.ones(n_samples))
            assert_raises(ValueError, classifier.predict_proba, X.T)
            assert_raises(ValueError, classifier.predict_proba, X.T)
            if hasattr(classifier, "predict_log_proba"):
                y_log_prob = classifier.predict_log_proba(X)
                assert_array_almost_equal(y_log_prob, np.log(y_prob), 8)
                assert_array_equal(np.argsort(y_log_prob), np.argsort(y_prob))

def fit(self, X, y):
    X, y = check_X_y(X, y, "csr")
    cv = check_cv(self.cv, y, is_classifier(self.estimator))
    scorer = check_scoring(self.estimator, scoring=self.scoring)
    n_features = X.shape[1]
    n_features_to_select = 1
    rfe = RFE(estimator=self.estimator,
              n_features_to_select=n_features_to_select,
              step=self.step, verbose=self.verbose - 1)
    if self.n_jobs == 1:
        parallel, func = list, _rfe_single_fit
    else:
        parallel, func, = Parallel(n_jobs=self.n_jobs), delayed(_rfe_single_fit)
    scores = parallel(
        func(rfe, self.estimator, X, y, train, test, scorer)
        for train, test in cv.split(X, y))
    scores = np.sum(scores, axis=0)[::-1]
    n_feature_index = np.ceil((n_features - n_features_to_select) /
                              float(self.step))
    n_features_to_select = max(n_features_to_select,
                               n_features - ((n_feature_index -
                                             np.argmax(scores)) *
                                             self.step))
    rfe = RFE(estimator=self.estimator,
              n_features_to_select=n_features_to_select, step=self.step)
    rfe.fit(X, y)
    self.support_ = rfe.support_
    self.n_features_ = rfe.n_features_
    self.ranking_ = rfe.ranking_
    self.estimator_ = clone(self.estimator)
    self.estimator_.fit(self.transform(X), y)
    self.grid_scores_ = scores / cv.get_n_splits(X, y)
    return self

def bincount(x, weights=None, minlength=None):
    x = np.asarray(x, dtype=np.intp)
    if x.size > 0:
        return np.bincount(x, weights, minlength)
    else:
        if minlength is None:
            minlength = 0
        minlength = np.asscalar(np.asarray(minlength, dtype=np.intp))
        return np.zeros(minlength, dtype=np.intp)

def _rescale_data(X, y, sample_weight):
    n_samples = X.shape[0]
    sample_weight = sample_weight * np.ones(n_samples)
    sample_weight = np.sqrt(sample_weight)
    if sparse.issparse(X):
        sw_matrix = sparse.dia_matrix((sample_weight, 0),
                                      shape=(n_samples, n_samples))
        X = safe_sparse_dot(sw_matrix, X)
    else:
        X = X.copy()
        X *= sample_weight[:, np.newaxis]
    y = y.copy()
    y *= sample_weight[:, np.newaxis]
    return X, y

def _lstsq(X, y, indices, fit_intercept):
    fit_intercept = int(fit_intercept)
    n_features = X.shape[1] + fit_intercept
    n_subsamples = indices.shape[1]
    weights = np.empty((indices.shape[0], n_features))
    X_subpopulation = np.ones((n_subsamples, n_features))
    y_subpopulation = np.zeros((max(n_subsamples, n_features)))
    lstsq, = get_lapack_funcs(('gelss',), (X_subpopulation, y_subpopulation))
    for index, subset in enumerate(indices):
        X_subpopulation[:, fit_intercept:] = X[subset, :]
        y_subpopulation[:n_subsamples] = y[subset]
        weights[index, :] = lstsq(X_subpopulation,
                                  y_subpopulation)[1][:n_features]
    return weights

def fit(self, X, y, n_jobs=1):
    if self.n_jobs != 1:
        n_jobs = self.n_jobs
    if n_jobs != 1:
        warnings.warn("The n_jobs parameter has been moved from the fit"
                      " method to the LinearRegression class constructor",
                      DeprecationWarning, stacklevel=2)
        n_jobs_ = n_jobs
    X = check_array(X, accept_sparse=['csr', 'csc', 'coo'])
    y = np.asarray(y)
    X, y, X_mean, y_mean, X_std = self._center_data(
        X, y, self.fit_intercept, self.normalize, self.copy_X)
    if sp.issparse(X):
        if y.ndim < 2:
            out = lsqr(X, y)
            self.coef_ = out[0]
            self.residues_ = out[3]
        else:
            outs = Parallel(n_jobs = n_jobs_)(
                delayed(lsqr)(X, y[:, j].ravel())
                for j in range(y.shape[1]))
            self.coef_ = np.vstack(out[0] for out in outs)
            self.residues_ = np.vstack(out[3] for out in outs)
    else:
        self.coef_, self.residues_, self.rank_, self.singular_ = \
                linalg.lstsq(X, y)
        self.coef_ = self.coef_.T
    if y.ndim == 1:
        self.coef_ = np.ravel(self.coef_)
    self._set_intercept(X_mean, y_mean, X_std)
    return self

def _update_terminal_region(self, tree, terminal_regions, leaf, X, y,
                            residual, pred):
    terminal_region = np.where(terminal_regions == leaf)[0]
    residual = residual.take(terminal_region, axis=0)
    y = y.take(terminal_region, axis=0)
    numerator = residual.sum()
    denominator = np.sum((y - residual) * (1 - y + residual))
    if denominator == 0.0:
        tree.value[leaf, 0, 0] = 0.0
    else:
        tree.value[leaf, 0, 0] = numerator / denominator

def fit(self, X, y):
    if self.strategy not in ("mean", "median", "constant"):
        raise ValueError("Unknown strategy type: %s, expected mean, median or constant"
                         % self.strategy)
    y = safe_asarray(y)
    self.output_2d_ = (y.ndim == 2)
    if self.strategy == "mean":
        self.constant_ = np.reshape(np.mean(y, axis=0), (1, -1))
    elif self.strategy == "median":
        self.constant_ = np.reshape(np.median(y, axis=0), (1, -1))
    elif self.strategy == "constant":
        if self.constant is None:
            raise TypeError("Constant target value has to be specified "
                            "when the constant strategy is used.")
        self.constant = safe_asarray(self.constant)
        if self.output_2d_:
            if self.constant.shape[0] != y.shape[1]:
                raise ValueError(
                    "Constant target value should have "
                    "shape (%d, 1)." % y.shape[1])
        self.constant_ = np.reshape(self.constant, (1, -1))
    self.n_outputs_ = np.size(self.constant_)  
    return self

def _fit_ovo_binary(estimator, X, y, i, j):
    cond = np.logical_or(y == i, y == j)
    y = y[cond]
    if np.dtype.kind != 'i':
        y_binary = np.empty(y.shape, np.int)
    else:
        y_binary = y
    y_binary[y == i] = 0
    y_binary[y == j] = 1
    ind = np.arange(X.shape[0])
    return _fit_binary(estimator, X[ind[cond]], y_binary, classes=[i, j])

def fast_dot(A, B):
    if LooseVersion(np.__version__) < '1.7.2':  
        try:
            linalg.get_blas_funcs(['gemm'])
            try:
                return _fast_dot(A, B)
            except ValueError:
                return np.dot(A, B)
        except (AttributeError, ValueError):
            warnings.warn('Could not import BLAS, falling back to np.dot')
            return np.dot(A, B)
    else:
        return np.dot(A, B)

def f_oneway(*args):
    n_classes = len(args)
    args = [safe_asarray(a) for a in args]
    n_samples_per_class = np.array([a.shape[0] for a in args])
    n_samples = np.sum(n_samples_per_class)
    ss_alldata = reduce(lambda x, y: x + y,
                        [safe_sqr(a).sum(axis=0) for a in args])
    sums_args = [a.sum(axis=0) for a in args]
    square_of_sums_alldata = safe_sqr(reduce(lambda x, y: x + y, sums_args))
    square_of_sums_args = [safe_sqr(s) for s in sums_args]
    sstot = ss_alldata - square_of_sums_alldata / float(n_samples)
    ssbn = 0.
    for k, _ in enumerate(args):
        ssbn += square_of_sums_args[k] / n_samples_per_class[k]
    ssbn -= square_of_sums_alldata / float(n_samples)
    sswn = sstot - ssbn
    dfbn = n_classes - 1
    dfwn = n_samples - n_classes
    msb = ssbn / float(dfbn)
    msw = sswn / float(dfwn)
    f = msb / msw
    f = np.asarray(f).ravel()
    prob = stats.fprob(dfbn, dfwn, f)
    return f, prob

def pairwise_distances_argmin(X, Y=None, axis=1, metric="euclidean",
                              chunk_x_num=None, chunk_y_num=None,
                              return_distances=False, **kwargs):
    dist_func = None
    if metric in PAIRWISE_DISTANCE_FUNCTIONS:
        dist_func = PAIRWISE_DISTANCE_FUNCTIONS[metric]
    elif not callable(metric):
        raise ValueError("'metric' must be string or a callable")
    X, Y = check_pairwise_arrays(X, Y)
    if axis == 0:
        X, Y = Y, X
        chunk_x_num, chunk_y_num = chunk_y_num, chunk_x_num
    if chunk_x_num is None and chunk_y_num is None:
        if X.shape[0] >= Y.shape[0] / 2 and Y.shape[0] >= X.shape[0] / 2:
            chunk_x_num, chunk_y_num = (7, 7)
        elif X.shape[0] > Y.shape[0]:
            chunk_x_num, chunk_y_num = (50, 1)
        else:
            chunk_x_num, chunk_y_num = (1, 50)
    if chunk_x_num is None:
        chunk_x_num = 1
    if chunk_y_num is None:
        chunk_y_num = 1
    indices = np.empty(X.shape[0], dtype='int32')
    values = np.empty(X.shape[0])
    values.fill(np.infty)
    for chunk_x in gen_even_slices(X.shape[0], chunk_x_num):
        X_chunk = X[chunk_x, :]
        for chunk_y in gen_even_slices(Y.shape[0], chunk_y_num):
            Y_chunk = Y[chunk_y, :]
            if dist_func is not None:
                tvar = dist_func(X_chunk, Y_chunk, **kwargs)
            else:
                tvar = np.empty((X_chunk.shape[0], Y_chunk.shape[0]),
                                dtype='float')
                for n_x in range(X_chunk.shape[0]):
                    start = 0
                    if X is Y:
                        start = n_x
                    for n_y in range(start, Y_chunk.shape[0]):
                        tvar[n_x, n_y] = metric(X_chunk[n_x], Y_chunk[n_y],
                                                **kwargs)
                        if X is Y:
                            tvar[n_y, n_x] = tvar[n_x, n_y]
            min_indices = tvar.argmin(axis=1)
            min_values = tvar[range(chunk_x.stop - chunk_x.start), min_indices]
            flags = values[chunk_x] > min_values
            indices[chunk_x] = np.where(
                flags, min_indices + chunk_y.start, indices[chunk_x])
            values[chunk_x] = np.where(
                flags, min_values, values[chunk_x])
    if return_distances:
        return indices, values
    else:
        return indices

def ridge_regression(X, y, alpha, sample_weight=1.0, solver='auto',
                     max_iter=None, tol=1e-3):
    n_samples, n_features = X.shape
    if y.ndim == 2:
        n_samples_, n_targets = y.shape
    elif y.ndim == 1:
        n_samples_ = len(y)
        n_targets = 1
    else:
        raise ValueError("Target y has the wrong shape %s" % str(y.shape))
    if n_samples != n_samples_:
        raise ValueError("Number of samples in X and y does not correspond:"
                         " %d != %d" % (n_samples, n_samples_))
    has_sw = isinstance(sample_weight, np.ndarray) or sample_weight != 1.0
    if solver == 'auto':
        if hasattr(X, '__array__'):
            solver = 'dense_cholesky'
        else:
            solver = 'sparse_cg'
    elif solver == 'lsqr' and not hasattr(sp_linalg, 'lsqr'):
        warnings.warn("""lsqr not available on this machine, falling back
                      to sparse_cg.""")
        solver = 'sparse_cg'
    alpha = safe_asarray(alpha).ravel()
    if alpha.size not in [1, n_targets]:
        raise ValueError("Number of targets and number of penalties "
                    "do not correspond: %d != %d" % (alpha.size, n_targets))
    if has_sw:
        solver = 'dense_cholesky'
    if solver not in ('sparse_cg', 'dense_cholesky', 'svd', 'lsqr'):
        ValueError('Solver %s not understood' % solver)
    if solver == 'sparse_cg':
        X1 = sp_linalg.aslinearoperator(X)
        if y.ndim == 1:
            y1 = np.reshape(y, (-1, 1))
        else:
            y1 = y
        coefs = np.empty((y1.shape[1], n_features))
        if n_features > n_samples:
            def create_mv(curr_alpha):
                def _mv(x):
                    return X1.matvec(X1.rmatvec(x)) + curr_alpha * x
                return _mv
        else:
            def create_mv(curr_alpha):
                def _mv(x):
                    return X1.rmatvec(X1.matvec(x)) + curr_alpha * x
                return _mv
        current_alpha = alpha[0]
        for i in range(y1.shape[1]):
            y_column = y1[:, i]
            if alpha.size > 1:
                current_alpha = alpha[i]
            mv = create_mv(current_alpha)
            if n_features > n_samples:
                C = sp_linalg.LinearOperator(
                    (n_samples, n_samples), matvec=mv, dtype=X.dtype)
                coef, info = sp_linalg.cg(C, y_column, tol=tol)
                coefs[i] = X1.rmatvec(coef)
            else:
                y_column = X1.rmatvec(y_column)
                C = sp_linalg.LinearOperator(
                    (n_features, n_features), matvec=mv, dtype=X.dtype)
                coefs[i], info = sp_linalg.cg(C, y_column, maxiter=max_iter,
                                              tol=tol)
            if info != 0:
                raise ValueError("Failed with error code %d" % info)
        if y.ndim == 1:
            coefs = np.ravel(coefs)
        return coefs
    if solver == "lsqr":
        if y.ndim == 1:
            y1 = np.reshape(y, (-1, 1))
        else:
            y1 = y
        coefs = np.empty((y1.shape[1], n_features))
        sqrt_alpha = np.sqrt(alpha)
        current_sqrt_alpha = sqrt_alpha[0]
        for i in range(y1.shape[1]):
            y_column = y1[:, i]
            if alpha.size > 1:
                current_sqrt_alpha = sqrt_alpha[i]
            coefs[i] = sp_linalg.lsqr(X, y_column, damp=current_sqrt_alpha,
                                      atol=tol, btol=tol, iter_lim=max_iter)[0]
        if y.ndim == 1:
            coefs = np.ravel(coefs)
        return coefs
    if solver == 'dense_cholesky':
        if n_features > n_samples or has_sw:
            K = safe_sparse_dot(X, X.T, dense_output=True)
            if has_sw:
                sw = np.sqrt(sample_weight)
                if y.ndim == 1:
                    y = y * sw
                else:
                    y = y * sw[:, np.newaxis]
                K *= np.outer(sw, sw)
            try:
                if alpha.size == 1:
                    K.flat[::n_samples + 1] += alpha
                    dual_coef = linalg.solve(K, y,
                                         sym_pos=True, overwrite_a=True)
                    if has_sw:
                        if dual_coef.ndim == 1:
                            dual_coef *= sw
                        else:
                            dual_coef *= sw[:, np.newaxis]
                    return safe_sparse_dot(X.T, dual_coef,
                                               dense_output=True).T
                else:
                    coef = np.empty([n_targets, n_features])
                    dual_coefs = np.empty([n_targets, n_samples])
                    for dual_coef, target, current_alpha in zip(
                            dual_coefs, y.T, alpha):
                        K.flat[::n_samples + 1] += current_alpha
                        dual_coef[:] = linalg.solve(K, target, sym_pos=True,
                                                 overwrite_a=False).ravel()
                        K.flat[::n_samples + 1] -= current_alpha
                    if has_sw:
                        dual_coefs *= sw[np.newaxis, :]
                    return safe_sparse_dot(dual_coefs, X, dense_output=True).T
            except linalg.LinAlgError:
                solver = 'svd'
        else:
            A = safe_sparse_dot(X.T, X, dense_output=True)
            Xy = safe_sparse_dot(X.T, y, dense_output=True)
            if alpha.size == 1:
                A.flat[::n_features + 1] += alpha
                try:
                    return linalg.solve(A, Xy, sym_pos=True,
                                        overwrite_a=True).T
                except linalg.LinAlgError:
                    solver = 'svd'
            else:
                coefs = np.empty([n_targets, n_features])
                for coef, target, current_alpha in zip(
                        coefs, Xy.T, alpha):
                    A.flat[::n_features + 1] += current_alpha
                    coef[:] = linalg.solve(A, target, sym_pos=True,
                                           overwrite_a=False).ravel()
                    A.flat[::n_features + 1] -= current_alpha
            return coefs
    if solver == 'svd':
        alpha_dim = alpha.ndim
        if y.ndim == 1:
            y1 = y[:, np.newaxis]
        else:
            y1 = y
        if alpha_dim == 1 and len(alpha) != n_targets:
            alpha = alpha[:, np.newaxis]
        alpha = np.atleast_2d(alpha)
        assert alpha.ndim == 2
        U, s, Vt = linalg.svd(X, full_matrices=False)
        idx = s > 1e-15  
        UTy = U.T.dot(y1)
        s[idx == False] = 0.
        d = (s[np.newaxis, :, np.newaxis] /
             (s[np.newaxis, :, np.newaxis] ** 2 + alpha[:, np.newaxis, :]))
        d_UT_y = d * UTy[np.newaxis, :, :]
        coef_ = np.empty([alpha.shape[0], n_targets, n_features])
        for dUTy, coef_slice in zip(d_UT_y, coef_):
            coef_slice[:] = Vt.T.dot(dUTy).T
        if (alpha_dim == 0) or (alpha_dim == 1 and alpha.size == n_targets):
            coef_ = coef_.reshape(n_targets, n_features)
            if y.ndim == 1:
                coef_ = coef_.ravel()
        else:
            if y.ndim == 1:
                coef_ = coef_.squeeze()
        return coef_

def fit(self, X, y):
    X, y = check_arrays(X, y, sparse_format="csr")
    rfe = RFE(estimator=self.estimator, n_features_to_select=1,
              step=self.step, estimator_params=self.estimator_params,
              verbose=self.verbose - 1)
    cv = check_cv(self.cv, X, y, is_classifier(self.estimator))
    scores = np.zeros(X.shape[1])
    n = 0
    for train, test in cv:
        ranking_ = rfe.fit(X[train], y[train]).ranking_
        for k in range(0, max(ranking_)):
            mask = np.where(ranking_ <= k + 1)[0]
            estimator = clone(self.estimator)
            estimator.fit(X[train][:, mask], y[train])
            if self.loss_func is None:
                loss_k = 1.0 - estimator.score(X[test][:, mask], y[test])
            else:
                loss_k = self.loss_func(
                    y[test], estimator.predict(X[test][:, mask]))
            if self.verbose > 0:
                print("Finished fold with %d / %d feature ranks, loss=%f"
                      % (k, max(ranking_), loss_k))
            scores[k] += loss_k
        n += 1
    best_score = np.inf
    best_k = None
    for k, score in enumerate(scores):
        if score < best_score:
            best_score = score
            best_k = k + 1
    rfe = RFE(estimator=self.estimator,
              n_features_to_select=best_k,
              step=self.step, estimator_params=self.estimator_params)
    rfe.fit(X, y)
    self.support_ = rfe.support_
    self.n_features_ = rfe.n_features_
    self.ranking_ = rfe.ranking_
    self.estimator_ = clone(self.estimator)
    self.estimator_.set_params(**self.estimator_params)
    self.estimator_.fit(self.transform(X), y)
    self.cv_scores_ = scores / n
    return self

def unique_labels(*lists_of_labels):
    labels = set()
    for l in lists_of_labels:
        if hasattr(l, 'ravel'):
            l = l.ravel()
        labels |= set(l)
    return np.unique(sorted(labels))

def make_circles(n_samples=100, shuffle=True, noise=None, random_state=None,
        factor=.8):
    if factor > 1 or factor < 0:
        raise ValueError("'factor' has to be between 0 and 1.")
    n_samples_out = int(n_samples / float(1 + factor))
    n_samples_in = n_samples - n_samples_out
    generator = check_random_state(random_state)
    n_samples_out, n_samples_in = n_samples_out + 1, n_samples_in + 1
    outer_circ_x = np.cos(np.linspace(0, 2 * np.pi, n_samples_out)[:-1])
    outer_circ_y = np.sin(np.linspace(0, 2 * np.pi, n_samples_out)[:-1])
    inner_circ_x = (np.cos(np.linspace(0, 2 * np.pi, n_samples_in)[:-1])
                    * factor)
    inner_circ_y = (np.sin(np.linspace(0, 2 * np.pi, n_samples_in)[:-1])
                    * factor)
    X = np.vstack((np.append(outer_circ_x, inner_circ_x),\
           np.append(outer_circ_y, inner_circ_y))).T
    y = np.hstack([np.zeros(n_samples_out - 1), np.ones(n_samples_in - 1)])
    if shuffle:
        X, y = util_shuffle(X, y, random_state=generator)
    if not noise is None:
        X += generator.normal(scale=noise, size=X.shape)
    return X, y.astype(np.int)

def __iter__(self):
    rng = check_random_state(self.random_state)
    cls_count = np.bincount(np.unique(self.y, return_inverse=True)[1])
    p_i = cls_count / float(self.n)
    n_i = np.round(self.n_train * p_i).astype('int')
    t_i = np.array([cls_count - n_i,
                    np.round(self.n_test * p_i).astype('int')]).min(axis=0)
    for n in range(self.n_iterations):
        train = []
        test = []
        for i, cls in enumerate(np.unique(self.y)):
            permutation = rng.permutation(n_i[i] + t_i[i])
            cls_i = np.where((self.y == cls))[0][permutation]
            train.extend(cls_i[:n_i[i]])
            test.extend(cls_i[n_i[i]:n_i[i] + t_i[i]])
        train = np.array(train)[rng.permutation(len(train))]
        test = np.array(test)[rng.permutation(len(test))]
        if self.indices:
            yield train, test
        else:
            train_m = np.zeros(self.n, dtype='bool')
            test_m = np.zeros(self.n, dtype='bool')
            train_m[train] = True
            test_m[test] = True
            yield train_m, test_m

def transform(self, y):
    self._check_fitted()
    classes = np.unique(y)
    if len(np.intersect1d(classes, self.classes_)) < len(classes):
        diff = np.setdiff1d(classes, self.classes_)
        raise ValueError("y contains new labels: %s" % str(diff))
    y = np.asarray(y)
    y_new = np.zeros(len(y), dtype=int)
    for i, k in enumerate(self.classes_[1:]):
        y_new[y == k] = i + 1
    return y_new

def load_svmlight_file(f, n_features=None, dtype=np.float64,
                       multilabel=False, zero_based="auto"):
    if hasattr(f, "read"):
        data, indices, indptr, y = _load_svmlight_file(f, dtype, multilabel,
                                                       bool(zero_based))
    else:
        with open(f, 'rb') as f:
            data, indices, indptr, y = _load_svmlight_file(f, dtype,
                                                           multilabel,
                                                           bool(zero_based))
    if zero_based is False or zero_based == "auto" and np.min(indices) > 0:
        indices -= 1
    if n_features is not None:
        shape = (indptr.shape[0] - 1, n_features)
    else:
        shape = None
    X = sp.csr_matrix((data, indices, indptr), shape)
    return X, y

def roc_curve(y_true, y_score):
    y_true = y_true.ravel()
    classes = np.unique(y_true)
    if classes.shape[0] != 2:
        raise ValueError("ROC is defined for binary classification only")
    y_score = y_score.ravel()
    thresholds = np.sort(np.unique(y_score))[::-1]
    n_thresholds = thresholds.size
    tpr = np.empty(n_thresholds)  
    fpr = np.empty(n_thresholds)  
    n_pos = float(np.sum(y_true == classes[1]))  
    n_neg = float(np.sum(y_true == classes[0]))  
    for i, t in enumerate(thresholds):
        tpr[i] = np.sum(y_true[y_score >= t] == classes[1]) / n_pos
        fpr[i] = np.sum(y_true[y_score >= t] == classes[0]) / n_neg
    if fpr.shape[0] == 2:
        fpr = np.array([0.0, fpr[0], fpr[1]])
        tpr = np.array([0.0, tpr[0], tpr[1]])
    elif fpr.shape[0] == 1:
        fpr = np.array([0.0, fpr[0], 1.0])
        tpr = np.array([0.0, tpr[0], 1.0])
    return fpr, tpr, thresholds

def fit(self, X, y=None):
    n_samples, n_features = X.shape
    if self.use_idf:
        idc = np.zeros(n_features, dtype=np.float64)
        for doc, token in zip(*X.nonzero()):
            idc[token] += 1
        self.idf_ = np.log(float(X.shape[0]) / idc)
    return self

def euclidean_distances(X, Y, Y_norm_squared=None, squared=False):
    if X is Y:
        X = Y = safe_asanyarray(X)
    else:
        X = safe_asanyarray(X)
        Y = safe_asanyarray(Y)
    if X.shape[1] != Y.shape[1]:
        raise ValueError("Incompatible dimension for X and Y matrices")
    if issparse(X):
        XX = X.multiply(X).sum(axis=1)
    else:
        XX = np.sum(X * X, axis=1)[:, np.newaxis]
    if X is Y:  
        YY = XX.T
    elif Y_norm_squared is None:
        if issparse(Y):
            YY = Y.copy() if isinstance(Y, csr_matrix) else Y.tocsr()
            YY.data **= 2
            YY = np.asarray(YY.sum(axis=1)).T
        else:
            YY = np.sum(Y ** 2, axis=1)[np.newaxis, :]
    else:
        YY = atleast2d_or_csr(Y_norm_squared)
        if YY.shape != (1, Y.shape[0]):
            raise ValueError(
                        "Incompatible dimensions for Y and Y_norm_squared")
    distances = XX + YY  
    distances -= 2 * safe_sparse_dot(X, Y.T)
    distances = np.maximum(distances, 0)
    return distances if squared else np.sqrt(distances)

def load(dataset):
    import csv
    import os
    DESCR = ''
    firis = csv.reader(open(os.path.dirname(__file__) + '/data/%s.csv' % dataset))
    fdescr = open(os.path.dirname(__file__) + '/descr/%s.rst' % dataset)
    temp = firis.next()
    nsamples = int(temp[0])
    nfeat = int(temp[1])
    labelnames = temp[2:]
    data = np.empty((nsamples, nfeat))
    label = np.empty((nsamples,))
    for i, ir in enumerate(firis):
        data[i] = np.asanyarray(ir[:-1], dtype=np.float)
        label[i] = np.asanyarray(ir[-1], dtype=np.int)
    return Bunch(data = data, label=label, labelnames=labelnames, DESCR=fdescr.read())

def _get_slot(self, request, spider):
    key = self._get_slot_key(request, spider)
    if key not in self.slots:
        conc = self.per_slot_settings.get(key, {}).get(
            'concurrency', self.ip_concurrency if self.ip_concurrency else self.domain_concurrency
        )
        conc, delay = _get_concurrency_delay(conc, spider, self.settings)
        delay = self.per_slot_settings.get(key, {}).get('delay', delay)
        randomize_delay = self.per_slot_settings.get(key, {}).get('randomize_delay', self.randomize_delay)
        new_slot = Slot(conc, delay, randomize_delay)
        self.slots[key] = new_slot
    return key, self.slots[key]

def url_has_any_extension(url, extensions):
    return any(parse_url(url).path.lower().endswith(ext) for ext in extensions)

def __init__(self, spidercls, settings=None, init_reactor = False):
    if isinstance(spidercls, Spider):
        raise ValueError('The spidercls argument must be a class, not an object')
    if isinstance(settings, dict) or settings is None:
        settings = Settings(settings)
    self.spidercls = spidercls
    self.settings = settings.copy()
    self.spidercls.update_settings(self.settings)
    self.signals = SignalManager(self)
    self.stats = load_object(self.settings['STATS_CLASS'])(self)
    handler = LogCounterHandler(self, level=self.settings.get('LOG_LEVEL'))
    logging.root.addHandler(handler)
    d = dict(overridden_settings(self.settings))
    logger.info("Overridden settings:\n%(settings)s",
                {'settings': pprint.pformat(d)})
    if get_scrapy_root_handler() is not None:
        install_scrapy_root_handler(self.settings)
    self.__remove_handler = lambda: logging.root.removeHandler(handler)
    self.signals.connect(self.__remove_handler, signals.engine_stopped)
    lf_cls = load_object(self.settings['LOG_FORMATTER'])
    self.logformatter = lf_cls.from_crawler(self)
    if init_reactor:
        if self.settings.get("TWISTED_REACTOR"):
            install_reactor(self.settings["TWISTED_REACTOR"], self.settings["ASYNCIO_EVENT_LOOP"])
        else:
            from twisted.internet import default
            default.install()
        log_reactor_info()
    if self.settings.get("TWISTED_REACTOR"):
        verify_installed_reactor(self.settings["TWISTED_REACTOR"])
    self.extensions = ExtensionManager.from_crawler(self)
    self.settings.freeze()
    self.crawling = False
    self.spider = None
    self.engine = None

def handshakeCompleted(self):
    negotiated_protocol = self.transport.negotiatedProtocol
    if isinstance(negotiated_protocol, bytes):
        negotiated_protocol = str(self.transport.negotiatedProtocol, 'utf-8')
    if negotiated_protocol != 'h2':
        self._lose_connection_with_error([InvalidNegotiatedProtocol(negotiated_protocol)])

def _identityVerifyingInfoCallback(self, connection, where, ret):
    if where & SSL.SSL_CB_HANDSHAKE_START:
        set_tlsext_host_name(connection, self._hostnameBytes)
    elif where & SSL.SSL_CB_HANDSHAKE_DONE:
        if self.verbose_logging:
            if hasattr(connection, 'get_cipher_name'):  
                if hasattr(connection, 'get_protocol_version_name'):  
                    logger.debug('SSL connection to %s using protocol %s, cipher %s',
                                 self._hostnameASCII,
                                 connection.get_protocol_version_name(),
                                 connection.get_cipher_name(),
                                 )
                else:
                    logger.debug('SSL connection to %s using cipher %s',
                                 self._hostnameASCII,
                                 connection.get_cipher_name(),
                                 )
            server_cert = connection.get_peer_certificate()
            logger.debug('SSL connection certificate: issuer "%s", subject "%s"',
                         x509name_to_string(server_cert.get_issuer()),
                         x509name_to_string(server_cert.get_subject()),
                         )
            key_info = get_temp_key_info(connection._ssl)
            if key_info:
                logger.debug('SSL temp key: %s', key_info)
        try:
            verifyHostname(connection, self._hostnameASCII)
        except (CertificateError, VerificationError) as e:
            logger.warning(
                'Remote certificate is not valid for hostname "{}"; {}'.format(
                    self._hostnameASCII, e))
        except ValueError as e:
            logger.warning(
                'Ignoring error while verifying certificate '
                'from host "{}" (exception: {})'.format(
                    self._hostnameASCII, repr(e)))

def scrape_response(self, scrape_func, response, request, spider):
    def process_spider_input(response):
        for method in self.methods['process_spider_input']:
            try:
                result = method(response=response, spider=spider)
                if result is not None:
                    msg = "Middleware {} must return None or raise an exception, got {}"
                    raise _InvalidOutput(msg.format(_fname(method), type(result)))
            except _InvalidOutput:
                raise
            except Exception:
                return scrape_func(Failure(), request, spider)
        return scrape_func(response, request, spider)
    def _evaluate_iterable(iterable, method_index, recover_to):
        try:
            for r in iterable:
                yield r
        except Exception as ex:
            exception_result = process_spider_exception(Failure(ex), method_index)
            if isinstance(exception_result, Failure):
                raise
            recover_to.extend(exception_result)
    def process_spider_exception(_failure, start_index=0):
        exception = _failure.value
        if isinstance(exception, _InvalidOutput):
            return _failure
        method_list = islice(self.methods['process_spider_exception'], start_index, None)
        for method_index, method in enumerate(method_list, start=start_index):
            if method is None:
                continue
            result = method(response=response, exception=exception, spider=spider)
            if _isiterable(result):
                return process_spider_output(result, method_index+1)
            elif result is None:
                continue
            else:
                msg = "Middleware {} must return None or an iterable, got {}"
                raise _InvalidOutput(msg.format(_fname(method), type(result)))
        return _failure
    def process_spider_output(result, start_index=0):
        recovered = MutableChain()
        method_list = islice(self.methods['process_spider_output'], start_index, None)
        for method_index, method in enumerate(method_list, start=start_index):
            if method is None:
                continue
            try:
                result = method(response=response, result=result, spider=spider)
            except Exception as ex:
                exception_result = process_spider_exception(Failure(ex), method_index+1)
                if isinstance(exception_result, Failure):
                    raise
                return exception_result
            else:
                if _isiterable(result):
                    result = _evaluate_iterable(result, method_index+1, recovered)
                else:
                    msg = "Middleware {} must return an iterable, got {}"
                    raise _InvalidOutput(msg.format(_fname(method), type(result)))
        return MutableChain(result, recovered)
    def process_callback_output(result):
        if isinstance(result, Failure):
            return process_spider_exception(result)
        recovered = MutableChain()
        result = _evaluate_iterable(result, 0, recovered)
        return MutableChain(process_spider_output(result), recovered)
    dfd = mustbe_deferred(process_spider_input, response)
    dfd.addCallbacks(callback=process_callback_output, errback=process_callback_output)
    return dfd

def follow_all(self, urls=None, callback=None, method='GET', headers=None, body=None,
               cookies=None, meta=None, encoding=None, priority=0,
               dont_filter=False, errback=None, cb_kwargs=None,
               css=None, xpath=None):
    arg_count = len(list(filter(None, (urls, css, xpath))))
    if arg_count != 1:
        raise ValueError('Please supply exactly one of the following arguments: urls, css, xpath')
    if not urls:
        urls = []
        if css:
            selector_method = getattr(self, 'css')
            expression = css
        elif xpath:
            selector_method = getattr(self, 'xpath')
            expression = xpath
        for selector in selector_method(expression):
            try:
                urls.append(_url_from_selector(selector))
            except ValueError:
                pass
    return (
        self.follow(
            url=url,
            callback=callback,
            method=method,
            headers=headers,
            body=body,
            cookies=cookies,
            meta=meta,
            encoding=encoding,
            priority=priority,
            dont_filter=dont_filter,
            errback=errback,
            cb_kwargs=cb_kwargs,
        )
        for url in urls
    )

def download_request(self, request):
    timeout = request.meta.get('download_timeout') or self._connectTimeout
    agent = self._get_agent(request, timeout)
    url = urldefrag(request.url)[0]
    method = to_bytes(request.method)
    headers = TxHeaders(request.headers)
    if isinstance(agent, self._TunnelingAgent):
        headers.removeHeader(b'Proxy-Authorization')
    if request.body:
        bodyproducer = _RequestBodyProducer(request.body)
    else:
        bodyproducer = _RequestBodyProducer(b'') if method == b'POST' else None
    start_time = time()
    d = agent.request(
        method, to_bytes(url, encoding='ascii'), headers, bodyproducer)
    d.addCallback(self._cb_latency, request, start_time)
    d.addCallback(self._cb_bodyready, request)
    d.addCallback(self._cb_bodydone, request, url)
    self._timeout_cl = reactor.callLater(timeout, d.cancel)
    d.addBoth(self._cb_timeout, request, url, timeout)
    return d

def _retry(self, request, reason, spider):
    retries = request.meta.get('retry_times', 0) + 1
    retry_times = self.max_retry_times
    if 'max_retry_times' in request.meta:
        retry_times = request.meta['max_retry_times']
    stats = spider.crawler.stats
    if retries <= retry_times:
        logger.debug("Retrying %(request)s (failed %(retries)d times): %(reason)s",
                     {'request': request, 'retries': retries, 'reason': reason},
                     extra={'spider': spider})
        retryreq = request.copy()
        retryreq.meta['retry_times'] = retries
        retryreq.dont_filter = True
        retryreq.priority = request.priority + self.priority_adjust
        if isinstance(reason, Exception):
            reason = global_object_name(reason.__class__)
        stats.inc_value('retry/count')
        stats.inc_value('retry/reason_count/%s' % reason)
        return retryreq
    else:
        stats.inc_value('retry/max_reached')
        logger.debug("Gave up retrying %(request)s (failed %(retries)d times): %(reason)s",
                     {'request': request, 'retries': retries, 'reason': reason},
                     extra={'spider': spider})

def tunnel_request_data(host, port, proxy_auth_header=None, host_header=True):
    host_value = to_bytes(host, encoding='ascii') + b':' + to_bytes(str(port))
    tunnel_req = b'CONNECT ' + host_value + b' HTTP/1.1\r\n'
    if host_header:
        tunnel_req += b'Host: ' + host_value + b'\r\n'
    if proxy_auth_header:
        tunnel_req += b'Proxy-Authorization: ' + proxy_auth_header + b'\r\n'
    tunnel_req += b'\r\n'
    return tunnel_req

def requestTunnel(self, protocol):
    tunnelReq = to_bytes(
        'CONNECT %s:%s HTTP/1.1\r\n' % (
            self._tunneledHost, self._tunneledPort), encoding='ascii')
    if self._proxyAuthHeader:
        tunnelReq += \
                b'Proxy-Authorization: ' + self._proxyAuthHeader + b'\r\n'
    tunnelReq += b'\r\n'
    protocol.transport.write(tunnelReq)
    self._protocolDataReceived = protocol.dataReceived
    protocol.dataReceived = self.processProxyResponse
    self._protocol = protocol
    return protocol

def requestTunnel(self, protocol):
    tunnelReq = (
        b'CONNECT ' +
        to_bytes(self._tunneledHost, encoding='ascii') + b':' +
        to_bytes(str(self._tunneledPort)) +
        b' HTTP/1.1\r\n')
    if self._proxyAuthHeader:
        tunnelReq += \
                b'Proxy-Authorization: ' + self._proxyAuthHeader + b'\r\n'
    tunnelReq += b'\r\n'
    protocol.transport.write(tunnelReq)
    self._protocolDataReceived = protocol.dataReceived
    protocol.dataReceived = self.processProxyResponse
    self._protocol = protocol
    return protocol

def process_response(self, request, response, spider):
    if (request.meta.get('dont_redirect', False) or
            response.status in getattr(spider, 'handle_httpstatus_list', []) or
            response.status in request.meta.get('handle_httpstatus_list', []) or
            request.meta.get('handle_httpstatus_all', False)):
        return response
    location = None
    if 'Location' in response.headers:
        location = to_native_str(response.headers['location'].decode('latin1'))
    if location is not None and response.status in [301, 302, 303, 307]:
        redirected_url = urljoin(request.url, location)
        if response.status in [301, 307] or request.method == 'HEAD':
            redirected = request.replace(url=redirected_url)
            return self._redirect(redirected, request, spider, response.status)
        if response.status in [302, 303]:
            redirected = self._redirect_request_using_get(request, redirected_url)
            return self._redirect(redirected, request, spider, response.status)
    return response

def process_response(self, request, response, spider):
    if (request.meta.get('dont_redirect', False) or
           response.status in getattr(spider, 'handle_httpstatus_list', []) or
           response.status in request.meta.get('handle_httpstatus_list', []) or
           request.meta.get('handle_httpstatus_all', False)):
        return response
    if request.method == 'HEAD':
        if response.status in [301, 302, 303, 307] and 'Location' in response.headers:
            redirected_url = urljoin(request.url, response.headers['location'])
            redirected = request.replace(url=redirected_url)
            return self._redirect(redirected, request, spider, response.status)
        else:
            return response
    if response.status in [302, 303] and 'Location' in response.headers:
        redirected_url = urljoin(request.url, response.headers['location'])
        redirected = self._redirect_request_using_get(request, redirected_url)
        return self._redirect(redirected, request, spider, response.status)
    if response.status in [301, 307] and 'Location' in response.headers:
        redirected_url = urljoin(request.url, response.headers['location'])
        redirected = request.replace(url=redirected_url)
        return self._redirect(redirected, request, spider, response.status)
    return response

def extract_first(self):
    for x in self.extract():
        return x

def add_options(self, parser):
    group = OptionGroup(parser, "Global Options")
    group.add_option("--logfile", dest="logfile", metavar="FILE", \
            help="log file. if omitted stderr will be used")
    group.add_option("-L", "--loglevel", dest="loglevel", metavar="LEVEL", \
            default=None, \
            help="log level (default: %s)" % settings['LOGLEVEL'])
    group.add_option("--nolog", action="store_true", dest="nolog", \
            help="disable logging completely")
    group.add_option("--profile", dest="profile", metavar="FILE", default=None, \
            help="write python cProfile stats to FILE")
    group.add_option("--lsprof", dest="lsprof", metavar="FILE", default=None, \
            help="write lsprof profiling stats to FILE")
    group.add_option("--pidfile", dest="pidfile", metavar="FILE", \
            help="write process ID to FILE")
    group.add_option("-s", "--set", dest="set", action="append", default=[], metavar="NAME=VALUE", \
            help="set/override setting (may be repeated)")
    parser.add_option_group(group)

def chain_deferred(d1, d2):
    if callable(d2):
        d2 = lambda_deferred(d2)
    def _pause(_):
        d2.pause()
        reactor.callLater(0, d2.unpause)
        return _
    def _reclaim(_):
        return d2
    d1.chainDeferred(d2)
    d1.addBoth(_reclaim)
    return d1
