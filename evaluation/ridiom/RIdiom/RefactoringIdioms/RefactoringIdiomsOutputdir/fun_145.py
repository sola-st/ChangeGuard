def from_crawler(cls, crawler):
    interval = crawler.settings.getfloat("LOGSTATS_INTERVAL")
    try:
        ext_stats = crawler.settings.getdict("PERIODIC_LOG_STATS")
    except ValueError:
        ext_stats = (
            {"enabled": True}
            if crawler.settings.getbool("PERIODIC_LOG_STATS")
            else None
        )
    except TypeError:
        ext_stats = (
            {"enabled": True}
            if crawler.settings.getbool("PERIODIC_LOG_STATS")
            else None
        )
    try:
        ext_delta = crawler.settings.getdict("PERIODIC_LOG_DELTA")
    except ValueError:
        ext_delta = (
            {"enabled": True}
            if crawler.settings.getdict("PERIODIC_LOG_DELTA")
            else None
        )
    except TypeError:
        ext_stats = (
            {"enabled": True}
            if crawler.settings.getbool("PERIODIC_LOG_DELTA")
            else None
        )
    ext_timing_enabled = crawler.settings.getbool(
        "PERIODIC_LOG_TIMING_ENABLED", False
    )
    if not interval:
        raise NotConfigured
    if not (ext_stats or ext_delta or ext_timing_enabled):
        raise NotConfigured
    o = cls(
        crawler.stats,
        interval,
        ext_stats,
        ext_delta,
        ext_timing_enabled,
    )
    crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
    crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
    return o
