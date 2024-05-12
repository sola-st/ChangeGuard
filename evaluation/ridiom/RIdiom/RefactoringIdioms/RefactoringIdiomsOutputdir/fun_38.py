def auth(self, auth):
    assert {'type', 'raw_auth'} == auth.keys()
    self['auth'] = auth
