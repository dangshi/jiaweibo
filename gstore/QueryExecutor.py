from gstore.GstoreConnector import GstoreConnector

defaultServerIP = "127.0.0.1"
defaultServerPort = "3305"
defaultDbName = "weibodb"
defaultUserName = "root"
defaultPassword = "123456"

def build_db(ip, port, db_name, db_source, username, password):
    # run gstore connector
    gc = GstoreConnector(ip, port)

    # build database
    ret = gc.build(db_name, db_source, username, password)

    res = gc.load(db_name, username, password)

    gc.show(username, password)

    return gc


class QueryExecutor(object):
    """docstring for ClassName"""
    def __init__(self, ip = defaultServerIP, port = defaultServerPort, db_name = defaultDbName, username = defaultUserName, password = defaultPassword):
        self.username = username
        self.password = password
        self.db_name = db_name
        self.gc = GstoreConnector(ip, port)
        self.gc.build(db_name, "/home/libing/code/gstore/weibodata.nt", username, password)
        self.gc.load(db_name, username, password)

    def execute(self, sparql):
        return self.gc.query(self.username, self.password, self.db_name, sparql)

if __name__ == '__main__':
    # gc = build_db(defaultServerIP, defaultServerPort, defaultDbName, "/home/libing/code/gstore/weibodata.nt", defaultUserName, defaultPassword)
    gc = GstoreConnector(defaultServerIP, defaultServerPort)
    # gc.build(defaultDbName, "/home/libing/code/gstore/weibodata.nt", defaultUserName, defaultPassword)
    gc.load(defaultDbName, defaultUserName, defaultPassword)
    # s = """fdf '
    #  " " "
    #  """
    # sparql = "select ?p ?o where {<http://localhost:2020/user/2452144190> ?p ?o.} "
    sparql = """
    PREFIX foaf:<http://localhost:2020/vocab/>  insert data { <http://localhost:2020/user/2452144190> <http://localhost:2020/vocab/password> "123".}
    """
    gc.query(defaultUserName, defaultPassword, defaultDbName, sparql)

    ret = gc.query(defaultUserName, defaultPassword, defaultDbName, sparql)
    sparql = "select ?p ?o where {<http://localhost:2020/user/2452144190> ?p ?o.} "
    sparql = """select ?p where {<http://localhost:2020/user/2452144190> ?p "Jing_Mini_Shop".}"""
    ret = gc.query(defaultUserName, defaultPassword, defaultDbName, sparql)
    print(ret)
    # qe = QueryExecutor()
    # ret = qe.execute(sparql)
    # print(ret)