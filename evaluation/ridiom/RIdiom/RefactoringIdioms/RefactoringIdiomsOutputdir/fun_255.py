def fit(self, X, y):
    X, y = check_X_y(X, y, "csr")
    cv , scorer , n_features , n_features_to_select  = check_cv(self.cv, y, is_classifier(self.estimator)), check_scoring(self.estimator, scoring=self.scoring), X.shape[1], 1
    rfe = RFE(estimator=self.estimator,
              n_features_to_select=n_features_to_select,
              step=self.step, verbose=self.verbose - 1)
    if self.n_jobs == 1:
        parallel, func = list, _rfe_single_fit
    else:
        parallel, func, = Parallel(n_jobs=self.n_jobs), delayed(_rfe_single_fit)
    scores = parallel(
        func(rfe, self.estimator, X, y, train, test, scorer)
        for train, test in cv.split(X, y))
    scores = np.sum(scores, axis=0)
    n_features_to_select = max(
        n_features - (np.argmax(scores) * self.step),
        n_features_to_select)
    rfe = RFE(estimator=self.estimator,
              n_features_to_select=n_features_to_select, step=self.step)
    rfe.fit(X, y)
    self.support_ , self.n_features_ , self.ranking_  = rfe.support_, rfe.n_features_, rfe.ranking_
    self.estimator_ = clone(self.estimator)
    self.estimator_.fit(self.transform(X), y)
    self.grid_scores_ = scores[::-1] / cv.get_n_splits(X, y)
    return self
