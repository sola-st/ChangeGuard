def _check_sample_weight(sample_weight, X, dtype=None):
    n_samples = _num_samples(X)
    if dtype is not None and dtype not in [np.float32, np.float64]:
        dtype = np.float64
    if sample_weight is None:
        sample_weight = np.ones(n_samples, dtype=dtype)
    elif isinstance(sample_weight, numbers.Number):
        sample_weight = np.full(n_samples, sample_weight, dtype=dtype)
    else:
        if dtype is None:
            dtype = [np.float64, np.float32]
        sample_weight = check_array(
            sample_weight, accept_sparse=False, ensure_2d=False, dtype=dtype,
            order="C"
        )
        if sample_weight.ndim != 1:
            raise ValueError("Sample weights must be 1D array or scalar")
        if sample_weight.shape != (n_samples,):
            raise ValueError("sample_weight.shape == {}, expected {}!"
                             .format(sample_weight.shape, (n_samples,)))
    return sample_weight
