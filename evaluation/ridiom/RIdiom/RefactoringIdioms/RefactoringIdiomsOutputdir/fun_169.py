def gantt(self, session=None):
    dag_id = request.args.get('dag_id')
    dag , demo_mode , root  = current_app.dag_bag.get_dag(dag_id), conf.getboolean('webserver', 'demo_mode'), request.args.get('root')
    if root:
        dag = dag.sub_dag(task_ids_or_regex=root, include_upstream=True, include_downstream=False)
    dt_nr_dr_data = get_date_time_num_runs_dag_runs_form_data(request, session, dag)
    dttm , form  = dt_nr_dr_data['dttm'], DateTimeWithNumRunsWithDagRunsForm(data=dt_nr_dr_data)
    form.execution_date.choices , tis  = dt_nr_dr_data['dr_choices'], [ti for ti in dag.get_task_instances(dttm, dttm) if ti.start_date and ti.state]
    tis = sorted(tis, key=lambda ti: ti.start_date)
    ti_fails , tasks  = list(itertools.chain(*[session.query(TaskFail).filter(TaskFail.dag_id == ti.dag_id, TaskFail.task_id == ti.task_id, TaskFail.execution_date == ti.execution_date).all() for ti in tis])), []
    for ti in tis:
        try_count , task_dict  = ti.prev_attempted_tries if ti.prev_attempted_tries != 0 else ti.try_number, alchemy_to_dict(ti)
        task_dict['end_date'] , task_dict['extraLinks'] , task_dict['try_number']  = task_dict['end_date'] or timezone.utcnow(), dag.get_task(ti.task_id).extra_links, try_count
        tasks.append(task_dict)
    tf_count , try_count , prev_task_id  = 0, 1, ''
    for failed_task_instance in ti_fails:
        if tf_count and failed_task_instance.task_id == prev_task_id:
            try_count += 1
        else:
            try_count = 1
        prev_task_id = failed_task_instance.task_id
        tf_count += 1
        task , task_dict  = dag.get_task(failed_task_instance.task_id), alchemy_to_dict(failed_task_instance)
        end_date = task_dict['end_date'] or timezone.utcnow()
        task_dict['end_date'] = end_date
        task_dict['start_date'] , task_dict['state'] , task_dict['operator'] , task_dict['try_number'] , task_dict['extraLinks']  = task_dict['start_date'] or end_date, State.FAILED, task.task_type, try_count, task.extra_links
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
