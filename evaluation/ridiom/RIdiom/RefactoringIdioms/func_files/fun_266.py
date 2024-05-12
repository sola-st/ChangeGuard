def pairwise_distances_argmin_min(X, Y, axis=1, metric="euclidean",
                                  batch_size=500, metric_kwargs={}):
    dist_func = None
    if metric in PAIRWISE_DISTANCE_FUNCTIONS:
        dist_func = PAIRWISE_DISTANCE_FUNCTIONS[metric]
    elif not callable(metric) and not isinstance(metric, str):
        raise ValueError("'metric' must be a string or a callable")
    X, Y = check_pairwise_arrays(X, Y)
    if axis == 0:
        X, Y = Y, X
    indices = np.empty(X.shape[0], dtype='int32')
    values = np.empty(X.shape[0])
    values.fill(np.infty)
    for chunk_x in gen_batches(X.shape[0], batch_size):
        X_chunk = X[chunk_x, :]
        for chunk_y in gen_batches(Y.shape[0], batch_size):
            Y_chunk = Y[chunk_y, :]
            if dist_func is not None:
                if metric == 'euclidean':  
                    dist_chunk = np.dot(X_chunk, Y_chunk.T)
                    dist_chunk *= -2
                    dist_chunk += (X_chunk * X_chunk
                                   ).sum(axis=1)[:, np.newaxis]
                    dist_chunk += (Y_chunk * Y_chunk
                                   ).sum(axis=1)[np.newaxis, :]
                    np.maximum(dist_chunk, 0, dist_chunk)
                else:
                    dist_chunk = dist_func(X_chunk, Y_chunk, **metric_kwargs)
            else:
                dist_chunk = pairwise_distances(X_chunk, Y_chunk,
                                                metric=metric, **metric_kwargs)
            min_indices = dist_chunk.argmin(axis=1)
            min_values = dist_chunk[np.arange(chunk_x.stop - chunk_x.start),
                                    min_indices]
            flags = values[chunk_x] > min_values
            indices[chunk_x] = np.where(
                flags, min_indices + chunk_y.start, indices[chunk_x])
            values[chunk_x] = np.where(
                flags, min_values, values[chunk_x])
    if metric == "euclidean" and not metric_kwargs.get("squared", False):
        values = np.sqrt(values)
    return indices, values
