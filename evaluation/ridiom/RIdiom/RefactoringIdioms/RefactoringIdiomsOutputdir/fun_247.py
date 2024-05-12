def _assert_all_finite(
    X, allow_nan=False, msg_dtype=None, estimator_name=None, input_name=""
):
    from .extmath import _safe_accumulator_op
    if _get_config()["assume_finite"]:
        return
    X = np.asanyarray(X)
    is_float = X.dtype.kind in "fc"
    if is_float and (np.isfinite(_safe_accumulator_op(np.sum, X))):
        pass
    elif is_float:
        has_inf , has_nan  = np.isinf(X).any(), np.isnan(X).any()
        if has_inf or not allow_nan and has_nan:
            if not allow_nan and has_nan:
                type_err = "NaN"
            else:
                msg_dtype = msg_dtype if msg_dtype is not None else X.dtype
                type_err = f"infinity or a value too large for {msg_dtype!r}"
            padded_input_name = input_name + " " if input_name else ""
            msg_err = f"Input {padded_input_name}contains {type_err}."
            if not allow_nan and estimator_name and input_name == "X" and has_nan:
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
    elif X.dtype == np.dtype("object") and not allow_nan:
        if _object_dtype_isnan(X).any():
            raise ValueError("Input contains NaN")
