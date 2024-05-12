def _read(
    filepath_or_buffer, kwds
):
    if kwds.get("parse_dates", None) is None:
        if kwds.get("date_parser", None) is None:
            kwds["parse_dates"] = False
        else:
            kwds["parse_dates"] = True
    iterator , chunksize  = kwds.get('iterator', False), kwds.get('chunksize', None)
    if kwds.get("engine") == "pyarrow":
        if iterator:
            raise ValueError(
                "The 'iterator' option is not supported with the 'pyarrow' engine"
            )
        if chunksize is not None:
            raise ValueError(
                "The 'chunksize' option is not supported with the 'pyarrow' engine"
            )
    else:
        chunksize = validate_integer("chunksize", chunksize, 1)
    nrows = kwds.get("nrows", None)
    _validate_names(kwds.get("names", None))
    parser = TextFileReader(filepath_or_buffer, **kwds)
    if chunksize or iterator:
        return parser
    with parser:
        return parser.read(nrows)
