def execute(self, context):
    self.log.info('Executing: %s', self.sql)
    hook = VerticaHook(vertica_conn_id=self.vertica_conn_id, log_sql=False)
    hook.run(sql=self.sql)
