def manage_slas(self, dag, session = None):
    self.log.info("Running SLA Checks for %s", dag.dag_id)
    if not any(isinstance(ti.sla, timedelta) for ti in dag.tasks):
        self.log.info("Skipping SLA check for %s because no tasks in DAG have SLAs", dag)
        return
    qry = (
        session.query(TI.task_id, func.max(TI.execution_date).label('max_ti'))
        .with_hint(TI, 'USE INDEX (PRIMARY)', dialect_name='mysql')
        .filter(TI.dag_id == dag.dag_id)
        .filter(or_(TI.state == State.SUCCESS, TI.state == State.SKIPPED))
        .filter(TI.task_id.in_(dag.task_ids))
        .group_by(TI.task_id)
        .subquery('sq')
    )
    max_tis , ts  = session.query(TI).filter(TI.dag_id == dag.dag_id, TI.task_id == qry.c.task_id, TI.execution_date == qry.c.max_ti).all(), timezone.utcnow()
    for ti in max_tis:
        task = dag.get_task(ti.task_id)
        if task.sla and not isinstance(task.sla, timedelta):
            raise TypeError(
                f"SLA is expected to be timedelta object, got "
                f"{type(task.sla)} in {task.dag_id}:{task.task_id}"
            )
        dttm = dag.following_schedule(ti.execution_date)
        while dttm < ts:
            following_schedule = dag.following_schedule(dttm)
            if following_schedule + task.sla < ts:
                session.merge(
                    SlaMiss(task_id=ti.task_id, dag_id=ti.dag_id, execution_date=dttm, timestamp=ts)
                )
            dttm = dag.following_schedule(dttm)
    session.commit()
    slas = (
        session.query(SlaMiss)
        .filter(SlaMiss.notification_sent == False, SlaMiss.dag_id == dag.dag_id)  
        .all()
    )
    if slas:  
        sla_dates = [sla.execution_date for sla in slas]
        fetched_tis , blocking_tis  = session.query(TI).filter(TI.state != State.SUCCESS, TI.execution_date.in_(sla_dates), TI.dag_id == dag.dag_id).all(), []
        for ti in fetched_tis:
            if ti.task_id in dag.task_ids:
                ti.task = dag.get_task(ti.task_id)
                blocking_tis.append(ti)
            else:
                session.delete(ti)
                session.commit()
        task_list , blocking_task_list , email_sent , notification_sent  = '\n'.join((sla.task_id + ' on ' + sla.execution_date.isoformat() for sla in slas)), '\n'.join((ti.task_id + ' on ' + ti.execution_date.isoformat() for ti in blocking_tis)), False, False
        if dag.sla_miss_callback:
            self.log.info('Calling SLA miss callback')
            try:
                dag.sla_miss_callback(dag, task_list, blocking_task_list, slas, blocking_tis)
                notification_sent = True
            except Exception:  
                self.log.exception("Could not call sla_miss_callback for DAG %s", dag.dag_id)
        email_content , tasks_missed_sla  = f"            Here's a list of tasks that missed their SLAs:\n            <pre><code>{task_list}\n<code></pre>\n            Blocking tasks:\n            <pre><code>{blocking_task_list}<code></pre>\n            Airflow Webserver URL: {conf.get(section='webserver', key='base_url')}\n            ", []
        for sla in slas:
            try:
                task = dag.get_task(sla.task_id)
            except TaskNotFound:
                self.log.warning(
                    "Task %s doesn't exist in DAG anymore, skipping SLA miss notification.", sla.task_id
                )
                continue
            tasks_missed_sla.append(task)
        emails = set()
        for task in tasks_missed_sla:
            if task.email:
                if isinstance(task.email, str):
                    emails |= set(get_email_address_list(task.email))
                elif isinstance(task.email, (list, tuple)):
                    emails |= set(task.email)
        if emails:
            try:
                send_email(emails, f"[airflow] SLA miss on DAG={dag.dag_id}", email_content)
                email_sent , notification_sent  = True, True
            except Exception:  
                Stats.incr('sla_email_notification_failure')
                self.log.exception("Could not send SLA Miss email notification for DAG %s", dag.dag_id)
        if notification_sent:
            for sla in slas:
                sla.email_sent , sla.notification_sent  = email_sent, True
                session.merge(sla)
        session.commit()
