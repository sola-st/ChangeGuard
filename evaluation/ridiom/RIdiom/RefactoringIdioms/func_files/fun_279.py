def _get_slot(self, request, spider):
    key = self._get_slot_key(request, spider)
    if key not in self.slots:
        slot_settings = self.per_slot_settings.get(key, {})
        conc = slot_settings.get(
            'concurrency', self.ip_concurrency if self.ip_concurrency else self.domain_concurrency
        )
        conc, delay = _get_concurrency_delay(conc, spider, self.settings)
        delay = slot_settings.get('delay', delay)
        randomize_delay = slot_settings.get('randomize_delay', self.randomize_delay)
        new_slot = Slot(conc, delay, randomize_delay)
        self.slots[key] = new_slot
    return key, self.slots[key]
