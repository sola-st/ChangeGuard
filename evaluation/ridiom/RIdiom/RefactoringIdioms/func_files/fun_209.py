def __init__(
    self,
    data,
    precision = None,
    table_styles = None,
    uuid = None,
    caption = None,
    table_attributes = None,
    cell_ids = True,
    na_rep = None,
    uuid_len = 5,
):
    if isinstance(data, pd.Series):
        data = data.to_frame()
    if not isinstance(data, DataFrame):
        raise TypeError("``data`` must be a Series or DataFrame")
    if not data.index.is_unique or not data.columns.is_unique:
        raise ValueError("style is not supported for non-unique indices.")
    self.data = data
    self.index = data.index
    self.columns = data.columns
    if precision is None:
        precision = get_option("display.precision")
    self.precision = precision
    self.table_styles = table_styles
    if not isinstance(uuid_len, int) or not uuid_len >= 0:
        raise TypeError("``uuid_len`` must be an integer in range [0, 32].")
    self.uuid_len = min(32, uuid_len)
    self.uuid = (uuid or uuid4().hex[: self.uuid_len]) + "_"
    self.caption = caption
    self.table_attributes = table_attributes
    self.cell_ids = cell_ids
    self.na_rep = na_rep
    self.hidden_index = False
    self.hidden_columns = []
    self.ctx = defaultdict(list)
    self.cell_context = {}
    self._todo = []
    self.tooltips = None
    self._display_funcs = defaultdict(lambda: self._default_display_func)
