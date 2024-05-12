def _fit(self, X, compute_sources=False):
    XT , fun_args  = self._validate_data(X, copy=self.whiten, dtype=FLOAT_DTYPES, ensure_min_samples=2).T, {} if self.fun_args is None else self.fun_args
    random_state , alpha  = check_random_state(self.random_state), fun_args.get('alpha', 1.0)
    if not 1 <= alpha <= 2:
        raise ValueError('alpha must be in [1,2]')
    if self.fun == 'logcosh':
        g = _logcosh
    elif self.fun == 'exp':
        g = _exp
    elif self.fun == 'cube':
        g = _cube
    elif callable(self.fun):
        def g(x, fun_args):
            return self.fun(x, **fun_args)
    else:
        exc = ValueError if isinstance(self.fun, str) else TypeError
        raise exc(
            "Unknown function %r;"
            " should be one of 'logcosh', 'exp', 'cube' or callable"
            % self.fun
        )
    n_features, n_samples = XT.shape
    n_components = self.n_components
    if not self.whiten and n_components is not None:
        n_components = None
        warnings.warn('Ignoring n_components with whiten=False.')
    if n_components is None:
        n_components = min(n_samples, n_features)
    if (n_components > min(n_samples, n_features)):
        n_components = min(n_samples, n_features)
        warnings.warn(
            'n_components is too large: it will be set to %s'
            % n_components
        )
    if self.whiten:
        X_mean = XT.mean(axis=-1)
        XT -= X_mean[:, np.newaxis]
        u, d, _ = linalg.svd(XT, full_matrices=False, check_finite=False)
        del _
        K = (u / d).T[:n_components]  
        del u, d
        X1 = np.dot(K, XT)
        X1 *= np.sqrt(n_samples)
    else:
        X1 = as_float_array(XT, copy=False)  
    w_init = self.w_init
    if w_init is None:
        w_init = np.asarray(random_state.normal(
            size=(n_components, n_components)), dtype=X1.dtype)
    else:
        w_init = np.asarray(w_init)
        if w_init.shape != (n_components, n_components):
            raise ValueError(
                'w_init has invalid shape -- should be %(shape)s'
                % {'shape': (n_components, n_components)})
    kwargs = {'tol': self.tol,
              'g': g,
              'fun_args': fun_args,
              'max_iter': self.max_iter,
              'w_init': w_init}
    if self.algorithm == 'parallel':
        W, n_iter = _ica_par(X1, **kwargs)
    elif self.algorithm == 'deflation':
        W, n_iter = _ica_def(X1, **kwargs)
    else:
        raise ValueError('Invalid algorithm: must be either `parallel` or'
                         ' `deflation`.')
    del X1
    if compute_sources:
        if self.whiten:
            S = np.linalg.multi_dot([W, K, XT]).T
        else:
            S = np.dot(W, XT).T
    else:
        S = None
    self.n_iter_ = n_iter
    if self.whiten:
        self.components_ , self.mean_ , self.whitening_  = np.dot(W, K), X_mean, K
    else:
        self.components_ = W
    self.mixing_ , self._unmixing  = linalg.pinv(self.components_, check_finite=False), W
    return S
