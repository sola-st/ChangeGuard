def check_array(
    array,
    accept_sparse=False,
    *,
    accept_large_sparse=True,
    dtype="numeric",
    order=None,
    copy=False,
    force_all_finite=True,
    ensure_2d=True,
    allow_nd=False,
    ensure_min_samples=1,
    ensure_min_features=1,
    estimator=None,
    input_name="",
):
    if isinstance(array, np.matrix):
        raise TypeError(
            "np.matrix is not supported. Please convert to a numpy array with "
            "np.asarray. For more information see: "
            "https://numpy.org/doc/stable/reference/generated/numpy.matrix.html"
        )
    xp, is_array_api_compliant = get_namespace(array)
    array_orig = array
    dtype_numeric = isinstance(dtype, str) and dtype == "numeric"
    dtype_orig = getattr(array, "dtype", None)
    if not is_array_api_compliant and not hasattr(dtype_orig, "kind"):
        dtype_orig = None
    dtypes_orig = None
    pandas_requires_conversion = False
    if hasattr(array, "dtypes") and hasattr(array.dtypes, "__array__"):
        with suppress(ImportError):
            from pandas import SparseDtype
            def is_sparse(dtype):
                return isinstance(dtype, SparseDtype)
            if not hasattr(array, "sparse") and array.dtypes.apply(is_sparse).any():
                warnings.warn(
                    "pandas.DataFrame with sparse columns found."
                    "It will be converted to a dense numpy array."
                )
        dtypes_orig = list(array.dtypes)
        pandas_requires_conversion = any(
            _pandas_dtype_needs_early_conversion(i) for i in dtypes_orig
        )
        if all(isinstance(dtype_iter, np.dtype) for dtype_iter in dtypes_orig):
            dtype_orig = np.result_type(*dtypes_orig)
        elif pandas_requires_conversion and any(d == object for d in dtypes_orig):
            dtype_orig = object
    elif (_is_extension_array_dtype(array) or hasattr(array, "iloc")) and hasattr(
        array, "dtype"
    ):
        pandas_requires_conversion = _pandas_dtype_needs_early_conversion(array.dtype)
        if isinstance(array.dtype, np.dtype):
            dtype_orig = array.dtype
        else:
            dtype_orig = None
    if dtype_numeric:
        if (
            dtype_orig is not None
            and hasattr(dtype_orig, "kind")
            and dtype_orig.kind == "O"
        ):
            dtype = xp.float64
        else:
            dtype = None
    if isinstance(dtype, (list, tuple)):
        if dtype_orig is not None and dtype_orig in dtype:
            dtype = None
        else:
            dtype = dtype[0]
    if pandas_requires_conversion:
        new_dtype = dtype_orig if dtype is None else dtype
        array = array.astype(new_dtype)
        dtype = None
    if force_all_finite not in (True, False, "allow-nan"):
        raise ValueError(
            'force_all_finite should be a bool or "allow-nan". Got {!r} instead'.format(
                force_all_finite
            )
        )
    if dtype is not None and _is_numpy_namespace(xp):
        dtype = np.dtype(dtype)
    estimator_name = _check_estimator_name(estimator)
    context = " by %s" % estimator_name if estimator is not None else ""
    if hasattr(array, "sparse") and array.ndim > 1:
        with suppress(ImportError):
            from pandas import SparseDtype  
            def is_sparse(dtype):
                return isinstance(dtype, SparseDtype)
            if array.dtypes.apply(is_sparse).all():
                array = array.sparse.to_coo()
                if array.dtype == np.dtype("object"):
                    unique_dtypes = set([dt.subtype.name for dt in array_orig.dtypes])
                    if len(unique_dtypes) > 1:
                        raise ValueError(
                            "Pandas DataFrame with mixed sparse extension arrays "
                            "generated a sparse matrix with object dtype which "
                            "can not be converted to a scipy sparse matrix."
                            "Sparse extension arrays should all have the same "
                            "numeric type."
                        )
    if sp.issparse(array):
        _ensure_no_complex_data(array)
        array = _ensure_sparse_format(
            array,
            accept_sparse=accept_sparse,
            dtype=dtype,
            copy=copy,
            force_all_finite=force_all_finite,
            accept_large_sparse=accept_large_sparse,
            estimator_name=estimator_name,
            input_name=input_name,
        )
    else:
        with warnings.catch_warnings():
            try:
                warnings.simplefilter("error", ComplexWarning)
                if dtype is not None and xp.isdtype(dtype, "integral"):
                    array = _asarray_with_order(array, order=order, xp=xp)
                    if xp.isdtype(array.dtype, ("real floating", "complex floating")):
                        _assert_all_finite(
                            array,
                            allow_nan=False,
                            msg_dtype=dtype,
                            estimator_name=estimator_name,
                            input_name=input_name,
                        )
                    array = xp.astype(array, dtype, copy=False)
                else:
                    array = _asarray_with_order(array, order=order, dtype=dtype, xp=xp)
            except ComplexWarning as complex_warning:
                raise ValueError(
                    "Complex data not supported\n{}\n".format(array)
                ) from complex_warning
        _ensure_no_complex_data(array)
        if ensure_2d:
            if array.ndim == 0:
                raise ValueError(
                    "Expected 2D array, got scalar array instead:\narray={}.\n"
                    "Reshape your data either using array.reshape(-1, 1) if "
                    "your data has a single feature or array.reshape(1, -1) "
                    "if it contains a single sample.".format(array)
                )
            if array.ndim == 1:
                raise ValueError(
                    "Expected 2D array, got 1D array instead:\narray={}.\n"
                    "Reshape your data either using array.reshape(-1, 1) if "
                    "your data has a single feature or array.reshape(1, -1) "
                    "if it contains a single sample.".format(array)
                )
        if dtype_numeric and hasattr(array.dtype, "kind") and array.dtype.kind in "USV":
            raise ValueError(
                "dtype='numeric' is not compatible with arrays of bytes/strings."
                "Convert your data to numeric values explicitly instead."
            )
        if not allow_nd and array.ndim >= 3:
            raise ValueError(
                "Found array with dim %d. %s expected <= 2."
                % (array.ndim, estimator_name)
            )
        if force_all_finite:
            _assert_all_finite(
                array,
                input_name=input_name,
                estimator_name=estimator_name,
                allow_nan=force_all_finite == "allow-nan",
            )
        if copy:
            if _is_numpy_namespace(xp):
                if np.may_share_memory(array, array_orig):
                    array = _asarray_with_order(
                        array, dtype=dtype, order=order, copy=True, xp=xp
                    )
            else:
                array = _asarray_with_order(
                    array, dtype=dtype, order=order, copy=True, xp=xp
                )
    if ensure_min_samples > 0:
        n_samples = _num_samples(array)
        if n_samples < ensure_min_samples:
            raise ValueError(
                "Found array with %d sample(s) (shape=%s) while a"
                " minimum of %d is required%s."
                % (n_samples, array.shape, ensure_min_samples, context)
            )
    if ensure_min_features > 0 and array.ndim == 2:
        n_features = array.shape[1]
        if n_features < ensure_min_features:
            raise ValueError(
                "Found array with %d feature(s) (shape=%s) while"
                " a minimum of %d is required%s."
                % (n_features, array.shape, ensure_min_features, context)
            )
    return array
