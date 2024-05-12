async def create_triggers(self):
    while self.to_create:
        trigger_id, trigger_instance = self.to_create.popleft()
        if trigger_id not in self.triggers:
            ti = trigger_instance.task_instance
            self.triggers[trigger_id] = {
                "task": asyncio.create_task(self.run_trigger(trigger_id, trigger_instance)),
                "name": f"{ti.dag_id}/{ti.run_id}/{ti.task_id}/{ti.map_index}/{ti.try_number} "
                f"(ID {trigger_id})",
                "events": 0,
            }
        else:
            self.log.warning("Trigger %s had insertion attempted twice", trigger_id)
        await asyncio.sleep(0)
