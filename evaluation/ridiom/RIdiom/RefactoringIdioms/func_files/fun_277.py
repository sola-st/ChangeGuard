def euclidean_distances(X, Y, Y_norm_squared=None, squared=False):
    if X is Y:
        X = Y = safe_asanyarray(X)
    else:
        X = safe_asanyarray(X)
        Y = safe_asanyarray(Y)
    if X.shape[1] != Y.shape[1]:
        raise ValueError("Incompatible dimension for X and Y matrices")
    if issparse(X):
        XX = X.multiply(X).sum(axis=1)
    else:
        XX = np.sum(X * X, axis=1)[:, np.newaxis]
    if X is Y:  
        YY = XX.T
    elif Y_norm_squared is None:
        if issparse(Y):
            YY = Y.copy() if isinstance(Y, csr_matrix) else Y.tocsr()
            YY.data **= 2
            YY = np.asarray(YY.sum(axis=1)).T
        else:
            YY = np.sum(Y ** 2, axis=1)[np.newaxis, :]
    else:
        YY = atleast2d_or_csr(Y_norm_squared)
        if YY.shape != (1, Y.shape[0]):
            raise ValueError(
                        "Incompatible dimensions for Y and Y_norm_squared")
    distances = safe_sparse_dot(X, Y.T)
    distances *= -2
    if issparse(distances):
        distances = distances.toarray()
    distances += XX
    distances += YY
    distances = np.maximum(distances, 0)
    return distances if squared else np.sqrt(distances)
