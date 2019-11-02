#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template
from flask import request, jsonify
import json
import threading
import datetime
import time
import hashlib
from subprocess import Popen,PIPE
import traceback
import os
import socket

#serverDmain
serverAddress = "iwabuchi.ddns.net"

#port番号
portNum = None

#domainToIpDict
dTi = {}

#debugMode
isLocalhost = False

#pythonコマンド
pythonCommand = "python" #windowsの場合

#URL
URL_root = "/"
URL_mainMenu = URL_root + "mainmenu"
URL_addSubject = URL_root + "addsub"

#HTML Source path
mainMenuHtmlPath = "./mainmanu.html"

#json path
subjectListJsonPath = "./subjectList.json"

#log path
logPath = "./log/mainMenu_{name}.log"

#教科辞書
subjectList = dict()
#jsonからロード
def loadSubject():
    global subjectList
    try:
        with open(subjectListJsonPath,"r",encoding="utf-8_sig") as sublit:
            subjectList = json.load(sublit)
            print(subjectList)
    except FileNotFoundError:
        print("教科リストファイルが存在しないため作成します")
        with open(subjectListJsonPath,"w",encoding="utf-8_sig") as sublit:
            if isLocalhost:
                sublit.write("""{"教科を追加してください":"localhost:81"}""")
            else:
                sublit.write("""{"教科を追加してください":"iwabuchi.ddns.net:81"}""")
            print(subjectList)
    except Exception as e :
        print("教科読み込みエラー:jsonファイル読み込み時にエラーが発生しました。")
        traceback.print_exc()
        exit()
#time
scanInterval = 60 * 60 * 60 #秒指定 定期処理タイマー
liveLimit = 60 * 60 * 60 #秒指定

app = Flask(__name__,template_folder="./")

#問題データセット
problems = object()

#成績辞書
recordDict = {}

#ログ用リスト
logList = []

#連番生成用変数
serialNumber = 0

#サーバープロセス管理用
subServers = []
startedServers = []

#成績データ
class RecordData():
    def __init__(self):
        self.totalAnswers = 0
        self.correctAnswers = 0
        self.wrongAnswers = 0
        self.correctNumber = []
        self.wrongNumber = []
        self.lastAccessTime = datetime.datetime.today()
        self.remoteIP = object()
        self.answers = []
    def getStatistics(self):
        data = [
            self.totalAnswers,
            self.correctAnswers,
            self.wrongAnswers,
            self.correctAnswers / self.totalAnswers,
            self.wrongAnswers / self.totalAnswers
            ]
        return data
    #引数に指定された問題番号の正誤を返す
    def getRorW(self,probNum):
        cIdx = 0 if len(self.correctNumber) > 0 else -1
        wIdx = 0 if len(self.wrongNumber) > 0 else -1
        res = []
        if cIdx != -1 and wIdx != -1:
            cProbNum = self.correctNumber[cIdx]
            wProbNum = self.wrongNumber[wIdx]
            for i in range(self.totalAnswers):
                if cProbNum < wProbNum:
                    #print(cProbNum)
                    res.append(True)
                    if cIdx < len(self.correctNumber)-1:
                        cIdx += 1
                        cProbNum = self.correctNumber[cIdx]
                    else:
                        cProbNum = self.totalAnswers
                else:
                    #print(wProbNum)
                    res.append(False)
                    if wIdx < len(self.wrongNumber)-1:
                        wIdx += 1
                        wProbNum = self.wrongNumber[wIdx]
                    else:
                        wProbNum = self.totalAnswers
        elif cIdx == -1:
            for trash in self.wrongNumber:
                res.append(False)
        elif wIdx == -1:
            for trash in self.correctNumber:
                res.append(True)
        #print(res)
        return res[probNum]


