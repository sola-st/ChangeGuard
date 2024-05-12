def wrapper(*args, **kwargs):
    bound_args = function_signature.bind(*args, **kwargs)
    if 'wildcard_key' in bound_args.arguments:
        key_name = 'wildcard_key'
    elif 'key' in bound_args.arguments:
        key_name = 'key'
    else:
        raise ValueError('Missing key parameter!')
    if 'bucket_name' not in bound_args.arguments:
        bound_args.arguments['bucket_name'], bound_args.arguments[key_name] = S3Hook.parse_s3_url(
            bound_args.arguments[key_name]
        )
    return func(*bound_args.args, **bound_args.kwargs)
