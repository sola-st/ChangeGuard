def transform(self, X):
    check_is_fitted(self)
    X = self._validate_data(X, reset=False, accept_sparse=False, ensure_2d=True)
    n_samples, n_features = X.shape
    n_splines , degree , scipy_1_10  = self.bsplines_[0].c.shape[1], self.degree, sp_version >= parse_version('1.10.0')
    if scipy_1_10:
        use_sparse , kwargs_extrapolate  = self.sparse_output, {'extrapolate': self.bsplines_[0].extrapolate}
    else:
        use_sparse , kwargs_extrapolate  = self.sparse_output and (not self.bsplines_[0].extrapolate), dict()
    n_out = self.n_features_out_ + n_features * (1 - self.include_bias)
    if X.dtype in FLOAT_DTYPES:
        dtype = X.dtype
    else:
        dtype = np.float64
    if use_sparse:
        output_list = []
    else:
        XBS = np.zeros((n_samples, n_out), dtype=dtype, order=self.order)
    for i in range(n_features):
        spl = self.bsplines_[i]
        if self.extrapolation in ("continue", "error", "periodic"):
            if self.extrapolation == "periodic":
                n = spl.t.size - spl.k - 1
                x = spl.t[spl.k] + (X[:, i] - spl.t[spl.k]) % (
                    spl.t[n] - spl.t[spl.k]
                )
            else:
                x = X[:, i]
            if use_sparse:
                XBS_sparse = BSpline.design_matrix(
                    x, spl.t, spl.k, **kwargs_extrapolate
                )
                if self.extrapolation == "periodic":
                    XBS_sparse = XBS_sparse.tolil()
                    XBS_sparse[:, :degree] += XBS_sparse[:, -degree:]
                    XBS_sparse = XBS_sparse[:, :-degree]
            else:
                XBS[:, (i * n_splines) : ((i + 1) * n_splines)] = spl(x)
        else:  
            xmin, xmax = spl.t[degree], spl.t[-degree - 1]
            f_min, f_max = spl(xmin), spl(xmax)
            mask = (xmin <= X[:, i]) & (X[:, i] <= xmax)
            if use_sparse:
                mask_inv , x  = ~mask, X[:, i].copy()
                x[mask_inv] = spl.t[self.degree]
                XBS_sparse = BSpline.design_matrix(x, spl.t, spl.k)
                if np.any(mask_inv):
                    XBS_sparse = XBS_sparse.tolil()
                    XBS_sparse[mask_inv, :] = 0
            else:
                XBS[mask, (i * n_splines) : ((i + 1) * n_splines)] = spl(X[mask, i])
        if self.extrapolation == "error":
            if (use_sparse and np.any(np.isnan(XBS_sparse.data))) or (
                not use_sparse
                and np.any(
                    np.isnan(XBS[:, (i * n_splines) : ((i + 1) * n_splines)])
                )
            ):
                raise ValueError(
                    "X contains values beyond the limits of the knots."
                )
        elif self.extrapolation == "constant":
            mask = X[:, i] < xmin
            if np.any(mask):
                if use_sparse:
                    XBS_sparse = XBS_sparse.tolil()
                    XBS_sparse[mask, :degree] = f_min[:degree]
                else:
                    XBS[mask, (i * n_splines) : (i * n_splines + degree)] = f_min[
                        :degree
                    ]
            mask = X[:, i] > xmax
            if np.any(mask):
                if use_sparse:
                    XBS_sparse = XBS_sparse.tolil()
                    XBS_sparse[mask, -degree:] = f_max[-degree:]
                else:
                    XBS[
                        mask,
                        ((i + 1) * n_splines - degree) : ((i + 1) * n_splines),
                    ] = f_max[-degree:]
        elif self.extrapolation == "linear":
            fp_min, fp_max = spl(xmin, nu=1), spl(xmax, nu=1)
            if degree <= 1:
                degree += 1
            for j in range(degree):
                mask = X[:, i] < xmin
                if np.any(mask):
                    linear_extr = f_min[j] + (X[mask, i] - xmin) * fp_min[j]
                    if use_sparse:
                        XBS_sparse = XBS_sparse.tolil()
                        XBS_sparse[mask, j] = linear_extr
                    else:
                        XBS[mask, i * n_splines + j] = linear_extr
                mask = X[:, i] > xmax
                if np.any(mask):
                    k = n_splines - 1 - j
                    linear_extr = f_max[k] + (X[mask, i] - xmax) * fp_max[k]
                    if use_sparse:
                        XBS_sparse = XBS_sparse.tolil()
                        XBS_sparse[mask, k : k + 1] = linear_extr[:, None]
                    else:
                        XBS[mask, i * n_splines + k] = linear_extr
        if use_sparse:
            if not sparse.isspmatrix_csr(XBS_sparse):
                XBS_sparse = XBS_sparse.tocsr()
            output_list.append(XBS_sparse)
    if use_sparse:
        max_int32 , all_int32  = np.iinfo(np.int32).max, True
        for mat in output_list:
            all_int32 &= mat.indices.dtype == np.int32
        if (
            sp_version < parse_version("1.9.2")
            and self.n_features_out_ > max_int32
            and all_int32
        ):
            raise ValueError(
                "In scipy versions `<1.9.2`, the function `scipy.sparse.hstack`"
                " produces negative columns when:\n1. The output shape contains"
                " `n_cols` too large to be represented by a 32bit signed"
                " integer.\n. All sub-matrices to be stacked have indices of"
                " dtype `np.int32`.\nTo avoid this error, either use a version"
                " of scipy `>=1.9.2` or alter the `SplineTransformer`"
                " transformer to produce fewer than 2^31 output features"
            )
        XBS = sparse.hstack(output_list, format="csr")
    elif self.sparse_output:
        XBS = sparse.csr_matrix(XBS)
    if self.include_bias:
        return XBS
    else:
        indices = [j for j in range(XBS.shape[1]) if (j + 1) % n_splines != 0]
        return XBS[:, indices]
