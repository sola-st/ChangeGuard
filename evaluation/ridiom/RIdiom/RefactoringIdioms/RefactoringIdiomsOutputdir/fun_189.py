def get_response(session_name, requests_kwargs, config_dir, read_only=False):
    if os.path.sep in session_name:
        path = os.path.expanduser(session_name)
    else:
        hostname = (
            requests_kwargs['headers'].get('Host', None)
            or urlsplit(requests_kwargs['url']).netloc.split('@')[-1]
        )
        assert re.match('^[a-zA-Z0-9_.:-]+$', hostname)
        hostname = hostname.replace(':', '_')
        path = os.path.join(config_dir,
                            SESSIONS_DIR_NAME,
                            hostname,
                            session_name + '.json')
    session = Session(path)
    session.load()
    request_headers = requests_kwargs.get('headers', {})
    requests_kwargs['headers'] = dict(session.headers, **request_headers)
    session.update_headers(request_headers)
    auth = requests_kwargs.get('auth', None)
    if auth:
        session.auth = auth
    elif session.auth:
        requests_kwargs['auth'] = session.auth
    requests_session = requests.Session()
    requests_session.cookies = session.cookies
    try:
        response = requests_session.request(**requests_kwargs)
    except Exception:
        raise
    else:
        if session.is_new or not read_only:
            session.cookies = requests_session.cookies
            session.save()
        return response
