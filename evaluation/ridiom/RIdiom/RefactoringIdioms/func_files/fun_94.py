def download_file(
    url,
    dest,
    session = None,
    chunk_size = 1024,
):
    import requests
    from poetry.puzzle.provider import Indicator
    get = requests.get if not session else session.get
    response = get(url, stream=True, timeout=REQUESTS_TIMEOUT)
    response.raise_for_status()
    set_indicator = False
    with Indicator.context() as update_context:
        update_context(f"Downloading {url}")
        if "Content-Length" in response.headers:
            try:
                total_size = int(response.headers["Content-Length"])
            except ValueError:
                total_size = 0
            fetched_size = 0
            last_percent = 0
            set_indicator = total_size > 1024 * 1024
        with atomic_open(dest) as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    if set_indicator:
                        fetched_size += len(chunk)
                        percent = (fetched_size * 100) // total_size
                        if percent > last_percent:
                            last_percent = percent
                            update_context(f"Downloading {url} {percent:3}%")
