def _task_instance_exists(session, source_table, dag_run, task_instance):
    if 'run_id' not in task_instance.c:
        where_clause = and_(
            source_table.c.dag_id == task_instance.c.dag_id,
            source_table.c.task_id == task_instance.c.task_id,
            source_table.c.execution_date == task_instance.c.execution_date,
        )
        ti_to_dr_join_cond = and_(
            dag_run.c.dag_id == task_instance.c.dag_id,
            dag_run.c.execution_date == task_instance.c.execution_date,
        )
    else:
        where_clause = and_(
            source_table.c.dag_id == task_instance.c.dag_id,
            source_table.c.task_id == task_instance.c.task_id,
            source_table.c.execution_date == dag_run.c.execution_date,
        )
        ti_to_dr_join_cond = and_(
            dag_run.c.dag_id == task_instance.c.dag_id,
            dag_run.c.run_id == task_instance.c.run_id,
        )
    exists_subquery = (
        session.query(text('1'))
        .select_from(task_instance.join(dag_run, onclause=ti_to_dr_join_cond))
        .filter(where_clause)
    )
    return exists_subquery
