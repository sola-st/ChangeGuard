def get_sources(
    *,
    ctx,
    src,
    quiet,
    verbose,
    include,
    exclude,
    extend_exclude,
    force_exclude,
    report,
    stdin_filename,
):
    sources , root  = set(), ctx.obj['root']
    for s in src:
        if s == "-" and stdin_filename:
            p , is_stdin  = Path(stdin_filename), True
        else:
            p , is_stdin  = Path(s), False
        if is_stdin or p.is_file():
            normalized_path = normalize_path_maybe_ignore(p, ctx.obj["root"], report)
            if normalized_path is None:
                continue
            normalized_path = "/" + normalized_path
            if force_exclude:
                force_exclude_match = force_exclude.search(normalized_path)
            else:
                force_exclude_match = None
            if force_exclude_match and force_exclude_match.group(0):
                report.path_ignored(p, "matches the --force-exclude regular expression")
                continue
            if is_stdin:
                p = Path(f"{STDIN_PLACEHOLDER}{str(p)}")
            if p.suffix == ".ipynb" and not jupyter_dependencies_are_installed(
                verbose=verbose, quiet=quiet
            ):
                continue
            sources.add(p)
        elif p.is_dir():
            if exclude is None:
                exclude , gitignore  = re_compile_maybe_verbose(DEFAULT_EXCLUDES), get_gitignore(root)
            else:
                gitignore = None
            sources.update(
                gen_python_files(
                    p.iterdir(),
                    ctx.obj["root"],
                    include,
                    exclude,
                    extend_exclude,
                    force_exclude,
                    report,
                    gitignore,
                    verbose=verbose,
                    quiet=quiet,
                )
            )
        elif s == "-":
            sources.add(p)
        else:
            err(f"invalid path: {s}")
    return sources
