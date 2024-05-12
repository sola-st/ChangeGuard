def format_file_in_place(
    src,
    fast,
    mode,
    write_back = WriteBack.NO,
    lock = None,  
):
    if src.suffix == ".pyi":
        mode = replace(mode, is_pyi=True)
    then = datetime.utcfromtimestamp(src.stat().st_mtime)
    with open(src, "rb") as buf:
        src_contents, encoding, newline = decode_bytes(buf.read())
    try:
        dst_contents = format_file_contents(src_contents, fast=fast, mode=mode)
    except NothingChanged:
        return False
    if write_back == WriteBack.YES:
        with open(src, "w", encoding=encoding, newline=newline) as f:
            f.write(dst_contents)
    elif write_back in (WriteBack.DIFF, WriteBack.COLOR_DIFF):
        now = datetime.utcnow()
        src_name = f"{src}\t{then} +0000"
        dst_name = f"{src}\t{now} +0000"
        diff_contents = diff(src_contents, dst_contents, src_name, dst_name)
        if write_back == WriteBack.COLOR_DIFF:
            diff_contents = color_diff(diff_contents)
        with lock or nullcontext():
            f = io.TextIOWrapper(
                sys.stdout.buffer,
                encoding=encoding,
                newline=newline,
                write_through=True,
            )
            f = wrap_stream_for_windows(f)
            f.write(diff_contents)
            f.detach()
    return True
