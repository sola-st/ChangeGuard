def process_response(self, request, response, spider):
    if (request.meta.get('dont_redirect', False) or
            response.status in getattr(spider, 'handle_httpstatus_list', []) or
            response.status in request.meta.get('handle_httpstatus_list', []) or
            request.meta.get('handle_httpstatus_all', False)):
        return response
    location = None
    if 'Location' in response.headers:
        location = response.headers['location']
    if location is not None and response.status in [301, 302, 303, 307]:
        redirected_url = urljoin(request.url, location)
        if response.status in [301, 307] or request.method == 'HEAD':
            redirected = request.replace(url=redirected_url)
            return self._redirect(redirected, request, spider, response.status)
        if response.status in [302, 303]:
            redirected = self._redirect_request_using_get(request, redirected_url)
            return self._redirect(redirected, request, spider, response.status)
    return response
