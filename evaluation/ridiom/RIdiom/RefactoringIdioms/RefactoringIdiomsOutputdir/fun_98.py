def _run(self, cmd, **kwargs):
    call , input_ , env , stderr  = kwargs.pop('call', False), kwargs.pop('input_', None), kwargs.pop('env', dict(os.environ)), kwargs.pop('stderr', subprocess.STDOUT)
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
