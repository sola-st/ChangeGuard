def _shallow_copy(self, values=None, **kwargs):
    if values is not None:
        names = kwargs.pop("names", kwargs.pop("name", self.names))
        return MultiIndex.from_tuples(values, names=names, **kwargs)
    result = self.copy(**kwargs)
    result._cache = self._cache.copy()
    result._cache.pop("levels", None)  
    return result
