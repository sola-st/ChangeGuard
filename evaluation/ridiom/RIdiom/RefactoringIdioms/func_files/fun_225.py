def wrapper(self, other, axis=None):
    if axis is not None:
        self._get_axis_number(axis)
    res_name = get_op_result_name(self, other)
    other = lib.item_from_zerodim(other)
    finalizer = (
        lambda x: x.__finalize__(self)
        if isinstance(other, (np.ndarray, ABCIndexClass))
        else x
    )
    if isinstance(other, list):
        other = np.asarray(other)
    if isinstance(other, ABCDataFrame):  
        return NotImplemented
    elif isinstance(other, ABCSeries) and not self._indexed_same(other):
        raise ValueError("Can only compare identically-labeled Series objects")
    elif (
        is_list_like(other)
        and len(other) != len(self)
        and not isinstance(other, frozenset)
    ):
        raise ValueError("Lengths must match to compare")
    if is_categorical_dtype(self):
        res_values = dispatch_to_extension_op(op, self, other)
    elif is_datetime64_dtype(self) or is_datetime64tz_dtype(self):
        from pandas.core.arrays import DatetimeArray
        res_values = dispatch_to_extension_op(op, DatetimeArray(self), other)
    elif is_timedelta64_dtype(self):
        from pandas.core.arrays import TimedeltaArray
        res_values = dispatch_to_extension_op(op, TimedeltaArray(self), other)
    elif is_extension_array_dtype(self) or (
        is_extension_array_dtype(other) and not is_scalar(other)
    ):
        res_values = dispatch_to_extension_op(op, self, other)
    elif is_scalar(other) and isna(other):
        if op is operator.ne:
            res_values = np.ones(len(self), dtype=bool)
        else:
            res_values = np.zeros(len(self), dtype=bool)
    else:
        lvalues = extract_array(self, extract_numpy=True)
        rvalues = extract_array(other, extract_numpy=True)
        with np.errstate(all="ignore"):
            res_values = na_op(lvalues, rvalues)
        if is_scalar(res_values):
            raise TypeError(
                "Could not compare {typ} type with Series".format(typ=type(other))
            )
    result = self._constructor(res_values, index=self.index)
    return finalizer(result).rename(res_name)
