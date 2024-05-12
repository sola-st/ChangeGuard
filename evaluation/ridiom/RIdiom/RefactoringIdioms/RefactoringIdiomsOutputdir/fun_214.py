def maybe_upcast_putmask(result, mask, other):
    if not isinstance(result, np.ndarray):
        raise ValueError("The result input must be a ndarray.")
    if not is_scalar(other):
        raise ValueError("other must be a scalar")
    if mask.any():
        if result.dtype.kind in ["m", "M"]:
            if is_scalar(other):
                if isna(other):
                    other = result.dtype.type("nat")
                elif is_integer(other):
                    other = np.array(other, dtype=result.dtype)
            elif is_integer_dtype(other):
                other = np.array(other, dtype=result.dtype)
        def changeit():
            r, _ = maybe_upcast(result, fill_value=other, copy=True)
            np.place(r, mask, other)
            return r, True
        new_dtype, _ = maybe_promote(result.dtype, other)
        if new_dtype != result.dtype:
            if isna(other):
                return changeit()
        try:
            np.place(result, mask, other)
        except TypeError:
            return changeit()
    return result, False
