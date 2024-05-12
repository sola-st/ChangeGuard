def _reduce(
    self,
    op,
    name,
    *,
    axis = 0,
    skipna = True,
    numeric_only = False,
    filter_type=None,
    **kwds,
):
    assert filter_type is None or filter_type == "bool", filter_type
    out_dtype = "bool" if filter_type == "bool" else None
    if axis is not None:
        axis = self._get_axis_number(axis)
    def func(values):
        return op(values, axis=axis, skipna=skipna, **kwds)
    dtype_has_keepdims = {}
    def blk_func(values, axis = 1):
        if isinstance(values, ExtensionArray):
            if not is_1d_only_ea_dtype(values.dtype) and not isinstance(
                self._mgr, ArrayManager
            ):
                return values._reduce(name, axis=1, skipna=skipna, **kwds)
            has_keepdims = dtype_has_keepdims.get(values.dtype)
            if has_keepdims is None:
                sign = signature(values._reduce)
                has_keepdims = "keepdims" in sign.parameters
                dtype_has_keepdims[values.dtype] = has_keepdims
            if has_keepdims:
                return values._reduce(name, skipna=skipna, keepdims=True, **kwds)
            else:
                warnings.warn(
                    f"{type(values)}._reduce will require a `keepdims` parameter "
                    "in the future",
                    FutureWarning,
                    stacklevel=find_stack_level(),
                )
                result = values._reduce(name, skipna=skipna, **kwds)
                return np.array([result])
        else:
            return op(values, axis=axis, skipna=skipna, **kwds)
    def _get_data():
        if filter_type is None:
            data = self._get_numeric_data()
        else:
            assert filter_type == "bool"
            data = self._get_bool_data()
        return data
    df = self
    if numeric_only:
        df = _get_data()
    if axis is None:
        dtype = find_common_type([arr.dtype for arr in df._mgr.arrays])
        if isinstance(dtype, ExtensionDtype):
            df = df.astype(dtype, copy=False)
            arr = concat_compat(list(df._iter_column_arrays()))
            return arr._reduce(name, skipna=skipna, keepdims=False, **kwds)
        return func(df.values)
    elif axis == 1:
        if len(df.index) == 0:
            result = df._reduce(
                op,
                name,
                axis=0,
                skipna=skipna,
                numeric_only=False,
                filter_type=filter_type,
                **kwds,
            ).iloc[:0]
            result.index = df.index
            return result
        df = df.T
    res = df._mgr.reduce(blk_func)
    out = df._constructor_from_mgr(res, axes=res.axes).iloc[0]
    if out_dtype is not None and out.dtype != "boolean":
        out = out.astype(out_dtype)
    elif (df._mgr.get_dtypes() == object).any() and name not in ["any", "all"]:
        out = out.astype(object)
    elif len(self) == 0 and out.dtype == object and name in ("sum", "prod"):
        out = out.astype(np.float64)
    return out
