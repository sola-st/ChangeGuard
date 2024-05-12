def is_categorical_dtype(arr_or_dtype):
    warnings.warn(
        "is_categorical_dtype is deprecated and will be removed in a future "
        "version. Use isinstance(dtype, pd.CategoricalDtype) instead",
        FutureWarning,
        stacklevel=find_stack_level(),
    )
    if isinstance(arr_or_dtype, ExtensionDtype):
        return arr_or_dtype.name == "category"
    if arr_or_dtype is None:
        return False
    return CategoricalDtype.is_dtype(arr_or_dtype)
