def log_error(msg, *args, **kwargs):
    msg = msg % args
    level = kwargs.get('level', 'error')
    assert level in ['error', 'warning']
    env.stderr.write('\nhttp: %s: %s\n' % (level, msg))
