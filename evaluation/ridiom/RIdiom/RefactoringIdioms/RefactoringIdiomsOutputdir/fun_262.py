def _fit_ovo_binary(estimator, X, y, i, j):
    cond = np.logical_or(y == i, y == j)
    y = y[cond]
    y_binary = np.empty(y.shape, np.int)
    y_binary[y == i] , y_binary[y == j], ind  = 0, 1, np.arange(X.shape[0])
    return _fit_binary(estimator, X[ind[cond]], y_binary, classes=[i, j])
