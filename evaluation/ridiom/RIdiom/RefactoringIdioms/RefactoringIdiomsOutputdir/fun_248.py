def make_s_curve(n_samples=100, *, noise=0.0, random_state=None):
    generator = check_random_state(random_state)
    t , X  = 3 * np.pi * (generator.uniform(size=(1, n_samples)) - 0.5), np.empty(shape=(n_samples, 3), dtype=np.float64)
    X[:, 0] , X[:, 1] , X[:, 2]  = np.sin(t), 2.0 * generator.uniform(size=n_samples), np.sign(t) * (np.cos(t) - 1)
    X += noise * generator.standard_normal(size=(3, n_samples)).T
    t = np.squeeze(t)
    return X, t
