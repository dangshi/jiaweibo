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

def _generate_weiboid():
    while (True):
        rand = random.randint(10000000000000, 99999999999999)
        sparql = "select ?o where {<http://localhost:2020/weibo/" + str(rand) + "> <http://localhost:2020/vocab/weibo_uid> ?o.}"
        ret = qe.execute(sparql)
        retjson = json.loads(ret)
        if len(retjson["results"]["bindings"]) == 0:
            return rand

'''get userid url'''
def _get_userid(username):
    sparql = "select ?s where {?s <http://localhost:2020/vocab/user_name> \"" + username + "\".}"
    ret = qe.execute(sparql)
    retjson = json.loads(ret)
    if len(retjson["results"]["bindings"]) == 0:
        return None
    else :
        return retjson["results"]["bindings"][0]['s']['value']

'''get username string'''
def _get_username(userid):
    sparql = "select ?o where {<http://localhost:2020/user/" + str(userid) + "> <http://localhost:2020/vocab/user_name> ?o.}"
    ret = qe.execute(sparql)
    retjson = json.loads(ret)
    if len(retjson["results"]["bindings"]) == 0:
        return None
    else:
        return retjson["results"]["bindings"][0]['o']['value']

'''get username string'''
def gstore_get_username(userid):
    sparql = "select ?o where {<http://localhost:2020/user/" + str(userid) + "> <http://localhost:2020/vocab/user_name> ?o.}"
    ret = qe.execute(sparql)
    retjson = json.loads(ret)
    if len(retjson["results"]["bindings"]) == 0:
        return None
    else:
        return retjson["results"]["bindings"][0]['o']['value']

def _get_follwee(username):
    useridurl = _get_userid(username)
    userid = useridurl.split('/')[-1]
    sparql = "select ?s where {?s <http://localhost:2020/vocab/userrelation_suid> \"" + userid + "\"}"
    ret = qe.execute(sparql)
    retjson = json.loads(ret)
    result = []
    list_follow = retjson["results"]["bindings"]
    for follow in list_follow:
        str_to_proc = follow['s']['value']
        followerid = str_to_proc.split("/")[-1]
        followername = _get_username(followerid)
        result.append(followername)
    return result

def _is_follow(fan, celebrity):
    fanidurl = _get_userid(fan)
    fanid = fanidurl.split("/")[-1]
    celebrityidurl = _get_userid(celebrity)
    celebrityid = celebrityidurl.split("/")[-1]
    sparql = "select ?s {<http://localhost:2020/userrelation/" + fanid + "/" + celebrityid + "> <http://localhost:2020/vocab/userrelation_suid> \"" + fanid + "\" }"
    ret = qe.execute(sparql)
    retjson = json.loads(ret)
    if len(retjson["results"]["bindings"]) == 0:
        return False
    else: return True

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
    userid = uid.split('/')[-1]
    if (pwd == password):
        retdict = {'status': 'OK', 'msg': '登录成功', 'result': {'userid': userid}}
        return retdict
    else:
        retdict = {'status': 'FAIL', 'msg': '密码错误', 'result':[]}
        return retdict

def gstore_user_weibo(username, offset = 0, size = -1):
    useridurl = _get_userid(username)
    if (useridurl == None):
        return {"status": "OK", "msg": "查询成功", "result": []}
    userid = useridurl.split('/')[-1]
    sparql = "select ?s  where {?s <http://localhost:2020/vocab/weibo_uid> ?o . FILTER regex(?o, '" + userid + "')}"
    ret = qe.execute(sparql)
    retjson = json.loads(ret)
    result = []
    if len(retjson["results"]["bindings"]) == 0:
        retdict = {"status": "OK",  "msg":"查询成功", "result":[]}
        return retdict
    else :
        list_weibo = retjson["results"]["bindings"]
        for weibo in list_weibo:
            weiboid = weibo['s']['value']
            sparql = "select  ?o  where { <" + weiboid + "> <http://localhost:2020/vocab/weibo_text> ?o . }"
            ret = qe.execute(sparql)
            retjson = json.loads(ret)
            content = retjson["results"]["bindings"][0]['o']['value']
            sparql = "select  ?o  where { <" + weiboid + "> <http://localhost:2020/vocab/weibo_date> ?o . }"
            ret = qe.execute(sparql)
            retjson = json.loads(ret)
            time = retjson["results"]["bindings"][0]['o']['value']
            entry = {"username": username, "content": content, "post_time": time}
            result.append(entry)
        result.sort(key=lambda k: (k.get('post_time', 0)))
        result.reverse()
        if (size != -1):
            result = result[offset: offset+size]
        retdict = {"status": "OK", "msg": "查询成功", "result": result}
        return retdict

