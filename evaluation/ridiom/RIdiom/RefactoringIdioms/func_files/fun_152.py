def poll_job_in_queue(self, location, jenkins_server):
    location += "/api/json"
    self.log.info("Polling jenkins queue at the url %s", location)
    for attempt in range(self.max_try_before_job_appears):
        if attempt:
            time.sleep(self.sleep_time)
        try:
            location_answer = jenkins_request_with_headers(
                jenkins_server, Request(method="POST", url=location)
            )
        except (HTTPError, JenkinsException):
            self.log.warning("polling failed, retrying", exc_info=True)
        else:
            if location_answer is not None:
                json_response = json.loads(location_answer["body"])
                if (
                    "executable" in json_response
                    and json_response["executable"] is not None
                    and "number" in json_response["executable"]
                ):
                    build_number = json_response["executable"]["number"]
                    self.log.info("Job executed on Jenkins side with the build number %s", build_number)
                    return build_number
    else:
        raise AirflowException(
            f"The job hasn't been executed after polling the queue "
            f"{self.max_try_before_job_appears} times"
        )
