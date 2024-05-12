def ridge_regression(X, y, alpha, sample_weight=1.0, solver='auto',
                     max_iter=None, tol=1e-3):
    n_samples, n_features = X.shape
    if y.ndim > 2:
        raise ValueError("Target y has the wrong shape %s" % str(y.shape))
    ravel = False
    if y.ndim == 1:
        y = y.reshape(-1, 1)
        ravel = True
    n_samples_, n_targets = y.shape
    if n_samples != n_samples_:
        raise ValueError("Number of samples in X and y does not correspond:"
                         " %d != %d" % (n_samples, n_samples_))
    has_sw = isinstance(sample_weight, np.ndarray) or sample_weight != 1.0
    if solver == 'auto':
        if hasattr(X, '__array__'):
            solver = 'dense_cholesky'
        else:
            solver = 'sparse_cg'
    elif solver == 'lsqr' and not hasattr(sp_linalg, 'lsqr'):
        warnings.warn("""lsqr not available on this machine, falling back
                      to sparse_cg.""")
        solver = 'sparse_cg'
    if has_sw:
        solver = 'dense_cholesky'
    alpha = safe_asarray(alpha).ravel()
    if alpha.size not in [1, n_targets]:
        raise ValueError("Number of targets and number of penalties "
                    "do not correspond: %d != %d" % (alpha.size, n_targets))
    if solver != "svd":
        one_alpha = alpha.size == 1
        if alpha.size == 1 and n_targets > 1:
            alpha = np.repeat(alpha, n_targets)
    if solver not in ('sparse_cg', 'dense_cholesky', 'svd', 'lsqr'):
        ValueError('Solver %s not understood' % solver)
    if solver == 'sparse_cg':
        X1 = sp_linalg.aslinearoperator(X)
        coefs = np.empty((y.shape[1], n_features))
        if n_features > n_samples:
            def create_mv(curr_alpha):
                def _mv(x):
                    return X1.matvec(X1.rmatvec(x)) + curr_alpha * x
                return _mv
        else:
            def create_mv(curr_alpha):
                def _mv(x):
                    return X1.rmatvec(X1.matvec(x)) + curr_alpha * x
                return _mv
        for i in range(y.shape[1]):
            y_column = y[:, i]
            mv = create_mv(alpha[i])
            if n_features > n_samples:
                C = sp_linalg.LinearOperator(
                    (n_samples, n_samples), matvec=mv, dtype=X.dtype)
                coef, info = sp_linalg.cg(C, y_column, tol=tol)
                coefs[i] = X1.rmatvec(coef)
            else:
                y_column = X1.rmatvec(y_column)
                C = sp_linalg.LinearOperator(
                    (n_features, n_features), matvec=mv, dtype=X.dtype)
                coefs[i], info = sp_linalg.cg(C, y_column, maxiter=max_iter,
                                              tol=tol)
            if info != 0:
                raise ValueError("Failed with error code %d" % info)
        if ravel:
            coefs = np.ravel(coefs)
        return coefs
    if solver == "lsqr":
        coefs = np.empty((y.shape[1], n_features))
        sqrt_alpha = np.sqrt(alpha)
        for i in range(y.shape[1]):
            y_column = y[:, i]
            coefs[i] = sp_linalg.lsqr(X, y_column, damp=sqrt_alpha[i],
                                      atol=tol, btol=tol, iter_lim=max_iter)[0]
        if ravel:
            coefs = np.ravel(coefs)
        return coefs
    if solver == 'dense_cholesky':
        if n_features > n_samples or has_sw:
            K = safe_sparse_dot(X, X.T, dense_output=True)
            if has_sw:
                sw = np.sqrt(sample_weight)
                y = y * sw[:, np.newaxis]
                K *= np.outer(sw, sw)
            try:
                if one_alpha:
                    K.flat[::n_samples + 1] += alpha[0]
                    dual_coef = linalg.solve(K, y,
                                         sym_pos=True, overwrite_a=True)
                    if has_sw:
                        if dual_coef.ndim == 1:
                            dual_coef *= sw
                        else:
                            dual_coef *= sw[:, np.newaxis]
                    coef = safe_sparse_dot(X.T, dual_coef,
                                               dense_output=True).T
                    if ravel:
                        coef = coef.ravel()
                    return coef
                else:
                    coef = np.empty([n_targets, n_features])
                    dual_coefs = np.empty([n_targets, n_samples])
                    for dual_coef, target, current_alpha in zip(
                            dual_coefs, y.T, alpha):
                        K.flat[::n_samples + 1] += current_alpha
                        dual_coef[:] = linalg.solve(K, target, sym_pos=True,
                                                 overwrite_a=False).ravel()
                        K.flat[::n_samples + 1] -= current_alpha
                    if has_sw:
                        dual_coefs *= sw[np.newaxis, :]
                    coef = safe_sparse_dot(dual_coefs, X, dense_output=True).T
                    if ravel:
                        coef = coef.ravel()
                    return coef
            except linalg.LinAlgError:
                solver = 'svd'
        else:
            A = safe_sparse_dot(X.T, X, dense_output=True)
            Xy = safe_sparse_dot(X.T, y, dense_output=True)
            if one_alpha:
                A.flat[::n_features + 1] += alpha[0]
                try:
                    coef = linalg.solve(A, Xy, sym_pos=True,
                                        overwrite_a=True).T
                    if ravel:
                        coef = coef.ravel()
                    return coef
                except linalg.LinAlgError:
                    solver = 'svd'
            else:
                coefs = np.empty([n_targets, n_features])
                for coef, target, current_alpha in zip(
                        coefs, Xy.T, alpha):
                    A.flat[::n_features + 1] += current_alpha
                    coef[:] = linalg.solve(A, target, sym_pos=True,
                                           overwrite_a=False).ravel()
                    A.flat[::n_features + 1] -= current_alpha
                return coefs
    if solver == 'svd':
        alpha_dim = alpha.ndim
        if alpha_dim == 1 and len(alpha) != n_targets:
            alpha = alpha[:, np.newaxis]
        alpha = np.atleast_2d(alpha)
        assert alpha.ndim == 2
        U, s, Vt = linalg.svd(X, full_matrices=False)
        idx = s > 1e-15  
        UTy = U.T.dot(y)
        s[idx == False] = 0.
        d = (s[np.newaxis, :, np.newaxis] /
             (s[np.newaxis, :, np.newaxis] ** 2 + alpha[:, np.newaxis, :]))
        d_UT_y = d * UTy[np.newaxis, :, :]
        coef_ = np.empty([alpha.shape[0], n_targets, n_features])
        for dUTy, coef_slice in zip(d_UT_y, coef_):
            coef_slice[:] = Vt.T.dot(dUTy).T
        if (alpha_dim == 0) or (alpha_dim == 1 and alpha.size == n_targets):
            coef_ = coef_.reshape(n_targets, n_features)
            if ravel:
                coef_ = coef_.ravel()
        else:
            if ravel:
                coef_ = coef_.squeeze()
        return coef_
