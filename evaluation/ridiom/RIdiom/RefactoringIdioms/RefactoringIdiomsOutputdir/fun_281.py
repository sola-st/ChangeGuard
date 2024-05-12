def __init__(self, spidercls, settings=None, init_reactor = False):
    if isinstance(spidercls, Spider):
        raise ValueError('The spidercls argument must be a class, not an object')
    if isinstance(settings, dict) or settings is None:
        settings = Settings(settings)
    self.spidercls , self.settings  = spidercls, settings.copy()
    self.spidercls.update_settings(self.settings)
    self.signals = SignalManager(self)
    self.stats = load_object(self.settings['STATS_CLASS'])(self)
    handler = LogCounterHandler(self, level=self.settings.get('LOG_LEVEL'))
    logging.root.addHandler(handler)
    d = dict(overridden_settings(self.settings))
    logger.info("Overridden settings:\n%(settings)s",
                {'settings': pprint.pformat(d)})
    if get_scrapy_root_handler() is not None:
        install_scrapy_root_handler(self.settings)
    self.__remove_handler = lambda: logging.root.removeHandler(handler)
    self.signals.connect(self.__remove_handler, signals.engine_stopped)
    lf_cls = load_object(self.settings['LOG_FORMATTER'])
    self.logformatter = lf_cls.from_crawler(self)
    reactor_class = self.settings.get("TWISTED_REACTOR")
    if init_reactor:
        if reactor_class:
            install_reactor(reactor_class, self.settings["ASYNCIO_EVENT_LOOP"])
        else:
            from twisted.internet import default
            default.install()
        log_reactor_info()
    if reactor_class:
        verify_installed_reactor(reactor_class)
    self.extensions = ExtensionManager.from_crawler(self)
    self.settings.freeze()
    self.crawling , self.spider , self.engine  = False, None, None
