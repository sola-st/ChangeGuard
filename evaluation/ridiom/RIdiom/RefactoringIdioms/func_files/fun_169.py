def gantt(self, session=None):
    dag_id = request.args.get('dag_id')
    dag = current_app.dag_bag.get_dag(dag_id)
    demo_mode = conf.getboolean('webserver', 'demo_mode')
    root = request.args.get('root')
    if root:
        dag = dag.sub_dag(task_ids_or_regex=root, include_upstream=True, include_downstream=False)
    dt_nr_dr_data = get_date_time_num_runs_dag_runs_form_data(request, session, dag)
    dttm = dt_nr_dr_data['dttm']
    form = DateTimeWithNumRunsWithDagRunsForm(data=dt_nr_dr_data)
    form.execution_date.choices = dt_nr_dr_data['dr_choices']
    tis = [ti for ti in dag.get_task_instances(dttm, dttm) if ti.start_date and ti.state]
    tis = sorted(tis, key=lambda ti: ti.start_date)
    ti_fails = list(
        itertools.chain(
            *[
                (
                    session.query(TaskFail)
                    .filter(
                        TaskFail.dag_id == ti.dag_id,
                        TaskFail.task_id == ti.task_id,
                        TaskFail.execution_date == ti.execution_date,
                    )
                    .all()
                )
                for ti in tis
            ]
        )
    )
    tasks = []
    for ti in tis:
        try_count = ti.prev_attempted_tries if ti.prev_attempted_tries != 0 else ti.try_number
        task_dict = alchemy_to_dict(ti)
        task_dict['end_date'] = task_dict['end_date'] or timezone.utcnow()
        task_dict['extraLinks'] = dag.get_task(ti.task_id).extra_links
        task_dict['try_number'] = try_count
        tasks.append(task_dict)
    tf_count = 0
    try_count = 1
    prev_task_id = ""
    for failed_task_instance in ti_fails:
        if tf_count != 0 and failed_task_instance.task_id == prev_task_id:
            try_count += 1
        else:
            try_count = 1
        prev_task_id = failed_task_instance.task_id
        tf_count += 1
        task = dag.get_task(failed_task_instance.task_id)
        task_dict = alchemy_to_dict(failed_task_instance)
        end_date = task_dict['end_date'] or timezone.utcnow()
        task_dict['end_date'] = end_date
        task_dict['start_date'] = task_dict['start_date'] or end_date
        task_dict['state'] = State.FAILED
        task_dict['operator'] = task.task_type
        task_dict['try_number'] = try_count
        task_dict['extraLinks'] = task.extra_links
        tasks.append(task_dict)
    data = {
        'taskNames': [ti.task_id for ti in tis],
        'tasks': tasks,
        'height': len(tis) * 25 + 25,
    }
    session.commit()
    return self.render_template(
        'airflow/gantt.html',
        dag=dag,
        execution_date=dttm.isoformat(),
        form=form,
        data=data,
        base_date='',
        demo_mode=demo_mode,
        root=root,
    )
