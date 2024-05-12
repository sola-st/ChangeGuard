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
    pool , repo  = Pool(ignore_repository_names=True), Repository()
    for package in local_repo.packages + locked_repository.packages:
        if not repo.has_package(package):
            repo.add_package(package)
    pool.add_repository(repo)
    whitelist = [pkg.name for pkg in locked_repository.packages]
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
        installs , updates , uninstalls , skipped  = 0, 0, 0, 0
        for op in ops:
            if op.skipped:
                skipped += 1
            elif op.job_type == "install":
                installs += 1
            elif op.job_type == "update":
                updates += 1
            elif op.job_type == "uninstall":
                uninstalls += 1
        self._io.write_line("")
        self._io.write_line(
            "Package operations: "
            "<info>{}</> install{}, "
            "<info>{}</> update{}, "
            "<info>{}</> removal{}"
            "{}".format(
                installs,
                "" if installs == 1 else "s",
                updates,
                "" if updates == 1 else "s",
                uninstalls,
                "" if uninstalls == 1 else "s",
                ", <info>{}</> skipped".format(skipped)
                if skipped and self.is_verbose()
                else "",
            )
        )
    self._io.write_line("")
    for op in ops:
        self._execute(op)
