def _get_commands_from_entry_points(inproject, group="scrapy.commands"):
    cmds = {}
    if sys.version_info >= (3, 10):
        eps = entry_points(group=group)
    else:
        eps = entry_points().get(group, ())
    for entry_point in eps:
        obj = entry_point.load()
        if inspect.isclass(obj):
            cmds[entry_point.name] = obj()
        else:
            raise Exception(f"Invalid entry point {entry_point.name}")
    return cmds
