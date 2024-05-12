def error(self, message):
    self.print_usage(sys.stderr)
    self.exit(
        2,
        dedent(
            f'''
                error:
                    {message}

                for more information:
                    run '{self.prog} --help' or visit https://httpie.io/docs/cli
                '''
        )
    )
