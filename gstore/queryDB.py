from gstore.GstoreConnector import GstoreConnector
from gstore.QueryExecutor import QueryExecutor
import json
import random

defaultServerIP = "127.0.0.1"
defaultServerPort = "3305"
defaultDbName = "weibodb"
defaultUserName = "root"
defaultPassword = "123456"

qe = QueryExecutor()

def _generate_uid():
    while (True):
        rand = random.randint(1000000000, 9999999999)
        sparql = "select ?o where {<http://localhost:2020/user/" + str(rand) + "> <http://localhost:2020/vocab/user_name> ?o.}"
        ret = qe.execute(sparql)
        retjson = json.loads(ret)
        if len(retjson["results"]["bindings"]) == 0:
            return rand

def gstore_user_register(username, password):
    sparql = "select ?s where {?s <http://localhost:2020/vocab/user_name> \"" + username + "\".}"
    password = str(password)
    ret = qe.execute(sparql)
    retjson = json.loads(ret)
    if len(retjson["results"]["bindings"]) != 0:
        retdict = {'status':'FAIL', 'msg':'duplicate username', 'result':[]}
        return retdict
    uid = _generate_uid()
    sparql = "insert data { <http://localhost:2020/user/" + str(uid) + "> <http://localhost:2020/vocab/password> \""+password+"\".}"
    qe.execute(sparql)
    sparql = "insert data { <http://localhost:2020/user/" + str(uid) + "> <http://localhost:2020/vocab/user_name> \"" + username + "\".}"
    qe.execute(sparql)
    retdict = {'status': 'OK', 'msg': 'successfully registered', 'result': []}
    return retdict

def gstore_user_login(username, password):
    sparql = "select ?s where {?s <http://localhost:2020/vocab/user_name> \"" + username + "\".}"
    ret = qe.execute(sparql)
    retjson = json.loads(ret)
    if len(retjson["results"]["bindings"]) == 0:
        retdict = {'status': 'FAIL', 'msg': '用户不存在', 'result': []}
        return retdict
    uid = retjson["results"]["bindings"][0]['s']['value']
    sparql = "select ?o where { <" + str(uid) + "> <http://localhost:2020/vocab/password> ?o.}"
    ret = qe.execute(sparql)
    retjson = json.loads(ret)
    if len(retjson["results"]["bindings"]) == 0:
        retdict = {'status': 'FAIL', 'msg': '没有这个人的密码', 'result': []}
        return retdict
    pwd = retjson["results"]["bindings"][0]['o']['value']
    if (pwd == password):
        retdict = {'status': 'OK', 'msg': '登录成功', 'result': []}
        return retdict
    else:
        retdict = {'status': 'FAIL', 'msg': '密码错误', 'result': []}
        return retdict

if __name__ == '__main__':
    # ret = gstore_user_register("afucsjker", "123")
    # sparql = """select ?s where {?s ?p "afucsjker".}"""
    # ret = qe.execute(sparql)
    ret = gstore_user_login("afucsjkfder", "1233")
    print(ret)