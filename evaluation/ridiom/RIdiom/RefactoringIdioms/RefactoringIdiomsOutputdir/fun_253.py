def _fit_stage(self, i, X, y, y_pred, sample_weight, sample_mask,
               random_state, X_idx_sorted, X_csc=None, X_csr=None):
    assert sample_mask.dtype == np.bool
    loss , original_y  = self.loss_, y
    for k in range(loss.K):
        if loss.is_multi_class:
            y = np.array(original_y == k, dtype=np.float64)
        residual , tree  = loss.negative_gradient(y, y_pred, k=k, sample_weight=sample_weight), DecisionTreeRegressor(criterion=self.criterion, splitter='best', max_depth=self.max_depth, min_samples_split=self.min_samples_split, min_samples_leaf=self.min_samples_leaf, min_weight_fraction_leaf=self.min_weight_fraction_leaf, min_impurity_decrease=self.min_impurity_decrease, min_impurity_split=self.min_impurity_split, max_features=self.max_features, max_leaf_nodes=self.max_leaf_nodes, random_state=random_state, presort=self.presort)
        if self.subsample < 1.0:
            sample_weight = sample_weight * sample_mask.astype(np.float64)
        X = X_csr if X_csr is not None else X
        tree.fit(X, residual, sample_weight=sample_weight,
                 check_input=False, X_idx_sorted=X_idx_sorted)
        loss.update_terminal_regions(tree.tree_, X, y, residual, y_pred,
                                     sample_weight, sample_mask,
                                     self.learning_rate, k=k)
        self.estimators_[i, k] = tree
    return y_pred
