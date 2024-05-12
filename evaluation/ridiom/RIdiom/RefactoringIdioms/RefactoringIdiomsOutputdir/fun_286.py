def follow_all(self, urls=None, callback=None, method='GET', headers=None, body=None,
               cookies=None, meta=None, encoding=None, priority=0,
               dont_filter=False, errback=None, cb_kwargs=None,
               css=None, xpath=None):
    arg_count = len(list(filter(None, (urls, css, xpath))))
    if arg_count != 1:
        raise ValueError('Please supply exactly one of the following arguments: urls, css, xpath')
    if not urls:
        if css:
            selector_list = self.css(css)
        if xpath:
            selector_list = self.xpath(xpath)
        urls = []
        for selector in selector_list:
            try:
                urls.append(_url_from_selector(selector))
            except ValueError:
                pass
    return (
        self.follow(
            url=url,
            callback=callback,
            method=method,
            headers=headers,
            body=body,
            cookies=cookies,
            meta=meta,
            encoding=encoding,
            priority=priority,
            dont_filter=dont_filter,
            errback=errback,
            cb_kwargs=cb_kwargs,
        )
        for url in urls
    )
