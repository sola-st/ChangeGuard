def load_svmlight_file(f, n_features=None, dtype=np.float64,
                       multilabel=False, zero_based="auto"):
    return tuple(load_svmlight_files([f], n_features, dtype, multilabel, zero_based))
