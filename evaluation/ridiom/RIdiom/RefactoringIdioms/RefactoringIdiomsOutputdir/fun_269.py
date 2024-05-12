def fit(self, X, y):
    X, y = check_arrays(X, y, sparse_format="csr")
    rfe , cv , scores  = RFE(estimator=self.estimator, n_features_to_select=1, step=self.step, estimator_params=self.estimator_params, verbose=self.verbose - 1), check_cv(self.cv, X, y, is_classifier(self.estimator)), np.zeros(X.shape[1])
    for n, (train, test) in enumerate(cv):
        X_train, X_test = X[train], X[test]
        y_train, y_test = y[train], y[test]
        ranking_ = rfe.fit(X_train, y_train).ranking_
        for k in range(0, max(ranking_)):
            mask , estimator  = np.where(ranking_ <= k + 1)[0], clone(self.estimator)
            estimator.fit(X_train[:, mask], y_train)
            if self.loss_func is None:
                loss_k = 1.0 - estimator.score(X_test[:, mask], y_test)
            else:
                loss_k = self.loss_func(
                    y_test, estimator.predict(X_test[:, mask]))
            if self.verbose > 0:
                print("Finished fold with %d / %d feature ranks, loss=%f"
                      % (k, max(ranking_), loss_k))
            scores[k] += loss_k
    best_score , best_k  = np.inf, None
    for k, score in enumerate(scores):
        if score < best_score:
            best_score , best_k  = score, k + 1
    rfe = RFE(estimator=self.estimator,
              n_features_to_select=best_k,
              step=self.step, estimator_params=self.estimator_params)
    rfe.fit(X, y)
    self.support_ , self.n_features_ , self.ranking_  = rfe.support_, rfe.n_features_, rfe.ranking_
    self.estimator_ = clone(self.estimator)
    self.estimator_.set_params(**self.estimator_params)
    self.estimator_.fit(self.transform(X), y)
    self.cv_scores_ = scores / n
    return self
