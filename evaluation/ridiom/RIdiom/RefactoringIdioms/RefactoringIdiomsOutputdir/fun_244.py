def _get_column_indices(X, key):
    n_columns , key_dtype  = X.shape[1], _determine_key_type(key)
    if isinstance(key, (list, tuple)) and not key:
        return []
    elif key_dtype in ("bool", "int"):
        try:
            idx = _safe_indexing(np.arange(n_columns), key)
        except IndexError as e:
            raise ValueError(
                "all features must be in [0, {}] or [-{}, 0]".format(
                    n_columns - 1, n_columns
                )
            ) from e
        return np.atleast_1d(idx).tolist()
    elif key_dtype == "str":
        try:
            all_columns = X.columns
        except AttributeError:
            raise ValueError(
                "Specifying the columns using strings is only "
                "supported for pandas DataFrames"
            )
        if isinstance(key, str):
            columns = [key]
        elif isinstance(key, slice):
            start, stop = key.start, key.stop
            if start is not None:
                start = all_columns.get_loc(start)
            if stop is not None:
                stop = all_columns.get_loc(stop) + 1
            else:
                stop = n_columns + 1
            return list(islice(range(n_columns), start, stop))
        else:
            columns = list(key)
        try:
            column_indices = []
            for col in columns:
                col_idx = all_columns.get_loc(col)
                if not isinstance(col_idx, numbers.Integral):
                    raise ValueError(
                        f"Selected columns, {columns}, are not unique in dataframe"
                    )
                column_indices.append(col_idx)
        except KeyError as e:
            raise ValueError("A given column is not a column of the dataframe") from e
        return column_indices
    else:
        raise ValueError(
            "No valid specification of the columns. Only a "
            "scalar, list or slice of all integers or all "
            "strings, or boolean mask is allowed"
        )
