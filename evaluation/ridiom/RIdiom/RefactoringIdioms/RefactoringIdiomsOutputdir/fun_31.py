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
        env.log_error(f'{session_name!r} @ {hostname!r} does not exist.')
        return ExitStatus.ERROR
    fixers = [
        fixer
        for version, fixer in FIXERS_TO_VERSIONS.items()
        if is_version_greater(version, session.version)
    ]
    if not len(fixers):
        env.stdout.write(f'{session_name!r} @ {hostname!r} is already up to date.\n')
        return ExitStatus.SUCCESS
    for fixer in fixers:
        fixer(session, hostname, args)
    session.save(bump_version=True)
    env.stdout.write(f'Upgraded {session_name!r} @ {hostname!r} to v{session.version}\n')
    return ExitStatus.SUCCESS
