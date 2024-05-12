def set_spidercls(self, url, opts):
    spider_loader = self.crawler_process.spider_loader
    if opts.spider:
        try:
            self.spidercls = spider_loader.load(opts.spider)
        except KeyError:
            logger.error('Unable to find spider: %(spider)s',
                         {'spider': opts.spider})
    else:
        self.spidercls = spidercls_for_request(spider_loader, Request(url))
        if not self.spidercls:
            logger.error('Unable to find spider for: %(url)s', {'url': url})
    def _start_requests(spider):
        yield self.prepare_request(spider, Request(url), opts)
    self.spidercls.start_requests = _start_requests