#しばらく使われていないセッションを削除するメソッドその他定期処理
def organize():
    global recordDict
    global adminLog
    global loginLogList
    global logList
    while True:
        time.sleep(scanInterval)
        print("organizeTask")
        #log保存タスク
        print("saveLogTask")
        #整理用辞書
        tmpDict = dict()
        #{IPアドレス:回数}の形式で保存したい
        for ipAddr in logList:
            if ipAddr in tmpDict:
                tmpDict[ipAddr] += 1
            else:
                tmpDict[ipAddr] = 1
        #クリア
        logList.clear()
        #保存用テキスト
        logTextTmplt = "{ip} : {num}\n"
        logText = ""
        #テキスト組み立て
        for ipAddr,tnum in list(tmpDict.items()):
            logText += logTextTmplt.format(ip=ipAddr,num=tnum)
        adminLog = logText
        #保存
        with open(logPath.format(name="{0:%Y-%m-%d_%H-%M-%S}".format(datetime.datetime.today())),mode="w") as l:
            l.write(logText)

subjectListTemp = """\t<tr>\n\t<td>{subName}</td>\n\t<td align="right"><button onclick="location.href='{URL}'" class="btn btn-default">開始</button></td>\n</tr>"""

#メインメニュー表示メソッド
@app.route(URL_mainMenu)
def getMainMenu():
    if not (request.remote_addr in dTi.keys()):
        dTi[request.remote_addr] = reverse_lookup(request.remote_addr)
    print("Access from : ",end="")
    print(dTi[request.remote_addr] if dTi[request.remote_addr] != False else request.remote_addr)

    sessionID = searchForFree(recordDict)
    recordDict[str(sessionID)] = RecordData()
    recordDict[str(sessionID)].remoteIP = request.remote_addr
    logList.append(request.remote_addr)
    subjectListHtml = ""
    for subName,subURL in subjectList.items():
        subjectListHtml += subjectListTemp.format(URL="http://" + subURL,subName=subName) + "\n"
    subjectListHtml += subjectListTemp.format(URL=URL_addSubject,subName="教科更新") + "\n"
    with open(mainMenuHtmlPath,'r',encoding="utf-8_sig") as htso:
        htmlSource = htso.read().format(buttons=subjectListHtml)
    return htmlSource

@app.route("/")
def redirectToMainmenu():
   return "<script> location.href='/mainmenu'</script>"

#サーバー追加用メソッド
@app.route(URL_addSubject)
def addSubjectByWeb():
    loadSubject()
    flg_update = False
    for subName,subURL in subjectList.items():
        if not subName in startedServers:
            url = subURL.split(":")
            subServers.append(Popen([pythonCommand,"server.py",subName,url[1]],stdout=PIPE,stderr=PIPE))
            flg_update = True
            startedServers.append(subName)
    if flg_update:
        print("<h1>教科を更新しました。{subName}を追加</h1>".format(subName=subName))
        return "<h1>教科を更新しました。{subName}を追加</h1>".format(subName=subName) + """<input type="button" class="btn btn-default" onclick="location.href='/mainmenu'" value="メニューに戻る">"""
    else:
        return "<h1>教科の更新はありません。</h1>" + """<input type="button" class="btn btn-default" onclick="location.href='/mainmenu'" value="メニューに戻る">"""
#空きスペースを探してそこのキーを返す
def searchForFree(dic):
    rKeys = dic.keys()
    genKey = 0
    while str(genKey) in rKeys:
        genKey += 1
    return genKey

def reverse_lookup(ip):
    try:
	    return socket.gethostbyaddr(str(ip))[0]
    except:
       return False


if __name__ == '__main__':
    if os.name == "posix":
        pythonCommand += "3"
    print("メインサーバー起動")
    thread = threading.Thread(target=organize)
    thread.daemon = True
    thread.start()
    print("定期処理スタート")
    try:
        loadSubject()
        for subName,subURL in subjectList.items():
            url = subURL.split(":")
            print("> {pycom} server.py {subName} {port}".format(pycom=pythonCommand,subName=subName,port=url[1]))
            subServers.append(Popen([pythonCommand,"server.py",subName,url[1]],stdout=PIPE,stderr=PIPE))
            startedServers.append(subName)
        app.run(threaded = True,debug=False,host="0.0.0.0", port=80)
    except KeyboardInterrupt:
        print("サーバー終了中")
        #ここに終了処理
    except Exception as e:
        traceback.print_exc()
    finally:
        for sub in subServers:
            sub.terminate()
            print("{procName}:終了".format(procName=sub.poll()))
        print("サーバ終了")
