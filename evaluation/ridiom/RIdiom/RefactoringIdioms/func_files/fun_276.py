def fit(self, X, y=None):
    if self.use_idf:
        n_samples, n_features = X.shape
        df = np.bincount(X.nonzero()[1])
        self.idf_ = np.log(float(X.shape[0]) / df)
    return self
