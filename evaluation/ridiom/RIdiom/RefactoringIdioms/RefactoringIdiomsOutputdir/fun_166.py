def create_pool(name, slots, description, session=None):
    if not (name and name.strip()):
        raise AirflowBadRequest("Pool name shouldn't be empty")
    try:
        slots = int(slots)
    except ValueError:
        raise AirflowBadRequest(f"Bad value for `slots`: {slots}")
    pool_name_length = Pool.pool.property.columns[0].type.length
    if len(name) > pool_name_length:
        raise AirflowBadRequest(f"Pool name can't be more than {pool_name_length} characters")
    session.expire_on_commit = False
    pool = session.query(Pool).filter_by(pool=name).first()
    if pool is None:
        pool = Pool(pool=name, slots=slots, description=description)
        session.add(pool)
    else:
        pool.slots , pool.description  = slots, description
    session.commit()
    return pool
