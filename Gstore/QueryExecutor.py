from GstoreConnector import GstoreConnector


def build_db(ip, port, db_name, db_source, username, password):
    # run gstore connector
    gc = GstoreConnector(ip, port)

    # build database
    ret = gc.build(db_name, db_source, username, password)

    res = gc.load(db_name, username, password)

    gc.show(username, password)


class QueryExecutor(object):
    """docstring for ClassName"""
    def __init__(self, ip, port, db_name, username, password):
        self.username = username
        self.password = password
        self.db_name = db_name
        self.gc = GstoreConnector(ip, port)
        self.gc.load(db_name, username, password)

    def execute(self, sparql):
        return self.gc.query(self.username, self.password, self.db_name, sparql)
