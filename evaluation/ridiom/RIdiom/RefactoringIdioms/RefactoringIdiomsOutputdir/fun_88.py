def infer_freq(
    index,
):
    from pandas.core.api import DatetimeIndex
    if isinstance(index, ABCSeries):
        values = index._values
        if not (
            lib.is_np_dtype(values.dtype, "mM")
            or isinstance(values.dtype, DatetimeTZDtype)
            or values.dtype == object
        ):
            raise TypeError(
                "cannot infer freq from a non-convertible dtype "
                f"on a Series of {index.dtype}"
            )
        index = values
    if not hasattr(index, "dtype"):
        pass
    elif isinstance(index.dtype, PeriodDtype):
        raise TypeError(
            "PeriodIndex given. Check the `freq` attribute "
            "instead of using infer_freq."
        )
    elif lib.is_np_dtype(index.dtype, "m"):
        inferer = _TimedeltaFrequencyInferer(index)
        return inferer.get_freq()
    elif is_numeric_dtype(index.dtype):
        raise TypeError(
            f"cannot infer freq from a non-convertible index of dtype {index.dtype}"
        )
    if not isinstance(index, DatetimeIndex):
        index = DatetimeIndex(index)
    inferer = _FrequencyInferer(index)
    return inferer.get_freq()
