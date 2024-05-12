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
        stdout , error  = StringIO(), None
        try:
            with redirect_stdout(stdout):
                dist_format = "wheel" if not editable else "editable"
                env.install(
                    builder.build_system_requires
                    | builder.get_requires_for_build(dist_format)
                )
                path = Path(
                    builder.build(
                        dist_format,
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
