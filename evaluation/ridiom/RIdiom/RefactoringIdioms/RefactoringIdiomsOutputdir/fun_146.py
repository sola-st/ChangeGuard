def _start_new_batch(self, batch_id, uri, feed_options, spider, uri_template):
    storage = self._get_storage(uri, feed_options)
    slot = FeedSlot(
        storage=storage,
        uri=uri,
        format=feed_options["format"],
        store_empty=feed_options["store_empty"],
        batch_id=batch_id,
        uri_template=uri_template,
        filter=self.filters[uri_template],
        feed_options=feed_options,
        spider=spider,
        exporters=self.exporters,
        settings=self.settings,
        crawler=getattr(self, "crawler", None),
    )
    return slot
