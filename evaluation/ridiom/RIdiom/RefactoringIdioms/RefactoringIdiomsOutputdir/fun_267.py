def pairwise_distances_argmin(X, Y=None, axis=1, metric="euclidean",
                              chunk_x_num=None, chunk_y_num=None,
                              return_distances=False, **kwargs):
    dist_func = None
    if metric in PAIRWISE_DISTANCE_FUNCTIONS:
        dist_func = PAIRWISE_DISTANCE_FUNCTIONS[metric]
    elif not callable(metric):
        raise ValueError("'metric' must be string or a callable")
    X, Y = check_pairwise_arrays(X, Y)
    if not axis:
        X, Y = Y, X
        chunk_x_num, chunk_y_num = chunk_y_num, chunk_x_num
    if chunk_x_num is None is chunk_y_num:
        if X.shape[0] >= Y.shape[0] / 2 and Y.shape[0] >= X.shape[0] / 2:
            chunk_x_num, chunk_y_num = (7, 7)
        elif X.shape[0] > Y.shape[0]:
            chunk_x_num, chunk_y_num = (50, 1)
        else:
            chunk_x_num, chunk_y_num = (1, 50)
    if chunk_x_num is None:
        chunk_x_num = 1
    if chunk_y_num is None:
        chunk_y_num = 1
    indices , values  = np.empty(X.shape[0], dtype='int32'), np.empty(X.shape[0])
    values.fill(np.infty)
    for chunk_x in gen_even_slices(X.shape[0], chunk_x_num):
        X_chunk = X[chunk_x, :]
        for chunk_y in gen_even_slices(Y.shape[0], chunk_y_num):
            Y_chunk = Y[chunk_y, :]
            if dist_func is not None:
                if metric == 'euclidean':  
                    tvar = np.dot(X_chunk, Y_chunk.T)
                    tvar *= -2
                    tvar += (X_chunk * X_chunk).sum(axis=1)[:, np.newaxis]
                    tvar += (Y_chunk * Y_chunk).sum(axis=1)[np.newaxis, :]
                    np.maximum(tvar, 0, tvar)
                else:
                    tvar = dist_func(X_chunk, Y_chunk, **kwargs)
            else:
                tvar = np.empty((X_chunk.shape[0], Y_chunk.shape[0]),
                                dtype='float')
                for n_x in range(X_chunk.shape[0]):
                    start = 0
                    if X is Y:
                        start = n_x
                    for n_y in range(start, Y_chunk.shape[0]):
                        tvar[n_x, n_y] = metric(X_chunk[n_x], Y_chunk[n_y],
                                                **kwargs)
                        if X is Y:
                            tvar[n_y, n_x] = tvar[n_x, n_y]
            min_indices = tvar.argmin(axis=1)
            min_values = tvar[range(chunk_x.stop - chunk_x.start), min_indices]
            flags = values[chunk_x] > min_values
            indices[chunk_x] = np.where(
                flags, min_indices + chunk_y.start, indices[chunk_x])
            values[chunk_x] = np.where(
                flags, min_values, values[chunk_x])
    if return_distances:
        if metric == "euclidean" and not kwargs.get("squared", False):
            values = np.sqrt(values)
        return indices, values
    else:
        return indices
