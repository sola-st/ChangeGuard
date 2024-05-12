def _init_centroids(
    self,
    X,
    x_squared_norms,
    init,
    random_state,
    sample_weight,
    init_size=None,
    n_centroids=None,
):
    n_samples = X.shape[0]
    n_clusters = self.n_clusters if n_centroids is None else n_centroids
    if init_size is not None and init_size < n_samples:
        init_indices = random_state.randint(0, n_samples, init_size)
        X = X[init_indices]
        x_squared_norms = x_squared_norms[init_indices]
        n_samples = X.shape[0]
        sample_weight = sample_weight[init_indices]
    if isinstance(init, str) and init == "k-means++":
        centers, _ = _kmeans_plusplus(
            X,
            n_clusters,
            random_state=random_state,
            x_squared_norms=x_squared_norms,
            sample_weight=sample_weight,
        )
    elif isinstance(init, str) and init == "random":
        seeds = random_state.choice(
            n_samples,
            size=n_clusters,
            replace=False,
            p=sample_weight / sample_weight.sum(),
        )
        centers = X[seeds]
    elif _is_arraylike_not_scalar(self.init):
        centers = init
    elif callable(init):
        centers = init(X, n_clusters, random_state=random_state)
        centers = check_array(centers, dtype=X.dtype, copy=False, order="C")
        self._validate_center_shape(X, centers)
    if sp.issparse(centers):
        centers = centers.toarray()
    return centers
