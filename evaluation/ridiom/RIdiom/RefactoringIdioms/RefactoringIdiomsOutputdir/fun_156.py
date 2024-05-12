def _stream_logs_to_output(self):
    if not self.service:
        raise Exception("The 'service' should be initialized before!")
    logs , line  = self.cli.service_logs(self.service['ID'], follow=True, stdout=True, stderr=True, is_tty=self.tty), ''
    for log in logs:
        try:
            log = log.decode()
        except UnicodeDecodeError:
            continue
        if log == "\n":
            self.log.info(line)
            line = ""
        else:
            line += log
    if line:
        self.log.info(line)
