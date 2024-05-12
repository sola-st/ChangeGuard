def apply_standard(self):
    func = cast(Callable, self.func)
    obj = self.obj
    if isinstance(func, np.ufunc):
        with np.errstate(all="ignore"):
            return func(obj, *self.args, **self.kwargs)
    elif not self.by_row:
        return func(obj, *self.args, **self.kwargs)
    if self.args or self.kwargs:
        def curried(x):
            return func(x, *self.args, **self.kwargs)
    else:
        curried = func
    action = "ignore" if isinstance(obj.dtype, CategoricalDtype) else None
    mapped = obj._map_values(
        mapper=curried, na_action=action, convert=self.convert_dtype
    )
    if len(mapped) and isinstance(mapped[0], ABCSeries):
        warnings.warn(
            "Returning a DataFrame from Series.apply when the supplied function "
            "returns a Series is deprecated and will be removed in a future "
            "version.",
            FutureWarning,
            stacklevel=find_stack_level(),
        )  
        return obj._constructor_expanddim(list(mapped), index=obj.index)
    else:
        return obj._constructor(mapped, index=obj.index).__finalize__(
            obj, method="apply"
        )
