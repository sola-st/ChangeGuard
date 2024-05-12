def aggregate(obj, arg, *args, **kwargs):
    is_aggregator , _axis  = lambda x: isinstance(x, (list, tuple, dict)), kwargs.pop('_axis', None)
    if _axis is None:
        _axis = getattr(obj, "axis", 0)
    if isinstance(arg, str):
        return obj._try_aggregate_string_function(arg, *args, **kwargs), None
    if isinstance(arg, dict):
        if _axis:  
            raise ValueError("Can only pass dict with axis=0")
        selected_obj = obj._selected_obj
        if any(is_aggregator(x) for x in arg.values()):
            new_arg = {}
            for k, v in arg.items():
                if not isinstance(v, (tuple, list, dict)):
                    new_arg[k] = [v]
                else:
                    new_arg[k] = v
                if isinstance(v, dict):
                    raise SpecificationError("nested renamer is not supported")
                elif isinstance(selected_obj, ABCSeries):
                    raise SpecificationError("nested renamer is not supported")
                elif (
                    isinstance(selected_obj, ABCDataFrame)
                    and k not in selected_obj.columns
                ):
                    raise KeyError(f"Column '{k}' does not exist!")
            arg = new_arg
        else:
            keys = list(arg.keys())
            if isinstance(selected_obj, ABCDataFrame) and len(
                selected_obj.columns.intersection(keys)
            ) != len(keys):
                cols = sorted(set(keys) - set(selected_obj.columns.intersection(keys)))
                raise SpecificationError(f"Column(s) {cols} do not exist")
        from pandas.core.reshape.concat import concat
        if selected_obj.ndim == 1:
            colg = obj._gotitem(obj._selection, ndim=1)
            results = {key: colg.agg(how) for key, how in arg.items()}
        else:
            results = {
                key: obj._gotitem(key, ndim=1).agg(how) for key, how in arg.items()
            }
        keys = list(arg.keys())
        def is_any_series():
            return any(isinstance(r, ABCSeries) for r in results.values())
        def is_any_frame():
            return any(isinstance(r, ABCDataFrame) for r in results.values())
        if isinstance(results, list):
            return concat(results, keys=keys, axis=1, sort=True), True
        elif is_any_frame():
            keys_to_use = [k for k in keys if not results[k].empty]
            keys_to_use = keys_to_use if keys_to_use != [] else keys
            return (
                concat([results[k] for k in keys_to_use], keys=keys_to_use, axis=1),
                True,
            )
        elif isinstance(obj, ABCSeries) and is_any_series():
            try:
                result = concat(results)
            except TypeError as err:
                raise ValueError(
                    "cannot perform both aggregation "
                    "and transformation operations "
                    "simultaneously"
                ) from err
            return result, True
        from pandas import DataFrame, Series
        try:
            result = DataFrame(results)
        except ValueError:
            if obj.ndim == 1:
                obj = cast("Series", obj)
                name = obj.name
            else:
                name = None
            result = Series(results, name=name)
        return result, True
    elif is_list_like(arg):
        return aggregate_multiple_funcs(obj, arg, _axis=_axis), None
    else:
        result = None
    if callable(arg):
        f = obj._get_cython_func(arg)
        if f and not args and not kwargs:
            return getattr(obj, f)(), None
    return result, True
