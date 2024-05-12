def _body_from_file(self, fd):
    if self.args.data:
        self.error('Request body (from stdin or a file) and request '
                   'data (key=value) cannot be mixed. Pass '
                   '--ignore-stdin to let key/value take priority.')
    self.args.data = getattr(fd, 'buffer', fd).read()
