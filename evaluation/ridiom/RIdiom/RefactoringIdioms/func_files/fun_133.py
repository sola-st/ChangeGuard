def _check_params_vs_input(self, X, default_n_init=None):
    if X.shape[0] < self.n_clusters:
        raise ValueError(
            f"n_samples={X.shape[0]} should be >= n_clusters={self.n_clusters}."
        )
    self._tol = _tolerance(X, self.tol)
    self._n_init = self.n_init
    if self._n_init == "warn":
        warnings.warn(
            (
                "The default value of `n_init` will change from "
                f"{default_n_init} to 'auto' in 1.4. Set the value of `n_init`"
                " explicitly to suppress the warning"
            ),
            FutureWarning,
            stacklevel=2,
        )
        self._n_init = default_n_init
    if self._n_init == "auto":
        if self.init == "k-means++":
            self._n_init = 1
        else:
            self._n_init = default_n_init
    if _is_arraylike_not_scalar(self.init) and self._n_init != 1:
        warnings.warn(
            (
                "Explicit initial center position passed: performing only"
                f" one init in {self.__class__.__name__} instead of "
                f"n_init={self._n_init}."
            ),
            RuntimeWarning,
            stacklevel=2,
        )
        self._n_init = 1
