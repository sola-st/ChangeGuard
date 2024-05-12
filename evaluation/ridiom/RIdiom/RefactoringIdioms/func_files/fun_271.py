def make_circles(n_samples=100, shuffle=True, noise=None, random_state=None,
        factor=.8):
    if factor > 1 or factor < 0:
        raise ValueError("'factor' has to be between 0 and 1.")
    generator = check_random_state(random_state)
    linspace = np.linspace(0, 2 * np.pi, n_samples / 2 + 1)[:-1]
    outer_circ_x = np.cos(linspace)
    outer_circ_y = np.sin(linspace)
    inner_circ_x = outer_circ_x * factor
    inner_circ_y = outer_circ_x * factor
    X = np.vstack((np.append(outer_circ_x, inner_circ_x),\
           np.append(outer_circ_y, inner_circ_y))).T
    y = np.hstack([np.zeros(n_samples / 2), np.ones(n_samples / 2)])
    if shuffle:
        X, y = util_shuffle(X, y, random_state=generator)
    if not noise is None:
        X += generator.normal(scale=noise, size=X.shape)
    return X, y.astype(np.int)
