def __init__(
        self, sql,
        presto_conn_id='presto_default',
        *args, **kwargs):
    super(PrestoCheckOperator, self).__init__(sql=sql, *args, **kwargs)
    self.presto_conn_id = presto_conn_id
    self.sql = sql
