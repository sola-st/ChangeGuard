def wrapper(*args, **kwargs):
    old_arg_value = kwargs.pop(old_arg_name, None)
    if old_arg_value is not None:
        if new_arg_name is None:
            msg = (
                f"the {repr(old_arg_name)} keyword is deprecated and "
                "will be removed in a future version. Please take "
                f"steps to stop the use of {repr(old_arg_name)}"
            )
            warnings.warn(msg, FutureWarning, stacklevel=stacklevel)
            kwargs[old_arg_name] = old_arg_value
            return func(*args, **kwargs)
        elif mapping is not None:
            if callable(mapping):
                new_arg_value = mapping(old_arg_value)
            else:
                new_arg_value = mapping.get(old_arg_value, old_arg_value)
            msg = (
                f"the {old_arg_name}={repr(old_arg_value)} keyword is "
                "deprecated, use "
                f"{new_arg_name}={repr(new_arg_value)} instead."
            )
        else:
            new_arg_value = old_arg_value
            msg = (
                f"the {repr(old_arg_name)} keyword is deprecated, "
                f"use {repr(new_arg_name)} instead."
            )
        warnings.warn(msg, FutureWarning, stacklevel=stacklevel)
        if kwargs.get(new_arg_name) is not None:
            msg = (
                f"Can only specify {repr(old_arg_name)} "
                f"or {repr(new_arg_name)}, not both."
            )
            raise TypeError(msg)
        kwargs[new_arg_name] = new_arg_value
    return func(*args, **kwargs)
