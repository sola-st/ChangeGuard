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
    for attr_name in ("create_app", "make_app"):
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
