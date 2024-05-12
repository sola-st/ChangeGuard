def fit(self, X, y, sample_weight=None, monitor=None):
    if not self.warm_start:
        self._clear_state()
    X, y = self._validate_data(
        X, y, accept_sparse=["csr", "csc", "coo"], dtype=DTYPE, multi_output=True
    )
    sample_weight_is_none = sample_weight is None
    sample_weight = _check_sample_weight(sample_weight, X)
    y = column_or_1d(y, warn=True)
    if is_classifier(self):
        y = self._validate_y(y, sample_weight)
    else:
        y = self._validate_y(y)
    self._check_params()
    if self.n_iter_no_change is not None:
        stratify = y if is_classifier(self) else None
        X_train, X_val, y_train, y_val, sample_weight_train, sample_weight_val = (
            train_test_split(
                X,
                y,
                sample_weight,
                random_state=self.random_state,
                test_size=self.validation_fraction,
                stratify=stratify,
            )
        )
        if is_classifier(self):
            if self._n_classes != np.unique(y_train).shape[0]:
                raise ValueError(
                    "The training data after the early stopping split "
                    "is missing some classes. Try using another random "
                    "seed."
                )
    else:
        X_train, y_train, sample_weight_train = X, y, sample_weight
        X_val = y_val = sample_weight_val = None
    if not self._is_initialized():
        self._init_state()
        if self.init_ == "zero":
            raw_predictions = np.zeros(
                shape=(X_train.shape[0], self._loss.K), dtype=np.float64
            )
        else:
            if sample_weight_is_none:
                self.init_.fit(X_train, y_train)
            else:
                msg = (
                    "The initial estimator {} does not support sample "
                    "weights.".format(self.init_.__class__.__name__)
                )
                try:
                    self.init_.fit(
                        X_train, y_train, sample_weight=sample_weight_train
                    )
                except TypeError as e:
                    if "unexpected keyword argument 'sample_weight'" in str(e):
                        raise ValueError(msg) from e
                    else:  
                        raise
                except ValueError as e:
                    if (
                        "pass parameters to specific steps of "
                        "your pipeline using the "
                        "stepname__parameter"
                        in str(e)
                    ):  
                        raise ValueError(msg) from e
                    else:  
                        raise
            raw_predictions = self._loss.get_init_raw_predictions(
                X_train, self.init_
            )
        begin_at_stage = 0
        self._rng = check_random_state(self.random_state)
    else:
        if self.n_estimators < self.estimators_.shape[0]:
            raise ValueError(
                "n_estimators=%d must be larger or equal to "
                "estimators_.shape[0]=%d when "
                "warm_start==True" % (self.n_estimators, self.estimators_.shape[0])
            )
        begin_at_stage = self.estimators_.shape[0]
        X_train = check_array(
            X_train,
            dtype=DTYPE,
            order="C",
            accept_sparse="csr",
            force_all_finite=False,
        )
        raw_predictions = self._raw_predict(X_train)
        self._resize_state()
    n_stages = self._fit_stages(
        X_train,
        y_train,
        raw_predictions,
        sample_weight_train,
        self._rng,
        X_val,
        y_val,
        sample_weight_val,
        begin_at_stage,
        monitor,
    )
    if n_stages != self.estimators_.shape[0]:
        self.estimators_ = self.estimators_[:n_stages]
        self.train_score_ = self.train_score_[:n_stages]
        if hasattr(self, "oob_improvement_"):
            self.oob_improvement_ = self.oob_improvement_[:n_stages]
            self.oob_scores_ = self.oob_scores_[:n_stages]
            self.oob_score_ = self.oob_scores_[-1]
    self.n_estimators_ = n_stages
    return self
