def log_error(msg, *args, **kwargs):
    msg , level  = msg % args, kwargs.get('level', 'error')
    assert level in ['error', 'warning']
    env.stderr.write('\nhttp: %s: %s\n' % (level, msg))
