def __contains__(self, other):
    if super().__contains__(other):
        return True
    return is_float(other) and np.isnan(other) and self.hasnans
