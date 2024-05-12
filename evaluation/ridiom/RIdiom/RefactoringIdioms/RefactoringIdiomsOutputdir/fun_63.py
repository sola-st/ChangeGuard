def shell_command():
    import code
    banner , ctx , startup  = f'Python {sys.version} on {sys.platform}\nApp: {current_app.import_name}\nInstance: {current_app.instance_path}', {}, os.environ.get('PYTHONSTARTUP')
    if startup and os.path.isfile(startup):
        with open(startup) as f:
            eval(compile(f.read(), startup, "exec"), ctx)
    ctx.update(current_app.make_shell_context())
    interactive_hook = getattr(sys, "__interactivehook__", None)
    if interactive_hook is not None:
        try:
            import readline
            from rlcompleter import Completer
        except ImportError:
            pass
        else:
            readline.set_completer(Completer(ctx).complete)
        interactive_hook()
    code.interact(banner=banner, local=ctx)
