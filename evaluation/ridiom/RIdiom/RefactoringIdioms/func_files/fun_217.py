def _setitem_with_indexer(self, indexer, value):
    from pandas import Series
    info_axis = self.obj._info_axis_number
    take_split_path = self.obj._is_mixed_type
    if not take_split_path and self.obj._data.blocks:
        (blk,) = self.obj._data.blocks
        if 1 < blk.ndim:  
            val = list(value.values()) if isinstance(value, dict) else value
            take_split_path = not blk._can_hold_element(val)
    if isinstance(indexer, tuple) and len(indexer) == len(self.obj.axes):
        for i, ax in zip(indexer, self.obj.axes):
            if isinstance(ax, ABCMultiIndex) and not (
                is_integer(i) or com.is_null_slice(i)
            ):
                take_split_path = True
                break
    if isinstance(indexer, tuple):
        nindexer = []
        for i, idx in enumerate(indexer):
            if isinstance(idx, dict):
                key, _ = convert_missing_indexer(idx)
                if self.ndim > 1 and i == self.obj._info_axis_number:
                    len_non_info_axes = (
                        len(_ax) for _i, _ax in enumerate(self.obj.axes) if _i != i
                    )
                    if any(not l for l in len_non_info_axes):
                        if not is_list_like_indexer(value):
                            raise ValueError(
                                "cannot set a frame with no "
                                "defined index and a scalar"
                            )
                        self.obj[key] = value
                        return
                    self.obj[key] = _infer_fill_value(value)
                    new_indexer = convert_from_missing_indexer_tuple(
                        indexer, self.obj.axes
                    )
                    self._setitem_with_indexer(new_indexer, value)
                    return
                index = self.obj._get_axis(i)
                labels = index.insert(len(index), key)
                self.obj._data = self.obj.reindex(labels, axis=i)._data
                self.obj._maybe_update_cacher(clear=True)
                self.obj._is_copy = None
                nindexer.append(labels.get_loc(key))
            else:
                nindexer.append(idx)
        indexer = tuple(nindexer)
    else:
        indexer, missing = convert_missing_indexer(indexer)
        if missing:
            self._setitem_with_indexer_missing(indexer, value)
            return
    item_labels = self.obj._get_axis(info_axis)
    if take_split_path:
        assert self.ndim == 2
        assert info_axis == 1
        if not isinstance(indexer, tuple):
            indexer = _tuplify(self.ndim, indexer)
        if isinstance(value, ABCSeries):
            value = self._align_series(indexer, value)
        info_idx = indexer[info_axis]
        if is_integer(info_idx):
            info_idx = [info_idx]
        labels = item_labels[info_idx]
        if len(labels) == 1:
            item = labels[0]
            idx = indexer[0]
            plane_indexer = tuple([idx])
            lplane_indexer = length_of_indexer(plane_indexer[0], self.obj.index)
            if is_list_like_indexer(value) and 0 != lplane_indexer != len(value):
                raise ValueError(
                    "cannot set using a multi-index "
                    "selection indexer with a different "
                    "length than the value"
                )
        else:
            plane_indexer = indexer[:1]
            lplane_indexer = length_of_indexer(plane_indexer[0], self.obj.index)
        def setter(item, v):
            ser = self.obj[item]
            pi = plane_indexer[0] if lplane_indexer == 1 else plane_indexer
            if isinstance(pi, tuple) and all(
                com.is_null_slice(idx) or com.is_full_slice(idx, len(self.obj))
                for idx in pi
            ):
                ser = v
            else:
                ser._consolidate_inplace()
                ser = ser.copy()
                ser._data = ser._data.setitem(indexer=pi, value=v)
                ser._maybe_update_cacher(clear=True)
            self.obj[item] = ser
        if is_list_like_indexer(value) and getattr(value, "ndim", 1) > 0:
            if isinstance(value, ABCDataFrame):
                sub_indexer = list(indexer)
                multiindex_indexer = isinstance(labels, ABCMultiIndex)
                for item in labels:
                    if item in value:
                        sub_indexer[info_axis] = item
                        v = self._align_series(
                            tuple(sub_indexer), value[item], multiindex_indexer
                        )
                    else:
                        v = np.nan
                    setter(item, v)
            elif np.ndim(value) == 2:
                value = np.array(value, dtype=object)
                if len(labels) != value.shape[1]:
                    raise ValueError(
                        "Must have equal len keys and value "
                        "when setting with an ndarray"
                    )
                for i, item in enumerate(labels):
                    setter(item, value[:, i].tolist())
            elif _can_do_equal_len(
                labels, value, plane_indexer, lplane_indexer, self.obj
            ):
                setter(labels[0], value)
            else:
                if len(labels) != len(value):
                    raise ValueError(
                        "Must have equal len keys and value "
                        "when setting with an iterable"
                    )
                for item, v in zip(labels, value):
                    setter(item, v)
        else:
            for item in labels:
                setter(item, value)
    else:
        if isinstance(indexer, tuple):
            indexer = maybe_convert_ix(*indexer)
            if (
                len(indexer) > info_axis
                and is_integer(indexer[info_axis])
                and all(
                    com.is_null_slice(idx)
                    for i, idx in enumerate(indexer)
                    if i != info_axis
                )
                and item_labels.is_unique
            ):
                self.obj[item_labels[indexer[info_axis]]] = value
                return
        if isinstance(value, (ABCSeries, dict)):
            value = self._align_series(indexer, Series(value))
        elif isinstance(value, ABCDataFrame):
            value = self._align_frame(indexer, value)
        self.obj._check_is_chained_assignment_possible()
        self.obj._consolidate_inplace()
        self.obj._data = self.obj._data.setitem(indexer=indexer, value=value)
        self.obj._maybe_update_cacher(clear=True)
