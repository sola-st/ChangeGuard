def add_options(self, parser):
    group = OptionGroup(parser, "Global Options")
    group.add_option("--logfile", metavar="FILE", \
            help="log file. if omitted stderr will be used")
    group.add_option("-L", "--loglevel", metavar="LEVEL", \
            default=None, \
            help="log level (default: %s)" % settings['LOGLEVEL'])
    group.add_option("--nolog", action="store_true", \
            help="disable logging completely")
    group.add_option("--profile", metavar="FILE", default=None, \
            help="write python cProfile stats to FILE")
    group.add_option("--lsprof", metavar="FILE", default=None, \
            help="write lsprof profiling stats to FILE")
    group.add_option("--pidfile", metavar="FILE", \
            help="write process ID to FILE")
    group.add_option("-s", "--set", action="append", default=[], metavar="NAME=VALUE", \
            help="set/override setting (may be repeated)")
    parser.add_option_group(group)
