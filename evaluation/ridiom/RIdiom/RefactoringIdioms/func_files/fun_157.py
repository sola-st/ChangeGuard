def run(
    self,
    sql,
    autocommit = False,
    parameters = None,
    handler = None,
    split_statements = True,
    return_last = True,
):
    self.descriptions = []
    if isinstance(sql, str):
        if split_statements:
            sql_list = [self.strip_sql_string(s) for s in self.split_sql_string(sql)]
        else:
            sql_list = [self.strip_sql_string(sql)]
    else:
        sql_list = [self.strip_sql_string(s) for s in sql]
    if sql_list:
        self.log.debug("Executing following statements against Databricks DB: %s", sql_list)
    else:
        raise ValueError("List of SQL statements is empty")
    conn = None
    results = []
    for sql_statement in sql_list:
        conn = self.get_conn()
        with closing(conn.cursor()) as cur:
            self.set_autocommit(conn, autocommit)
            with closing(conn.cursor()) as cur:
                self._run_command(cur, sql_statement, parameters)
                if handler is not None:
                    result = handler(cur)
                    if return_single_query_results(sql, return_last, split_statements):
                        results = [result]
                        self.descriptions = [cur.description]
                    else:
                        results.append(result)
                        self.descriptions.append(cur.description)
    if conn:
        conn.close()
        self._sql_conn = None
    if handler is None:
        return None
    if return_single_query_results(sql, return_last, split_statements):
        return results[-1]
    else:
        return results
