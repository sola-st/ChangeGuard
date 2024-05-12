def bincount(x, weights=None, minlength=None):
    if len(x) > 0:
        return np.bincount(x, weights, minlength)
    else:
        if minlength is None:
            minlength = 0
        minlength = np.asscalar(np.asarray(minlength, dtype=np.intp))
        return np.zeros(minlength, dtype=np.intp)
