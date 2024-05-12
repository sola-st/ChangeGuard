def convert_fill_value(value, pa_type, dtype):
    if value is None:
        return value
    if isinstance(value, (pa.Scalar, pa.Array, pa.ChunkedArray)):
        return value
    if isinstance(value, Timedelta) and value.unit in ("s", "ms"):
        value = value.to_numpy()
    if is_array_like(value):
        pa_box = pa.array
    else:
        pa_box = pa.scalar
    try:
        value = pa_box(value, type=pa_type, from_pandas=True)
    except pa.ArrowTypeError as err:
        msg = f"Invalid value '{str(value)}' for dtype {dtype}"
        raise TypeError(msg) from err
    return value
