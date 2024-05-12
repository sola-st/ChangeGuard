def jsonify(*args, **kwargs):
    indent = None
    separators = (',', ':')
    if current_app.config['JSONIFY_PRETTYPRINT_REGULAR'] or current_app.debug:
        indent = 2
        separators = (', ', ': ')
    if args and kwargs:
        raise TypeError('jsonify() behavior undefined when passed both args and kwargs')
    elif len(args) == 1:  
        data = args[0]
    else:
        data = args or kwargs
    return current_app.response_class(
        dumps(data, indent=indent, separators=separators) + '\n',
        mimetype=current_app.config['JSONIFY_MIMETYPE']
    )
