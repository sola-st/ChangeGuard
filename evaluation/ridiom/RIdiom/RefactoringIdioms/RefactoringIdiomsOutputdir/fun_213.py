def interpolate(
    self,
    method = "linear",
    axis = 0,
    limit = None,
    inplace = False,
    limit_direction = "forward",
    limit_area = None,
    downcast = None,
    **kwargs,
):
    inplace , axis , fillna_methods  = validate_bool_kwarg(inplace, 'inplace'), self._get_axis_number(axis), ['ffill', 'bfill', 'pad', 'backfill']
    should_transpose = axis == 1 and method not in fillna_methods
    obj = self.T if should_transpose else self
    if method not in fillna_methods:
        axis = self._info_axis_number
    if isinstance(obj.index, MultiIndex) and method != "linear":
        raise ValueError(
            "Only `method=linear` interpolation is supported on MultiIndexes."
        )
    if obj.ndim == 2 and np.all(obj.dtypes == np.dtype(object)):
        raise TypeError(
            "Cannot interpolate with all object-dtype columns "
            "in the DataFrame. Try setting at least one "
            "column to a numeric dtype."
        )
    if method == "linear":
        index = np.arange(len(obj.index))
    else:
        index = obj.index
        methods , is_numeric_or_datetime  = {'index', 'values', 'nearest', 'time'}, is_numeric_dtype(index.dtype) or is_datetime64_any_dtype(index.dtype) or is_timedelta64_dtype(index.dtype)
        if method not in methods and not is_numeric_or_datetime:
            raise ValueError(
                "Index column must be numeric or datetime type when "
                f"using {method} method other than linear. "
                "Try setting a numeric or datetime index column before "
                "interpolating."
            )
    if isna(index).any():
        raise NotImplementedError(
            "Interpolation with NaNs in the index "
            "has not been implemented. Try filling "
            "those NaNs before interpolating."
        )
    new_data = obj._mgr.interpolate(
        method=method,
        axis=axis,
        index=index,
        limit=limit,
        limit_direction=limit_direction,
        limit_area=limit_area,
        inplace=inplace,
        downcast=downcast,
        **kwargs,
    )
    result = self._constructor(new_data)
    if should_transpose:
        result = result.T
    if inplace:
        return self._update_inplace(result)
    else:
        return result.__finalize__(self, method="interpolate")
