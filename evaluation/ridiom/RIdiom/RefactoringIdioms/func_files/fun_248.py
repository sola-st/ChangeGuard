def make_s_curve(n_samples=100, *, noise=0.0, random_state=None):
    generator = check_random_state(random_state)
    t = 3 * np.pi * (generator.uniform(size=(1, n_samples)) - 0.5)
    X = np.empty(shape=(n_samples, 3), dtype=np.float64)
    X[:, 0] = np.sin(t)
    X[:, 1] = 2.0 * generator.uniform(size=n_samples)
    X[:, 2] = np.sign(t) * (np.cos(t) - 1)
    X += noise * generator.standard_normal(size=(3, n_samples)).T
    t = np.squeeze(t)
    return X, t
