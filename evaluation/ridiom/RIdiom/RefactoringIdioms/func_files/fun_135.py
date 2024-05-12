def start(
    self, stop_after_crawl = True, install_signal_handlers = True
):
    from twisted.internet import reactor
    if stop_after_crawl:
        d = self.join()
        if d.called:
            return
        d.addBoth(self._stop_reactor)
    resolver_class = load_object(self.settings["DNS_RESOLVER"])
    resolver = create_instance(resolver_class, self.settings, self, reactor=reactor)
    resolver.install_on_reactor()
    tp = reactor.getThreadPool()
    tp.adjustPoolsize(maxthreads=self.settings.getint("REACTOR_THREADPOOL_MAXSIZE"))
    reactor.addSystemEventTrigger("before", "shutdown", self.stop)
    if install_signal_handlers:
        reactor.addSystemEventTrigger(
            "after", "startup", install_shutdown_handlers, self._signal_shutdown
        )
    reactor.run(installSignalHandlers=install_signal_handlers)  
