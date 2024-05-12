def reorder_arrays(
    arrays, arr_columns, columns, length
):
    if columns is not None:
        if not columns.equals(arr_columns):
            new_arrays , indexer  = [], arr_columns.get_indexer(columns)
            for i, k in enumerate(indexer):
                if k == -1:
                    arr = np.empty(length, dtype=object)
                    arr.fill(np.nan)
                else:
                    arr = arrays[k]
                new_arrays.append(arr)
            arrays , arr_columns  = new_arrays, columns
    return arrays, arr_columns
