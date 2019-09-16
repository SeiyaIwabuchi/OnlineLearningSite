# make_responseをインポート
from flask import Flask, make_response
from datetime import datetime
# requestをインポート
from flask import request

sNum = 0

def getSerialNum():
    global sNum
    sNum += 1
    return sNum - 1


app = Flask(__name__)
@app.route('/')
def index():
    uid = request.cookies.get('uid', None)
    retStr = ""
    if uid == None:
        uid = str(getSerialNum())
        retStr = "<h1>新規ユーザー様ですね。ユーザーID:{uid}を付与します。</h1>".format(uid=uid)
    else:
        retStr = "<h1>{uid}様ですね。</h1>".format(uid=uid)

    # make_responseでレスポンスオブジェクトを生成する
    response = make_response(retStr)

    # Cookieの設定を行う
    max_age = 60 * 60 * 24 * 120 # 120 days
    expires = int(datetime.now().timestamp()) + max_age
    response.set_cookie('uid', value=uid, max_age=max_age, expires=expires, path='/', secure=None, httponly=False)

    # レスポンスを返す
    return response

@app.route('/foo')
def foo():
    # requestオブジェクトからCookieを取得する
    uid = request.cookies.get('uid', None)
    # 以下省略
    retStr = ""
    if uid == None:
        retStr = "<h1>新規ユーザー様ですね。</h1>"
    else:
        retStr = "<h1>{uid}様ですね。</h1>".format(uid=uid)
    return retStr

app.run(threaded = True,debug=False,host="0.0.0.0", port=80)