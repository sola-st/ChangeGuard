def _rescale_data(X, y, sample_weight):
    n_samples = X.shape[0]
    sample_weight = sample_weight * np.ones(n_samples)
    sample_weight = np.sqrt(sample_weight)
    sw_matrix = sparse.dia_matrix((sample_weight, 0),
                                  shape=(n_samples, n_samples))
    X = safe_sparse_dot(sw_matrix, X)
    y = safe_sparse_dot(sw_matrix, y)
    return X, y
