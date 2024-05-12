def fit(self, X, y, n_jobs=1):
    if n_jobs != 1:
        warnings.warn("The n_jobs parameter has been moved from the fit"
                      " method to the LinearRegression class constructor",
                      DeprecationWarning, stacklevel=2)
        n_jobs_ = n_jobs
    else:
        n_jobs_ = self.n_jobs
    X , y  = check_array(X, accept_sparse=['csr', 'csc', 'coo']), np.asarray(y)
    X, y, X_mean, y_mean, X_std = self._center_data(
        X, y, self.fit_intercept, self.normalize, self.copy_X)
    if sp.issparse(X):
        if y.ndim < 2:
            out = lsqr(X, y)
            self.coef_ , self.residues_  = out[0], out[3]
        else:
            outs = Parallel(n_jobs = n_jobs_)(
                delayed(lsqr)(X, y[:, j].ravel())
                for j in range(y.shape[1]))
            self.coef_ , self.residues_  = np.vstack((out[0] for out in outs)), np.vstack((out[3] for out in outs))
    else:
        self.coef_, self.residues_, self.rank_, self.singular_ = \
                linalg.lstsq(X, y)
        self.coef_ = self.coef_.T
    if y.ndim == 1:
        self.coef_ = np.ravel(self.coef_)
    self._set_intercept(X_mean, y_mean, X_std)
    return self
