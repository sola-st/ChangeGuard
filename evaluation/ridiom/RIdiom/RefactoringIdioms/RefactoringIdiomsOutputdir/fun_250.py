def cross_validate(estimator, X, y=None, *, groups=None, scoring=None, cv=None,
                   n_jobs=None, verbose=0, fit_params=None,
                   pre_dispatch='2*n_jobs', return_train_score=False,
                   return_estimator=False, error_score=np.nan):
    X, y, groups = indexable(X, y, groups)
    cv = check_cv(cv, y, classifier=is_classifier(estimator))
    scorers, _ = _check_multimetric_scoring(estimator, scoring=scoring)
    parallel = Parallel(n_jobs=n_jobs, verbose=verbose,
                        pre_dispatch=pre_dispatch)
    results = parallel(
        delayed(_fit_and_score)(
            clone(estimator), X, y, scorers, train, test, verbose, None,
            fit_params, return_train_score=return_train_score,
            return_times=True, return_estimator=return_estimator,
            error_score=error_score)
        for train, test in cv.split(X, y, groups))
    results , ret  = _aggregate_score_dicts(results), {}
    ret['fit_time'] , ret['score_time']  = results['fit_time'], results['score_time']
    if return_estimator:
        ret['estimator'] = results["estimator"]
    test_scores = _aggregate_score_dicts(results["test_scores"])
    if return_train_score:
        train_scores = _aggregate_score_dicts(results["train_scores"])
    for name in test_scores:
        ret['test_%s' % name] = test_scores[name]
        if return_train_score:
            key = 'train_%s' % name
            ret[key] = train_scores[name]
    return ret
