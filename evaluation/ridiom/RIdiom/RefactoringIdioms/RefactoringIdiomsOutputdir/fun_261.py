def fit(self, X, y):
    if self.strategy not in ("mean", "median", "constant"):
        raise ValueError("Unknown strategy type: %s, expected 'mean, 'median' or 'constant'"
                         % self.strategy)
    y = safe_asarray(y)
    self.output_2d_ = (y.ndim == 2)
    if self.strategy == "mean":
        self.constant_ = np.reshape(np.mean(y, axis=0), (1, -1))
    elif self.strategy == "median":
        self.constant_ = np.reshape(np.median(y, axis=0), (1, -1))
    elif self.strategy == "constant":
        if self.constant is None:
            raise TypeError("Constant target value has to be specified "
                            "when the constant strategy is used.")
        self.constant = safe_asarray(self.constant)
        if self.output_2d_ and self.constant.shape[0] != y.shape[1]:
            raise ValueError(
                    "Constant target value should have "
                                 "shape (%d, 1)." % y.shape[1])
        self.constant_ = np.reshape(self.constant, (1, -1))
    self.n_outputs_ = np.size(self.constant_)  
    return self
