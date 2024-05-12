def main(
    ctx,
    line_length,
    check,
    diff,
    fast,
    pyi,
    py36,
    skip_string_normalization,
    quiet,
    include,
    exclude,
    src,
):
    sources = []
    try:
        include_regex = re.compile(include)
    except re.error:
        err(f"Invalid regular expression for include given: {include!r}")
        ctx.exit(2)
    try:
        exclude_regex = re.compile(exclude)
    except re.error:
        err(f"Invalid regular expression for exclude given: {exclude!r}")
        ctx.exit(2)
    root = find_project_root(src)
    for s in src:
        p = Path(s)
        if p.is_dir():
            sources.extend(
                gen_python_files_in_dir(p, root, include_regex, exclude_regex)
            )
        elif p.is_file() or s == "-":
            sources.append(p)
        else:
            err(f"invalid path: {s}")
    if check and not diff:
        write_back = WriteBack.NO
    elif diff:
        write_back = WriteBack.DIFF
    else:
        write_back = WriteBack.YES
    mode = FileMode.AUTO_DETECT
    if py36:
        mode |= FileMode.PYTHON36
    if pyi:
        mode |= FileMode.PYI
    if skip_string_normalization:
        mode |= FileMode.NO_STRING_NORMALIZATION
    report = Report(check=check, quiet=quiet)
    if len(sources) == 0:
        out("No paths given. Nothing to do 😴")
        ctx.exit(0)
        return
    elif len(sources) == 1:
        reformat_one(
            src=sources[0],
            line_length=line_length,
            fast=fast,
            write_back=write_back,
            mode=mode,
            report=report,
        )
    else:
        loop = asyncio.get_event_loop()
        executor = ProcessPoolExecutor(max_workers=os.cpu_count())
        try:
            loop.run_until_complete(
                schedule_formatting(
                    sources=sources,
                    line_length=line_length,
                    fast=fast,
                    write_back=write_back,
                    mode=mode,
                    report=report,
                    loop=loop,
                    executor=executor,
                )
            )
        finally:
            shutdown(loop)
        if not quiet:
            out("All done! ✨ 🍰 ✨")
            click.echo(str(report))
    ctx.exit(report.return_code)
