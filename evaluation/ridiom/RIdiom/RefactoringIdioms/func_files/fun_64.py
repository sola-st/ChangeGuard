def run_async(func):
    try:
        from asgiref.sync import async_to_sync
    except ImportError:
        raise RuntimeError(
            "Install Flask with the 'async' extra in order to use async views."
        )
    if ContextVar.__module__ == "werkzeug.local":
        raise RuntimeError(
            "Async cannot be used with this combination of Python & Greenlet versions."
        )
    def wrapper(*args, **kwargs):
        return async_to_sync(func)(*args, **kwargs)
    wrapper._flask_sync_wrapper = True  
    return wrapper
