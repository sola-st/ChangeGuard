def call_factory(app_factory, script_info, arguments=()):
    args_spec = getargspec(app_factory)
    arg_names = args_spec.args
    arg_defaults = args_spec.defaults
    if 'script_info' in arg_names:
        return app_factory(*arguments, script_info=script_info)
    elif arguments:
        return app_factory(*arguments)
    elif not arguments and len(arg_names) == 1 and arg_defaults is None:
        return app_factory(script_info)
    return app_factory()
