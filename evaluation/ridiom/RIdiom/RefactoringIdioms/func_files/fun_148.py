def __call__(self, parser, namespace, values, option_string=None):
    value = str(values)
    if value.startswith("$"):
        value = value[1:]
    setattr(namespace, self.dest, value)
