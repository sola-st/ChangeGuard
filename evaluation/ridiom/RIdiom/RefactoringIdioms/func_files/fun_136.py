def json(self):
    if self._cached_decoded_json is _NONE:
        self._cached_decoded_json = json.loads(self.body)
    return self._cached_decoded_json
