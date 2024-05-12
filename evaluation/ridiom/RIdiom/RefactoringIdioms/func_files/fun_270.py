def unique_labels(*lists_of_labels):
    labels = set().union(*(l.ravel() if hasattr(l, "ravel") else l
                           for l in lists_of_labels))
    return np.asarray(sorted(labels))