def gstore_user_following_weibo(username, offset = 0, size = -1):
    useridurl = _get_userid(username)
    userid = useridurl.split('/')[-1]
    sparql = "select ?s where {?s <http://localhost:2020/vocab/userrelation_suid> \"" + userid + "\"}"
    ret = qe.execute(sparql)
    retjson = json.loads(ret)
    result = []
    if len(retjson["results"]["bindings"]) == 0:
        retdict = {"status": "OK",  "msg":"查询成功", "result":[]}
        return retdict
    else:
        list_follow = retjson["results"]["bindings"]
        for follow in list_follow:
            str_to_proc = follow['s']['value']
            followerid = str_to_proc.split("/")[-1]
            followername = _get_username(followerid)
            result += gstore_user_weibo(followername)['result']
        result.sort(key=lambda k: (k.get('post_time', 0)))
        result.reverse()
        if (size != -1):
            result = result[offset: offset + size]
        retdict = {"status": "OK", "msg": "查询成功", "result": result}
        return retdict

# {
#   "status": "OK",  # "OK","FAIL",
#   "msg":"查询成功", # 是否成功，失败原因
#   "result":{
#     "posts_num":12, #发帖数
#     "following":1, # 关注的人数
#     "followed":1, # 粉丝人数
#   }
# }
def gstore_user_info(username):
    try:
        userweibo = gstore_user_weibo(username)['result']
        weibocnt = len(userweibo)
        useridurl = _get_userid(username)
        userid = useridurl.split('/')[-1]
        sparql = "select ?s where {?s <http://localhost:2020/vocab/userrelation_suid> \"" + userid + "\"}"
        ret = qe.execute(sparql)
        retjson = json.loads(ret)
        nfollows =  len(retjson["results"]["bindings"])

        sparql = "select ?s where {?s <http://localhost:2020/vocab/userrelation_tuid> \"" + userid + "\"}"
        ret = qe.execute(sparql)
        retjson = json.loads(ret)
        nfollowers = len(retjson["results"]["bindings"])
        retdict = {"status": "OK", "msg": "查询成功", "result": {"userid":userid,"posts_num":weibocnt, "following_num": nfollows, "followed_num": nfollowers}}
    except Exception as e:
        retdict = {"status":"FAIL", "msg":"查询失败", "result":""}
    return retdict

def gstore_user_detail_info(username):
    try:
        userweibo = gstore_user_weibo(username)['result']
        weibocnt = len(userweibo)
        useridurl = _get_userid(username)
        userid = useridurl.split('/')[-1]
        sparql = "select ?s where {?s <http://localhost:2020/vocab/userrelation_suid> \"" + userid + "\"}"
        ret = qe.execute(sparql)
        retjson = json.loads(ret)
        nfollows =  len(retjson["results"]["bindings"])
        following = list()
        for item in retjson["results"]["bindings"]:
            str_to_proc = item['s']['value']
            followerid = str_to_proc.split("/")[-1]
            followername = _get_username(followerid)
            following.append(followername)

        sparql = "select ?s where {?s <http://localhost:2020/vocab/userrelation_tuid> \"" + userid + "\"}"
        ret = qe.execute(sparql)
        retjson = json.loads(ret)
        nfollowers = len(retjson["results"]["bindings"])
        followed = list()
        for item in retjson["results"]["bindings"]:
            str_to_proc = item['s']['value']
            followerid = str_to_proc.split("/")[-1]
            followername = _get_username(followerid)
            followed.append(followername)

        retdict = {"status": "OK", "msg": "查询成功", "result": {"userid":userid,"posts_num":weibocnt, "following_num": nfollows, "followed_num": nfollowers,
                                                             "following":following, "followed":followed}}
    except Exception as e:
        retdict = {"status": "FAIL", "msg": "查询失败", "result": ""}
    return retdict

# {
#   "status": "OK",  # "OK","FAIL",
#   "msg":"操作成功", # 是否成功，失败原因
#   "result":[]
# }
def gstore_add_follow(fan, celebrity):
    # sparql = "insert data { <http://localhost:2020/user/" + str(uid) + "> <http://localhost:2020/vocab/password> \"" + password + "\".}"
    fanidurl = _get_userid(fan)
    fanid = fanidurl.split("/")[-1]
    celebrityidurl = _get_userid(celebrity)
    celebrityid = celebrityidurl.split("/")[-1]
    sparql = "insert data {<http://localhost:2020/userrelation/" + fanid + "/" + celebrityid + "> <http://localhost:2020/vocab/userrelation_suid> \"" + fanid + "\" }"
    qe.execute(sparql)
    sparql = "insert data {<http://localhost:2020/userrelation/" + fanid + "/" + celebrityid + "> <http://localhost:2020/vocab/userrelation_tuid> \"" + celebrityid + "\" }"
    qe.execute(sparql)
    retdict = {"status": "OK", "msg": "操作成功", "result": []}
    return retdict

