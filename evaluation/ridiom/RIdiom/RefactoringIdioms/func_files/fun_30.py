def headers(self):
    try:
        raw = self._orig.raw
        if getattr(raw, '_original_response', None):
            raw_version = raw._original_response.version
        else:
            raw_version = raw.version
    except AttributeError:
        raw_version = 11
    version = {
        9: '0.9',
        10: '1.0',
        11: '1.1',
        20: '2.0',
    }[raw_version]
    original = self._orig
    status_line = f'HTTP/{version} {original.status_code} {original.reason}'
    headers = [status_line]
    headers.extend(
        ': '.join(header)
        for header in original.headers.items()
        if header[0] != 'Set-Cookie'
    )
    headers.extend(
        f'Set-Cookie: {cookie}'
        for header, value in original.headers.items()
        for cookie in split_cookies(value)
        if header == 'Set-Cookie'
    )
    return '\r\n'.join(headers)
