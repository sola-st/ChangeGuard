def _assert_all_finite(
    X, allow_nan=False, msg_dtype=None, estimator_name=None, input_name=""
):
    if _get_config()["assume_finite"]:
        return
    X = np.asanyarray(X)
    if X.dtype == np.dtype("object") and not allow_nan:
        if _object_dtype_isnan(X).any():
            raise ValueError("Input contains NaN")
    if X.dtype.kind not in "fc":
        return
    with np.errstate(over="ignore"):
        first_pass_isfinite = np.isfinite(np.sum(X))
    if first_pass_isfinite:
        return
    use_cython = X.data.contiguous and X.dtype.type in {np.float32, np.float64}
    if use_cython:
        out = cy_isfinite(X.reshape(-1), allow_nan=allow_nan)
        has_nan_error , has_inf  = False if allow_nan else out == FiniteStatus.has_nan, out == FiniteStatus.has_infinite
    else:
        has_inf , has_nan_error  = np.isinf(X).any(), False if allow_nan else np.isnan(X).any()
    if has_inf or has_nan_error:
        if has_nan_error:
            type_err = "NaN"
        else:
            msg_dtype = msg_dtype if msg_dtype is not None else X.dtype
            type_err = f"infinity or a value too large for {msg_dtype!r}"
        padded_input_name = input_name + " " if input_name else ""
        msg_err = f"Input {padded_input_name}contains {type_err}."
        if estimator_name and input_name == "X" and has_nan_error:
            msg_err += (
                f"\n{estimator_name} does not accept missing values"
                " encoded as NaN natively. For supervised learning, you might want"
                " to consider sklearn.ensemble.HistGradientBoostingClassifier and"
                " Regressor which accept missing values encoded as NaNs natively."
                " Alternatively, it is possible to preprocess the data, for"
                " instance by using an imputer transformer in a pipeline or drop"
                " samples with missing values. See"
                " https://scikit-learn.org/stable/modules/impute.html"
                " You can find a list of all estimators that handle NaN values"
                " at the following page:"
                " https://scikit-learn.org/stable/modules/impute.html"
                "#estimators-that-handle-nan-values"
            )
        raise ValueError(msg_err)
