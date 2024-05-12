def main(as_module=False):
    args = sys.argv[1:]
    if as_module:
        this_module = 'flask'
        if sys.version_info < (2, 7):
            this_module += '.cli'
        name , sys.argv  = 'python -m ' + this_module, ['-m', this_module] + args
    else:
        name = None
    cli.main(args=args, prog_name=name)
