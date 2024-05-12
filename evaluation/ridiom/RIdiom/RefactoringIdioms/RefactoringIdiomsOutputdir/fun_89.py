def sanitize_masked_array(data):
    mask = ma.getmaskarray(data)
    if mask.any():
        dtype, fill_value = maybe_promote(data.dtype, np.nan)
        dtype = cast(np.dtype, dtype)
        data = ma.asarray(data.astype(dtype, copy=True))
        data.soften_mask()  
        data[mask] = fill_value
    else:
        data = data.copy()
    return data
