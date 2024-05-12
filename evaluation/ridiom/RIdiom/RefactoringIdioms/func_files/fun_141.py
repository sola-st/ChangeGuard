def inside_project():
    scrapy_module = os.environ.get(ENVVAR)
    if scrapy_module:
        try:
            import_module(scrapy_module)
        except ImportError as exc:
            warnings.warn(
                f"Cannot import scrapy settings module {scrapy_module}: {exc}"
            )
        else:
            return True
    return bool(closest_scrapy_cfg())
