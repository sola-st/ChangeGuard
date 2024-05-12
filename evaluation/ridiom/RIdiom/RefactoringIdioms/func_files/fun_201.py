def json(self):
    if __debug__:
        _assert_have_json()
    if self.mimetype == 'application/json':
        request_charset = self.mimetype_params.get('charset')
        if request_charset is not None:
            return json.loads(self.data, encoding=request_charset)
        return json.loads(self.data)
