async def run(self):
    async with self.hook.async_conn as client:
        waiter = self.hook.get_waiter("batch_job_complete", deferrable=True, client=client)
        for attempt in range(1, 1 + self.max_retries):
            try:
                await waiter.wait(
                    jobs=[self.job_id],
                    WaiterConfig={
                        "Delay": self.poll_interval,
                        "MaxAttempts": 1,
                    },
                )
            except WaiterError as error:
                if "terminal failure" in str(error):
                    yield TriggerEvent(
                        {"status": "failure", "message": f"Delete Cluster Failed: {error}"}
                    )
                    break
                self.log.info(
                    "Job status is %s. Retrying attempt %s/%s",
                    error.last_response["jobs"][0]["status"],
                    attempt,
                    self.max_retries,
                )
                await asyncio.sleep(int(self.poll_interval))
            else:
                yield TriggerEvent({"status": "success", "job_id": self.job_id})
                break
        else:
            yield TriggerEvent({"status": "failure", "message": "Job Failed - max attempts reached."})
