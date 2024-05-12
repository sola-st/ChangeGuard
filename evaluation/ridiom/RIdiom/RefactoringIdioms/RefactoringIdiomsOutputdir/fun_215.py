def __getitem__(self, key):
    key = com.apply_if_callable(key, self)
    if key is Ellipsis:
        return self
    key_is_scalar = is_scalar(key)
    if isinstance(key, (list, tuple)):
        key = unpack_1tuple(key)
    if is_integer(key) and self.index._should_fallback_to_positional():
        return self._values[key]
    elif key_is_scalar:
        return self._get_value(key)
    if (
        isinstance(key, tuple)
        and is_hashable(key)
        and isinstance(self.index, MultiIndex)
    ):
        try:
            result = self._get_value(key)
            return result
        except KeyError:
            return self._get_values_tuple(key)
    if is_iterator(key):
        key = list(key)
    if com.is_bool_indexer(key):
        key = check_bool_indexer(self.index, key)
        key = np.asarray(key, dtype=bool)
        return self._get_values(key)
    return self._get_with(key)
