def parse_format_options(s, defaults):
    value_map = {
        'true': True,
        'false': False,
    }
    options = deepcopy(defaults or {})
    for option in s.split(','):
        try:
            path, value = option.lower().split('=')
            section, key = path.split('.')
        except ValueError:
            raise argparse.ArgumentTypeError(f'invalid option {option!r}')
        if value in value_map:
            parsed_value = value_map[value]
        else:
            if value.isnumeric():
                parsed_value = int(value)
            else:
                parsed_value = value
        if defaults is None:
            options.setdefault(section, {})
        else:
            try:
                default_value = defaults[section][key]
            except KeyError:
                raise argparse.ArgumentTypeError(
                    f'invalid key {path!r}')
            default_type, parsed_type = type(default_value), type(parsed_value)
            if parsed_type is not default_type:
                raise argparse.ArgumentTypeError(
                    'invalid value'
                    f' {value!r} in {option!r}'
                    f' (expected {default_type.__name__}'
                    f' got {parsed_type.__name__})'
                )
        options[section][key] = parsed_value
    return options
