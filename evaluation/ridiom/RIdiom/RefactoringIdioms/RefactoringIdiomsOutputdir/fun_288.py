def _retry(self, request, reason, spider):
    retries , retry_times , stats  = request.meta.get('retry_times', 0) + 1, request.meta.get('max_retry_times') or self.max_retry_times, spider.crawler.stats
    if retries <= retry_times:
        logger.debug("Retrying %(request)s (failed %(retries)d times): %(reason)s",
                     {'request': request, 'retries': retries, 'reason': reason},
                     extra={'spider': spider})
        retryreq = request.copy()
        retryreq.meta['retry_times'] , retryreq.dont_filter , retryreq.priority  = retries, True, request.priority + self.priority_adjust
        if isinstance(reason, Exception):
            reason = global_object_name(reason.__class__)
        stats.inc_value('retry/count')
        stats.inc_value('retry/reason_count/%s' % reason)
        return retryreq
    else:
        stats.inc_value('retry/max_reached')
        logger.debug("Gave up retrying %(request)s (failed %(retries)d times): %(reason)s",
                     {'request': request, 'retries': retries, 'reason': reason},
                     extra={'spider': spider})
