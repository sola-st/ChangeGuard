def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
    if self.url_prefix is not None:
        rule = '/'.join((self.url_prefix, rule.lstrip('/')))
    options.setdefault('subdomain', self.subdomain)
    if endpoint is None:
        endpoint = _endpoint_from_view_func(view_func)
    defaults = self.url_defaults
    if 'defaults' in options:
        defaults = dict(defaults, **options.pop('defaults'))
    self.app.add_url_rule(rule, '%s.%s' % (self.blueprint.name, endpoint),
                          view_func, defaults=defaults, **options)
