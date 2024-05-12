def _align_series(
    self,
    other,
    join="outer",
    axis=None,
    level=None,
    copy = True,
    fill_value=None,
    method=None,
    limit=None,
    fill_axis=0,
):
    is_series = isinstance(self, ABCSeries)
    if (not is_series and axis is None) or axis not in [None, 0, 1]:
        raise ValueError("Must specify axis=0 or 1")
    if is_series and axis == 1:
        raise ValueError("cannot align series to a series other than axis 0")
    if not axis:
        if self.index.equals(other.index):
            join_index, lidx, ridx = None, None, None
        else:
            join_index, lidx, ridx = self.index.join(
                other.index, how=join, level=level, return_indexers=True
            )
        if is_series:
            left = self._reindex_indexer(join_index, lidx, copy)
        elif lidx is None or join_index is None:
            left = self.copy() if copy else self
        else:
            left = self._constructor(
                self._mgr.reindex_indexer(join_index, lidx, axis=1, copy=copy)
            )
        right = other._reindex_indexer(join_index, ridx, copy)
    else:
        fdata = self._mgr
        join_index = self.axes[1]
        lidx, ridx = None, None
        if not join_index.equals(other.index):
            join_index, lidx, ridx = join_index.join(
                other.index, how=join, level=level, return_indexers=True
            )
        if lidx is not None:
            bm_axis = self._get_block_manager_axis(1)
            fdata = fdata.reindex_indexer(join_index, lidx, axis=bm_axis)
        if copy and fdata is self._mgr:
            fdata = fdata.copy()
        left = self._constructor(fdata)
        if ridx is None:
            right = other
        else:
            right = other.reindex(join_index, level=level)
    fill_na = notna(fill_value) or (method is not None)
    if fill_na:
        left = left.fillna(fill_value, method=method, limit=limit, axis=fill_axis)
        right = right.fillna(fill_value, method=method, limit=limit)
    if is_series or (not is_series and axis == 0):
        left, right = _align_as_utc(left, right, join_index)
    return (
        left.__finalize__(self),
        right.__finalize__(other),
    )
