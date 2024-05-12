def make_circles(n_samples=100, shuffle=True, noise=None, random_state=None,
        factor=.8):
    if factor > 1 or factor < 0:
        raise ValueError("'factor' has to be between 0 and 1.")
    generator , linspace  = check_random_state(random_state), np.linspace(0, 2 * np.pi, n_samples / 2 + 1)[:-1]
    outer_circ_x = np.cos(linspace)
    outer_circ_y , inner_circ_x , inner_circ_y  = np.sin(linspace), outer_circ_x * factor, outer_circ_x * factor
    X , y  = np.vstack((np.append(outer_circ_x, inner_circ_x), np.append(outer_circ_y, inner_circ_y))).T, np.hstack([np.zeros(n_samples / 2), np.ones(n_samples / 2)])
    if shuffle:
        X, y = util_shuffle(X, y, random_state=generator)
    if not noise is None:
        X += generator.normal(scale=noise, size=X.shape)
    return X, y.astype(np.int)
