def create_axes(
    self,
    axes,
    obj,
    validate = True,
    nan_rep=None,
    data_columns=None,
    min_itemsize=None,
):
    if axes is None:
        try:
            axes = _AXES_MAP[type(obj)]
        except KeyError:
            group = self.group._v_name
            raise TypeError(
                f"cannot properly create the storer for: [group->{group},"
                f"value->{type(obj)}]"
            )
    axes = [obj._get_axis_number(a) for a in axes]
    if self.infer_axes():
        existing_table = self.copy()
        existing_table.infer_axes()
        axes = [a.axis for a in existing_table.index_axes]
        data_columns = existing_table.data_columns
        nan_rep = existing_table.nan_rep
        self.encoding = existing_table.encoding
        self.errors = existing_table.errors
        self.info = copy.copy(existing_table.info)
    else:
        existing_table = None
    assert self.ndim == 2  
    if len(axes) != self.ndim - 1:
        raise ValueError(
            "currently only support ndim-1 indexers in an AppendableTable"
        )
    new_non_index_axes = []
    new_data_columns = []
    if nan_rep is None:
        nan_rep = "nan"
    idx = [x for x in [0, 1] if x not in axes][0]
    a = obj.axes[idx]
    append_axis = list(a)
    if existing_table is not None:
        indexer = len(new_non_index_axes)  
        exist_axis = existing_table.non_index_axes[indexer][1]
        if not array_equivalent(np.array(append_axis), np.array(exist_axis)):
            if array_equivalent(
                np.array(sorted(append_axis)), np.array(sorted(exist_axis))
            ):
                append_axis = exist_axis
    info = self.info.setdefault(idx, {})
    info["names"] = list(a.names)
    info["type"] = type(a).__name__
    new_non_index_axes.append((idx, append_axis))
    idx = axes[0]
    a = obj.axes[idx]
    name = obj._AXIS_NAMES[idx]
    new_index = _convert_index(name, a, self.encoding, self.errors)
    new_index.axis = idx
    new_index.set_pos(0)
    new_index.update_info(self.info)
    new_index.maybe_set_size(min_itemsize)  
    self.non_index_axes = new_non_index_axes
    new_index_axes = [new_index]
    j = len(new_index_axes)  
    assert j == 1
    assert len(new_non_index_axes) == 1
    for a in new_non_index_axes:
        obj = _reindex_axis(obj, a[0], a[1])
    def get_blk_items(mgr, blocks):
        return [mgr.items.take(blk.mgr_locs) for blk in blocks]
    transposed = new_index.axis == 1
    block_obj = self.get_object(obj, transposed)._consolidate()
    blocks = block_obj._data.blocks
    blk_items = get_blk_items(block_obj._data, blocks)
    if len(new_non_index_axes):
        axis, axis_labels = new_non_index_axes[0]
        data_columns = self.validate_data_columns(data_columns, min_itemsize)
        if len(data_columns):
            mgr = block_obj.reindex(
                Index(axis_labels).difference(Index(data_columns)), axis=axis
            )._data
            blocks = list(mgr.blocks)
            blk_items = get_blk_items(mgr, blocks)
            for c in data_columns:
                mgr = block_obj.reindex([c], axis=axis)._data
                blocks.extend(mgr.blocks)
                blk_items.extend(get_blk_items(mgr, mgr.blocks))
    if existing_table is not None:
        by_items = {
            tuple(b_items.tolist()): (b, b_items)
            for b, b_items in zip(blocks, blk_items)
        }
        new_blocks = []
        new_blk_items = []
        for ea in existing_table.values_axes:
            items = tuple(ea.values)
            try:
                b, b_items = by_items.pop(items)
                new_blocks.append(b)
                new_blk_items.append(b_items)
            except (IndexError, KeyError):
                jitems = ",".join(pprint_thing(item) for item in items)
                raise ValueError(
                    f"cannot match existing table structure for [{jitems}] "
                    "on appending data"
                )
        blocks = new_blocks
        blk_items = new_blk_items
    vaxes = []
    for i, (b, b_items) in enumerate(zip(blocks, blk_items)):
        klass = DataCol
        name = None
        if data_columns and len(b_items) == 1 and b_items[0] in data_columns:
            klass = DataIndexableCol
            name = b_items[0]
            if not (name is None or isinstance(name, str)):
                raise ValueError("cannot have non-object label DataIndexableCol")
            new_data_columns.append(name)
        if existing_table is not None and validate:
            try:
                existing_col = existing_table.values_axes[i]
            except (IndexError, KeyError):
                raise ValueError(
                    f"Incompatible appended table [{blocks}]"
                    f"with existing table [{existing_table.values_axes}]"
                )
        else:
            existing_col = None
        col = klass.create_for_block(i=i, name=name, version=self.version)
        col.values = list(b_items)
        col.set_atom(
            block=b,
            existing_col=existing_col,
            min_itemsize=min_itemsize,
            nan_rep=nan_rep,
            encoding=self.encoding,
            errors=self.errors,
            info=self.info,
        )
        col.set_pos(j)
        vaxes.append(col)
        j += 1
    self.nan_rep = nan_rep
    self.data_columns = new_data_columns
    self.values_axes = vaxes
    self.index_axes = new_index_axes
    self.validate_min_itemsize(min_itemsize)
    self.metadata = [c.name for c in self.values_axes if c.metadata is not None]
    if validate:
        self.validate(existing_table)
