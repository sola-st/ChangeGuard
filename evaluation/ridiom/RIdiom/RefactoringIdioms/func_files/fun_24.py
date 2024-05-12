def path_empty(
    src, msg, quiet, verbose, ctx
):
    if not src:
        if verbose or not quiet:
            out(msg)
        ctx.exit(0)
