def connections_export(args):
    file_formats = [".yaml", ".json", ".env"]
    if args.format:
        warnings.warn("Option `--format` is deprecated.  Use `--file-format` instead.", DeprecationWarning)
    if args.format and args.file_format:
        raise SystemExit("Option `--format` is deprecated.  Use `--file-format` instead.")
    default_format = ".json"
    provided_file_format = None
    if args.format or args.file_format:
        provided_file_format = f".{(args.format or args.file_format).lower()}"
    with args.file as f:
        if file_is_stdout := is_stdout(f):
            filetype = provided_file_format or default_format
        elif provided_file_format:
            filetype = provided_file_format
        else:
            filetype = Path(args.file.name).suffix.lower()
            if filetype not in file_formats:
                raise SystemExit(
                    f"Unsupported file format. The file must have the extension {', '.join(file_formats)}."
                )
        if args.serialization_format and filetype != ".env":
            raise SystemExit("Option `--serialization-format` may only be used with file type `env`.")
        with create_session() as session:
            connections = session.scalars(select(Connection).order_by(Connection.conn_id)).all()
        msg = _format_connections(
            conns=connections,
            file_format=filetype,
            serialization_format=args.serialization_format or "uri",
        )
        f.write(msg)
    if file_is_stdout:
        print(f"\n{len(connections)} connections successfully exported.", file=sys.stderr)
    else:
        print(f"{len(connections)} connections successfully exported to {args.file.name}.")