def gstore_remove_follow(fan, celebrity):
    fanidurl = _get_userid(fan)
    fanid = fanidurl.split("/")[-1]
    celebrityidurl = _get_userid(celebrity)
    celebrityid = celebrityidurl.split("/")[-1]
    sparql = "delete data {<http://localhost:2020/userrelation/" + fanid + "/" + celebrityid + "> <http://localhost:2020/vocab/userrelation_suid> \"" + fanid + "\" }"
    ret = qe.execute(sparql)
    sparql = "delete data {<http://localhost:2020/userrelation/" + fanid + "/" + celebrityid + "> <http://localhost:2020/vocab/userrelation_tuid> \"" + celebrityid + "\" }"
    qe.execute(sparql)
    retdict = {"status": "OK", "msg": "操作成功", "result": []}
    return retdict

def gstore_post_weibo(username, content, post_time):
    useridurl = _get_userid(username)
    if (useridurl == None):
        return {"status": "FAIL", "msg": "wrong username", "result": []}
    weiboid = str(_generate_weiboid())
    userid = useridurl.split('/')[-1]
    sparql = "insert data {<http://localhost:2020/weibo/" + weiboid + "> <http://localhost:2020/vocab/weibo_uid> \"" + userid + "\" }"
    ret = qe.execute(sparql)
    sparql = "insert data {<http://localhost:2020/weibo/" + weiboid + "> <http://localhost:2020/vocab/weibo_text> \"" + content + "\" }"
    ret = qe.execute(sparql)
    sparql = "insert data {<http://localhost:2020/weibo/" + weiboid + "> <http://localhost:2020/vocab/weibo_date> \"" + post_time + "\" }"
    ret = qe.execute(sparql)

    retdict = {"status": "OK", "msg": "查询成功", "result": []}
    return retdict

def gstore_hit_weibo(offset, size):
    sparql = "select ?s ?o where {?s <http://localhost:2020/vocab/weibo_date> ?o.} order by DESC(?o) limit "+str(size) + " offset " + str(offset)
    ret = qe.execute(sparql)
    retjson = json.loads(ret)
    list_weibo = retjson['results']['bindings']
    result = []
    for weibodata in list_weibo:
        weibourl = weibodata['s']['value']
        time = weibodata['o']['value']
        sparql = "select ?o where {<" + weibourl + "> <http://localhost:2020/vocab/weibo_text> ?o }"
        ret = qe.execute(sparql)
        tmpjson = json.loads(ret)
        content = tmpjson['results']['bindings'][0]['o']['value']
        sparql = "select ?o where {<" + weibourl + "> <http://localhost:2020/vocab/weibo_uid> ?o }"
        ret = qe.execute(sparql)
        tmpjson = json.loads(ret)
        uid = tmpjson['results']['bindings'][0]['o']['value']
        username = _get_username(uid)
        result.append({"username": username, "content": content, "post_time": time})
    retdict = {"status": "OK", "msg": "查询成功", "result": result}
    return retdict

if __name__ == '__main__':
    # ret = gstore_user_register("afucsjker", "123")
    # sparql = """select ?s where {?s ?p "afucsjker".}"""
    # ret = qe.execute(sparql)
    # ret = gstore_user_login("afucsjkfder", "1233")
    # sparql = " select ?s ?p ?o  where {?s ?p ?o . FILTER regex(?o, \"userrelation #1775467263\")}"
    # ret = qe.execute(sparql)
    # sparql = "select ?s  where {?s <http://localhost:2020/vocab/weibo_uid> ?o . FILTER regex(?o, '2452144190')}"
    # sparql = "select ?p ?o where{ <http://localhost:2020/weibo/3708696074833794> <http://localhost:2020/vocab/weibo_date> ?o.    	}"
    # ret = qe.execute(sparql)
    # ret = json.loads(ret)
    # name = _get_username("1914410112")
    # ret = _get_userid("DongShan_")
    # ret = gstore_user_weibo(name, 0, 1)
    # ret = _get_follwee("Jing_Mini_Shop")
    # print(ret)
    # tmp = ret[2]
    # gstore_remove_follow("Jing_Mini_Shop", tmp)
    # ret = _get_follwee("Jing_Mini_Shop")
    # gstore_add_follow("Jing_Mini_Shop", tmp)
    # ret = _get_follwee("Jing_Mini_Shop")
    # ret = gstore_user_weibo("Jing_Mini_Shop")
    # gstore_post_weibo("Jing_Mini_Shop", "sdfajldsjkfl", "lfdskfjioajf")
    # ret = gstore_user_weibo("Jing_Mini_Shop")
    ret = gstore_hit_weibo(0, 10)
    #'2014-04-30T15:53:35'
    print("1")
