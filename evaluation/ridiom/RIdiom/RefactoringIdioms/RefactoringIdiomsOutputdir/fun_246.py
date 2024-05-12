def _fit(self, X):
    if issparse(X):
        raise TypeError(
            "PCA does not support sparse input. See "
            "TruncatedSVD for a possible alternative."
        )
    X = self._validate_data(
        X, dtype=[np.float64, np.float32], ensure_2d=True, copy=self.copy
    )
    if self.n_components is None:
        if self.svd_solver != "arpack":
            n_components = min(X.shape)
        else:
            n_components = min(X.shape) - 1
    else:
        n_components = self.n_components
    self._fit_svd_solver = self.svd_solver
    if self._fit_svd_solver == "auto":
        if max(X.shape) <= 500 or n_components == "mle":
            self._fit_svd_solver = "full"
        elif 1 <= n_components < 0.8 * min(X.shape):
            self._fit_svd_solver = "randomized"
        else:
            self._fit_svd_solver = "full"
    if self._fit_svd_solver == "full":
        return self._fit_full(X, n_components)
    elif self._fit_svd_solver in ["arpack", "randomized"]:
        return self._fit_truncated(X, n_components, self._fit_svd_solver)
    else:
        raise ValueError(
            "Unrecognized svd_solver='{0}'".format(self._fit_svd_solver)
        )
