def locate_app(script_info, app_id, raise_if_not_found=True):
    __traceback_hide__ = True
    if ':' in app_id:
        module, app_obj = app_id.split(':', 1)
    else:
        module , app_obj  = app_id, None
    try:
        __import__(module)
    except ImportError:
        if sys.exc_info()[-1].tb_next:
            stack_trace = traceback.format_exc()
            raise NoAppException(
                'There was an error trying to import the app ({module}):\n'
                '{stack_trace}'.format(
                    module=module, stack_trace=stack_trace
                )
            )
        elif raise_if_not_found:
            raise NoAppException(
                'The file/path provided ({module}) does not appear to exist.'
                ' Please verify the path is correct. If app is not on'
                ' PYTHONPATH, ensure the extension is .py.'.format(
                    module=module)
            )
        else:
            return
    mod = sys.modules[module]
    if app_obj is None:
        return find_best_app(script_info, mod)
    else:
        return find_app_by_string(app_obj, script_info, mod)
