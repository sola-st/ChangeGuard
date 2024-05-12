def __call__(self, parser, namespace, values, option_string=None):
    value = str(values).encode("utf-8").decode("utf-8")
    value = value[1::] if re.match(r"^\$(.+)", value) else value
    setattr(namespace, self.dest, value)
