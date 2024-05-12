def __iter__(self):
    rng = check_random_state(self.random_state)
    cls_count = np.bincount(np.unique(self.y, return_inverse=True)[1])
    p_i = cls_count / float(self.n)
    n_i = np.round(self.n_train * p_i).astype('int')
    t_i = np.minimum(cls_count - n_i,
                     np.round(self.n_test * p_i).astype('int'))
    for n in range(self.n_iterations):
        train = []
        test = []
        for i, cls in enumerate(np.unique(self.y)):
            permutation = rng.permutation(n_i[i] + t_i[i])
            cls_i = np.where((self.y == cls))[0][permutation]
            train.extend(cls_i[:n_i[i]])
            test.extend(cls_i[n_i[i]:n_i[i] + t_i[i]])
        train = rng.permutation(train)
        test = rng.permutation(test)
        if self.indices:
            yield train, test
        else:
            train_m = np.zeros(self.n, dtype='bool')
            test_m = np.zeros(self.n, dtype='bool')
            train_m[train] = True
            test_m[test] = True
            yield train_m, test_m
