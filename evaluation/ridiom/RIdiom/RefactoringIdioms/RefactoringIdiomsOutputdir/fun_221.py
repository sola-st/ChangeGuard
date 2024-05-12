def maybe_promote(dtype, fill_value=np.nan):
    if isinstance(fill_value, np.ndarray):
        if issubclass(fill_value.dtype.type, (np.datetime64, np.timedelta64)):
            fill_value = fill_value.dtype.type("NaT", "ns")
        else:
            if fill_value.dtype == np.object_:
                dtype = np.dtype(np.object_)
            fill_value = np.nan
        if dtype == np.object_ or dtype.kind in ["U", "S"]:
            fill_value , dtype  = np.nan, np.dtype(np.object_)
    if issubclass(dtype.type, np.datetime64):
        if isinstance(fill_value, datetime) and fill_value.tzinfo is not None:
            dtype = np.dtype(np.object_)
        elif is_integer(fill_value) or (is_float(fill_value) and not isna(fill_value)):
            dtype = np.dtype(np.object_)
        else:
            try:
                fill_value = tslibs.Timestamp(fill_value).to_datetime64()
            except (TypeError, ValueError):
                dtype = np.dtype(np.object_)
    elif issubclass(dtype.type, np.timedelta64):
        if (
            is_integer(fill_value)
            or (is_float(fill_value) and not np.isnan(fill_value))
            or isinstance(fill_value, str)
        ):
            dtype = np.dtype(np.object_)
        else:
            try:
                fv = tslibs.Timedelta(fill_value)
            except ValueError:
                dtype = np.dtype(np.object_)
            else:
                if fv is NaT:
                    fill_value = np.timedelta64("NaT", "ns")
                else:
                    fill_value = fv.to_timedelta64()
    elif is_datetime64tz_dtype(dtype):
        if isna(fill_value):
            fill_value = NaT
    elif is_extension_array_dtype(dtype) and isna(fill_value):
        fill_value = dtype.na_value
    elif is_float(fill_value):
        if issubclass(dtype.type, np.bool_):
            dtype = np.object_
        elif issubclass(dtype.type, np.integer):
            dtype = np.dtype(np.float64)
            if not isna(fill_value):
                fill_value = dtype.type(fill_value)
        elif dtype.kind == "f":
            if not np.can_cast(fill_value, dtype):
                dtype = np.min_scalar_type(fill_value)
        elif dtype.kind == "c":
            mst = np.min_scalar_type(fill_value)
            dtype = np.promote_types(dtype, mst)
            if dtype.kind == "c" and not np.isnan(fill_value):
                fill_value = dtype.type(fill_value)
    elif is_bool(fill_value):
        if not issubclass(dtype.type, np.bool_):
            dtype = np.object_
        else:
            fill_value = np.bool_(fill_value)
    elif is_integer(fill_value):
        if issubclass(dtype.type, np.bool_):
            dtype = np.dtype(np.object_)
        elif issubclass(dtype.type, np.integer):
            if not np.can_cast(fill_value, dtype):
                mst = np.min_scalar_type(fill_value)
                dtype = np.promote_types(dtype, mst)
                if dtype.kind == "f":
                    dtype = np.dtype(np.object_)
            fill_value = dtype.type(fill_value)
        elif issubclass(dtype.type, np.floating):
            if _check_lossless_cast(fill_value, dtype):
                fill_value = dtype.type(fill_value)
        if dtype.kind in ["c", "f"]:
            fill_value = dtype.type(fill_value)
    elif is_complex(fill_value):
        if issubclass(dtype.type, np.bool_):
            dtype = np.dtype(np.object_)
        elif issubclass(dtype.type, (np.integer, np.floating)):
            mst = np.min_scalar_type(fill_value)
            dtype = np.promote_types(dtype, mst)
        elif dtype.kind == "c":
            mst = np.min_scalar_type(fill_value)
            if mst > dtype and mst.kind == "c":
                dtype = mst
        if dtype.kind == "c":
            fill_value = dtype.type(fill_value)
    elif fill_value is None:
        if is_float_dtype(dtype) or is_complex_dtype(dtype):
            fill_value = np.nan
        elif is_integer_dtype(dtype):
            dtype , fill_value  = np.float64, np.nan
        elif is_datetime_or_timedelta_dtype(dtype):
            fill_value = dtype.type("NaT", "ns")
        else:
            dtype , fill_value  = np.object_, np.nan
    else:
        dtype = np.object_
    if is_extension_array_dtype(dtype):
        pass
    elif issubclass(np.dtype(dtype).type, (bytes, str)):
        dtype = np.object_
    return dtype, fill_value
