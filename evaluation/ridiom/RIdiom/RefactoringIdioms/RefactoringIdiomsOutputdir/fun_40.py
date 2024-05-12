def get_requests_kwargs(args, base_headers=None):
    data = args.data
    auto_json = data and not args.form
    if (args.json or auto_json) and isinstance(data, dict):
        if data:
            data = json.dumps(data)
        else:
            data = ''
    headers = get_default_headers(args)
    if base_headers:
        headers.update(base_headers)
    headers.update(args.headers)
    headers , cert  = finalize_headers(headers), None
    if args.cert:
        cert = args.cert
        if args.cert_key:
            cert = cert, args.cert_key
    kwargs = {
        'stream': True,
        'method': args.method.lower(),
        'url': args.url,
        'headers': headers,
        'data': data,
        'verify': {
            'yes': True,
            'true': True,
            'no': False,
            'false': False,
        }.get(args.verify.lower(), args.verify),
        'cert': cert,
        'timeout': args.timeout,
        'auth': args.auth,
        'proxies': dict((p.key, p.value) for p in args.proxy),
        'files': args.files,
        'allow_redirects': args.follow,
        'params': args.params,
    }
    return kwargs
