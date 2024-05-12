def agg_list_like(self):
    from pandas.core.groupby.generic import (
        DataFrameGroupBy,
        SeriesGroupBy,
    )
    from pandas.core.reshape.concat import concat
    obj , arg  = self.obj, cast(List[AggFuncTypeBase], self.f)
    if getattr(obj, "axis", 0) == 1:
        raise NotImplementedError("axis other than 0 is not supported")
    if not isinstance(obj, SelectionMixin):
        selected_obj = obj
    elif obj._selected_obj.ndim == 1:
        selected_obj = obj._selected_obj
    else:
        selected_obj = obj._obj_with_exclusions
    results , keys , is_groupby , is_ser_or_df  = [], [], isinstance(obj, (DataFrameGroupBy, SeriesGroupBy)), isinstance(obj, (ABCDataFrame, ABCSeries))
    this_args = [self.axis, *self.args] if is_ser_or_df else self.args
    if is_groupby:
        context_manager = com.temp_setattr(obj, "as_index", True)
    else:
        context_manager = nullcontext()
    with context_manager:
        if selected_obj.ndim == 1:
            for a in arg:
                colg = obj._gotitem(selected_obj.name, ndim=1, subset=selected_obj)
                new_res = colg.aggregate(a, *this_args, **self.kwargs)
                results.append(new_res)
                name = com.get_callable_name(a) or a
                keys.append(name)
        else:
            indices = []
            for index, col in enumerate(selected_obj):
                colg = obj._gotitem(col, ndim=1, subset=selected_obj.iloc[:, index])
                new_res = colg.aggregate(arg, *this_args, **self.kwargs)
                results.append(new_res)
                indices.append(index)
            keys = selected_obj.columns.take(indices)
    try:
        return concat(results, keys=keys, axis=1, sort=False)
    except TypeError as err:
        from pandas import Series
        result = Series(results, index=keys, name=obj.name)
        if is_nested_object(result):
            raise ValueError(
                "cannot combine transform and aggregation operations"
            ) from err
        return result
