def _get_commands_from_entry_points(inproject, group="scrapy.commands"):
    cmds = {}
    for entry_point in entry_points().get(group, {}):
        obj = entry_point.load()
        if inspect.isclass(obj):
            cmds[entry_point.name] = obj()
        else:
            raise Exception(f"Invalid entry point {entry_point.name}")
    return cmds
