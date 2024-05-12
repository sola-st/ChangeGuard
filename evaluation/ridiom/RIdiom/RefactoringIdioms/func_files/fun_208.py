def _translate(self):
    ROW_HEADING_CLASS = "row_heading"
    COL_HEADING_CLASS = "col_heading"
    INDEX_NAME_CLASS = "index_name"
    DATA_CLASS = "data"
    BLANK_CLASS = "blank"
    BLANK_VALUE = "&nbsp;"
    ctx = self.ctx  
    cell_context = self.cell_context  
    cellstyle_map = defaultdict(list)
    hidden_index = self.hidden_index
    hidden_columns = self.hidden_columns
    d = {
        "uuid": self.uuid,
        "table_styles": _format_table_styles(self.table_styles or []),
        "caption": self.caption,
    }
    idx_lengths = _get_level_lengths(self.index)
    col_lengths = _get_level_lengths(self.columns, hidden_columns)
    n_rlvls = self.data.index.nlevels
    n_clvls = self.data.columns.nlevels
    rlabels = self.data.index.tolist()
    clabels = self.data.columns.tolist()
    if n_rlvls == 1:
        rlabels = [[x] for x in rlabels]
    if n_clvls == 1:
        clabels = [[x] for x in clabels]
    clabels = list(zip(*clabels))
    head = []
    for r in range(n_clvls):
        row_es = [
            {
                "type": "th",
                "value": BLANK_VALUE,
                "display_value": BLANK_VALUE,
                "is_visible": not hidden_index,
                "class": " ".join([BLANK_CLASS]),
            }
        ] * (n_rlvls - 1)
        name = self.data.columns.names[r]
        cs = [
            BLANK_CLASS if name is None else INDEX_NAME_CLASS,
            f"level{r}",
        ]
        name = BLANK_VALUE if name is None else name
        row_es.append(
            {
                "type": "th",
                "value": name,
                "display_value": name,
                "class": " ".join(cs),
                "is_visible": not hidden_index,
            }
        )
        if clabels:
            for c, value in enumerate(clabels[r]):
                es = {
                    "type": "th",
                    "value": value,
                    "display_value": value,
                    "class": f"{COL_HEADING_CLASS} level{r} col{c}",
                    "is_visible": _is_visible(c, r, col_lengths),
                }
                colspan = col_lengths.get((r, c), 0)
                if colspan > 1:
                    es["attributes"] = f'colspan="{colspan}"'
                row_es.append(es)
            head.append(row_es)
    if (
        self.data.index.names
        and com.any_not_none(*self.data.index.names)
        and not hidden_index
    ):
        index_header_row = []
        for c, name in enumerate(self.data.index.names):
            cs = [INDEX_NAME_CLASS, f"level{c}"]
            name = "" if name is None else name
            index_header_row.append(
                {"type": "th", "value": name, "class": " ".join(cs)}
            )
        index_header_row.extend(
            [
                {
                    "type": "th",
                    "value": BLANK_VALUE,
                    "class": " ".join([BLANK_CLASS, f"col{c}"]),
                }
                for c in range(len(clabels[0]))
                if c not in hidden_columns
            ]
        )
        head.append(index_header_row)
    d.update({"head": head})
    body = []
    for r, row_tup in enumerate(self.data.itertuples()):
        row_es = []
        for c, value in enumerate(rlabels[r]):
            rid = [
                ROW_HEADING_CLASS,
                f"level{c}",
                f"row{r}",
            ]
            es = {
                "type": "th",
                "is_visible": (_is_visible(r, c, idx_lengths) and not hidden_index),
                "value": value,
                "display_value": value,
                "id": "_".join(rid[1:]),
                "class": " ".join(rid),
            }
            rowspan = idx_lengths.get((c, r), 0)
            if rowspan > 1:
                es["attributes"] = f'rowspan="{rowspan}"'
            row_es.append(es)
        for c, value in enumerate(row_tup[1:]):
            formatter = self._display_funcs[(r, c)]
            row_dict = {
                "type": "td",
                "value": value,
                "display_value": formatter(value),
                "is_visible": (c not in hidden_columns),
                "attributes": "",
            }
            props = []
            if self.cell_ids or (r, c) in ctx:
                row_dict["id"] = f"row{r}_col{c}"
                props.extend(ctx[r, c])
            cls = ""
            if (r, c) in cell_context:
                cls = " " + cell_context[r, c]
            row_dict["class"] = f"{DATA_CLASS} row{r} col{c}{cls}"
            row_es.append(row_dict)
            if props:  
                cellstyle_map[tuple(props)].append(f"row{r}_col{c}")
        body.append(row_es)
    d.update({"body": body})
    cellstyle = [
        {"props": list(props), "selectors": selectors}
        for props, selectors in cellstyle_map.items()
    ]
    d.update({"cellstyle": cellstyle})
    table_attr = self.table_attributes
    use_mathjax = get_option("display.html.use_mathjax")
    if not use_mathjax:
        table_attr = table_attr or ""
        if 'class="' in table_attr:
            table_attr = table_attr.replace('class="', 'class="tex2jax_ignore ')
        else:
            table_attr += ' class="tex2jax_ignore"'
    d.update({"table_attributes": table_attr})
    if self.tooltips:
        d = self.tooltips._translate(self.data, self.uuid, d)
    return d
