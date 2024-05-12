def find_best_app(module):
    from . import Flask
    for attr_name in 'app', 'application':
        app = getattr(module, attr_name, None)
        if isinstance(app, Flask):
            return app
    matches = [v for k, v in iteritems(module.__dict__)
               if isinstance(v, Flask)]
    if len(matches) == 1:
        return matches[0]
    for attr_name in 'create_app', 'make_app':
        app_factory = getattr(module, attr_name, None)
        if callable(app_factory):
            try:
                app = app_factory()
                if isinstance(app, Flask):
                    return app
            except TypeError:
                raise NoAppException(
                    'Auto-detected "{callable}()" in module "{module}", but '
                    'could not call it without specifying arguments.'
                    .format(callable=attr_name,
                            module=module.__name__))
    raise NoAppException(
        'Failed to find application in module "{module}".  Are you sure '
        'it contains a Flask application?  Maybe you wrapped it in a WSGI '
        'middleware or you are using a factory function.'
        .format(module=module.__name__))
