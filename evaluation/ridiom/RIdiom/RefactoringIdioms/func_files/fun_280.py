def url_has_any_extension(url, extensions):
    lowercase_path = parse_url(url).path.lower()
    return any(lowercase_path.endswith(ext) for ext in extensions)
