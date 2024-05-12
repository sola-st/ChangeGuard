def run_and_check(self, session, prepped_request, extra_options):
    extra_options = extra_options or {}
    response = session.send(
        prepped_request,
        stream=extra_options.get("stream", False),
        verify=extra_options.get("verify", False),
        proxies=extra_options.get("proxies", {}),
        cert=extra_options.get("cert"),
        timeout=extra_options.get("timeout"),
        allow_redirects=extra_options.get("allow_redirects", True))
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        logging.error("HTTP error: " + response.reason)
        if self.method != 'GET':
            logging.error(response.text)
        raise AirflowException(str(response.status_code)+":"+response.reason)
    return response
