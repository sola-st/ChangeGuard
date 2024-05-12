def _update_terminal_region(self, tree, terminal_regions, leaf, X, y,
                            residual, pred):
    terminal_region = np.where(terminal_regions == leaf)[0]
    residual = residual.take(terminal_region, axis=0)
    y = y.take(terminal_region, axis=0)
    numerator = residual.sum()
    denominator = np.dot(y - residual, 1 - y + residual)
    if denominator == 0.0:
        tree.value[leaf, 0, 0] = 0.0
    else:
        tree.value[leaf, 0, 0] = numerator / denominator
