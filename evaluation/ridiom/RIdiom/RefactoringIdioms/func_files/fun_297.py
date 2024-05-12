def _requests_to_follow(self, response):
    seen = set()
    for n, rule in enumerate(self._rules):
        links = [l for l in rule.link_extractor.extract_links(response) if l not in seen]
        if links and rule.process_links:
            links = rule.process_links(links)
        seen = seen.union(links)
        for link in links:
            r = Request(url=link.url, callback=self._response_downloaded)
            r.meta.update(rule=n, link_text=link.text)
            yield rule.process_request(r)
