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
                env=env,
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
