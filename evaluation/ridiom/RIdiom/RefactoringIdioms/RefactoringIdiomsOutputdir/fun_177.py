def execute(self, context):
    hive = HiveCliHook(hive_cli_conn_id=self.hive_cli_conn_id)
    logging.info("Extracting data from Hive")
    hive_table , sql , hql  = 'druid.' + context['task_instance_key_str'].replace('.', '_'), self.sql.strip().strip(';'), "        set mapred.output.compress=false;\n        set hive.exec.compress.output=false;\n        DROP TABLE IF EXISTS {hive_table};\n        CREATE TABLE {hive_table}\n        ROW FORMAT DELIMITED FIELDS TERMINATED BY  '\t'\n        STORED AS TEXTFILE\n        TBLPROPERTIES ('serialization.null.format' = '')\n        AS\n        {sql}\n        ".format(**locals())
    logging.info("Running command:\n {}".format(hql))
    hive.run_cli(hql)
    m = HiveMetastoreHook(self.metastore_conn_id)
    t = m.get_table(hive_table)
    columns , hdfs_uri  = [col.name for col in t.sd.cols], m.get_table(hive_table).sd.location
    pos = hdfs_uri.find('/user')
    static_path = hdfs_uri[pos:]
    schema, table = hive_table.split('.')
    druid = DruidHook(druid_ingest_conn_id=self.druid_ingest_conn_id)
    logging.info("Inserting rows into Druid")
    logging.info("HDFS path: " + static_path)
    try:
        druid.load_from_hdfs(
            datasource=self.druid_datasource,
            intervals=self.intervals,
            static_path=static_path, ts_dim=self.ts_dim,
            columns=columns, num_shards=self.num_shards, target_partition_size=self.target_partition_size,
            metric_spec=self.metric_spec, hadoop_dependency_coordinates=self.hadoop_dependency_coordinates)
        logging.info("Load seems to have succeeded!")
    finally:
        logging.info(
            "Cleaning up by dropping the temp "
            "Hive table {}".format(hive_table))
        hql = "DROP TABLE IF EXISTS {}".format(hive_table)
        hive.run_cli(hql)
