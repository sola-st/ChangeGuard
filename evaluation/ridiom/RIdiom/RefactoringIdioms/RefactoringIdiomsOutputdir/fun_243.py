def _alpha_grid(
    X,
    y,
    Xy=None,
    l1_ratio=1.0,
    fit_intercept=True,
    eps=1e-3,
    n_alphas=100,
    copy_X=True,
):
    if not l1_ratio:
        raise ValueError(
            "Automatic alpha grid generation is not supported for"
            " l1_ratio=0. Please supply a grid by providing "
            "your estimator with the appropriate `alphas=` "
            "argument."
        )
    n_samples , sparse_center  = len(y), False
    if Xy is None:
        X_sparse = sparse.isspmatrix(X)
        sparse_center , X  = X_sparse and fit_intercept, check_array(X, accept_sparse='csc', copy=copy_X and fit_intercept and (not X_sparse))
        if not X_sparse:
            X, y, _, _, _ = _preprocess_data(X, y, fit_intercept, copy=False)
        Xy = safe_sparse_dot(X.T, y, dense_output=True)
        if sparse_center:
            _, _, X_offset, _, X_scale = _preprocess_data(X, y, fit_intercept)
            mean_dot = X_offset * np.sum(y)
    if Xy.ndim == 1:
        Xy = Xy[:, np.newaxis]
    if sparse_center:
        if fit_intercept:
            Xy -= mean_dot[:, np.newaxis]
    alpha_max = np.sqrt(np.sum(Xy**2, axis=1)).max() / (n_samples * l1_ratio)
    if alpha_max <= np.finfo(float).resolution:
        alphas = np.empty(n_alphas)
        alphas.fill(np.finfo(float).resolution)
        return alphas
    return np.geomspace(alpha_max, alpha_max * eps, num=n_alphas)
