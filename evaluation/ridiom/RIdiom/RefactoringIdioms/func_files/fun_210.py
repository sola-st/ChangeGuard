def maybe_upcast(
    values,
    fill_value = np.nan,
    copy = False,
):
    new_dtype, fill_value = maybe_promote(values.dtype, fill_value)
    values = values.astype(new_dtype, copy=copy)
    return values, fill_value
