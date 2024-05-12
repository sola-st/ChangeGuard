def __init__(
        self, host=None, login=None,
        psw=None, db=None, port=None, postgres_conn_id=None):
    if not postgres_conn_id:
        self.host , self.login , self.psw , self.db , self.port  = host, login, psw, db, port
    else:
        session = settings.Session()
        db = session.query(
            Connection).filter(
                Connection.conn_id == postgres_conn_id)
        if not db.count():
            raise Exception("The postgres_dbid you provided isn't defined")
        else:
            db = db.all()[0]
        self.host , self.login , self.psw , self.db , self.port  = db.host, db.login, db.password, db.schema, db.port
        session.commit()
        session.close()
