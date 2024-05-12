def download_request(self, request):
    timeout = request.meta.get('download_timeout') or self._connectTimeout
    agent = self._get_agent(request, timeout)
    url = urldefrag(request.url)[0]
    method = to_bytes(request.method)
    headers = TxHeaders(request.headers)
    if isinstance(agent, self._TunnelingAgent):
        headers.removeHeader(b'Proxy-Authorization')
    if request.body:
        bodyproducer = _RequestBodyProducer(request.body)
    elif method == b'POST':
        bodyproducer = _RequestBodyProducer(b'')
    else:
        bodyproducer = None
    start_time = time()
    d = agent.request(
        method, to_bytes(url, encoding='ascii'), headers, bodyproducer)
    d.addCallback(self._cb_latency, request, start_time)
    d.addCallback(self._cb_bodyready, request)
    d.addCallback(self._cb_bodydone, request, url)
    self._timeout_cl = reactor.callLater(timeout, d.cancel)
    d.addBoth(self._cb_timeout, request, url, timeout)
    return d
