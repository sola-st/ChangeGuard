def transform(self, X):
    X_ordinal, X_known_mask = self._transform(
        X, handle_unknown="ignore", force_all_finite="allow-nan"
    )
    X_out = np.empty_like(X_ordinal, dtype=np.float64)
    self._transform_X_ordinal(
        X_out,
        X_ordinal,
        ~X_known_mask,
        slice(None),
        self.encodings_,
        self.target_mean_,
    )
    return X_out
