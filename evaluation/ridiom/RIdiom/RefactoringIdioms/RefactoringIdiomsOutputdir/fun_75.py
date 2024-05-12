def __call__(self, *args, **kwargs):
    plot_backend = _get_plot_backend(kwargs.pop("backend", None))
    x, y, kind, kwargs = self._get_call_args(
        plot_backend.__name__, self._parent, args, kwargs
    )
    kind = self._kind_aliases.get(kind, kind)
    if plot_backend.__name__ != "pandas.plotting._matplotlib":
        return plot_backend.plot(self._parent, x=x, y=y, kind=kind, **kwargs)
    if kind not in self._all_kinds:
        raise ValueError(
            f"{kind} is not a valid plot kind "
            f"Valid plot kinds: {self._all_kinds}"
        )
    data = self._parent.copy()
    if isinstance(data, ABCSeries):
        kwargs["reuse_plot"] = True
    if kind in self._dataframe_kinds:
        if isinstance(data, ABCDataFrame):
            return plot_backend.plot(data, x=x, y=y, kind=kind, **kwargs)
        else:
            raise ValueError(f"plot kind {kind} can only be used for data frames")
    elif kind in self._series_kinds:
        if isinstance(data, ABCDataFrame):
            if y is None and kwargs.get("subplots") is False:
                raise ValueError(
                    f"{kind} requires either y column or 'subplots=True'"
                )
            if y is not None:
                if is_integer(y) and not data.columns._holds_integer():
                    y = data.columns[y]
                data = data[y].copy()
                data.index.name = y
    elif isinstance(data, ABCDataFrame):
        data_cols = data.columns
        if x is not None:
            if is_integer(x) and not data.columns._holds_integer():
                x = data_cols[x]
            elif not isinstance(data[x], ABCSeries):
                raise ValueError("x must be a label or position")
            data = data.set_index(x)
        if y is not None:
            int_ylist = is_list_like(y) and all(is_integer(c) for c in y)
            int_y_arg = is_integer(y) or int_ylist
            if int_y_arg and not data.columns._holds_integer():
                y = data_cols[y]
            label_kw = kwargs["label"] if "label" in kwargs else False
            for kw in ["xerr", "yerr"]:
                if kw in kwargs and (
                    isinstance(kwargs[kw], str) or is_integer(kwargs[kw])
                ):
                    try:
                        kwargs[kw] = data[kwargs[kw]]
                    except (IndexError, KeyError, TypeError):
                        pass
            data = data[y].copy()
            if isinstance(data, ABCSeries):
                label_name = label_kw or y
                data.name = label_name
            else:
                match = is_list_like(label_kw) and len(label_kw) == len(y)
                if label_kw and not match:
                    raise ValueError(
                        "label should be list-like and same length as y"
                    )
                label_name = label_kw or data.columns
                data.columns = label_name
    return plot_backend.plot(data, kind=kind, **kwargs)
