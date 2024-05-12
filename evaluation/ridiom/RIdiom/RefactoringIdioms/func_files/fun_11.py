def iter_mapped_task_groups(self):
    if (group := self.task_group) is None:
        return
    yield from group.iter_mapped_task_groups()
