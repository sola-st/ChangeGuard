def get_counter(self, name, attributes = None):
    key = _generate_key_name(name, attributes)
    if key not in self.map:
        self.map[key] = self._create_counter(name)
    return self.map[key]
