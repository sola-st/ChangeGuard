def create_url_adapter(self, request):
    if request is not None:
        if not self.subdomain_matching:
            subdomain = self.url_map.default_subdomain or None
        else:
            subdomain = None
        return self.url_map.bind_to_environ(
            request.environ,
            server_name=self.config["SERVER_NAME"],
            subdomain=subdomain,
        )
    if self.config["SERVER_NAME"] is not None:
        return self.url_map.bind(
            self.config["SERVER_NAME"],
            script_name=self.config["APPLICATION_ROOT"],
            url_scheme=self.config["PREFERRED_URL_SCHEME"],
        )
    return None
