def _lstsq(X, y, indices, fit_intercept):
    fit_intercept = int(fit_intercept)
    n_features = X.shape[1] + fit_intercept
    n_subsamples = indices.shape[1]
    weights , X_subpopulation , y_subpopulation  = np.empty((indices.shape[0], n_features)), np.ones((n_subsamples, n_features)), np.zeros(max(n_subsamples, n_features))
    lstsq, = get_lapack_funcs(('gelss',), (X_subpopulation, y_subpopulation))
    for index, subset in enumerate(indices):
        X_subpopulation[:, fit_intercept:] , y_subpopulation[:n_subsamples]  = X[subset, :], y[subset]
        weights[index] = lstsq(X_subpopulation,
                               y_subpopulation)[1][:n_features]
    return weights
