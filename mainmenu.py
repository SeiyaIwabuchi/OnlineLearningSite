#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template
from flask import request, jsonify
import json
import threading
import datetime
import time
import hashlib

#URL
URL_root = "/"
URL_mainMenu = URL_root + "mainmenu"

#HTML Source path
mainMenuHtmlPath = "./mainmanu.html"

#log path
logPath = "./log/mainMenu_{name}.log"

#教科辞書
subjectList = {"":"","Linux":"localhost:81","セキュリティ":"localhost:82"}

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

subjectListTemp = """<option value="{URL}">{subName}</option>"""

#メインメニュー表示メソッド
@app.route(URL_mainMenu)
def getMainMenu():
    sessionID = searchForFree(recordDict)
    recordDict[str(sessionID)] = RecordData()
    recordDict[str(sessionID)].remoteIP = request.remote_addr
    logList.append(request.remote_addr)
    subjectListHtml = ""
    for subName,subURL in subjectList.items():
        subjectListHtml += subjectListTemp.format(URL=subURL,subName=subName) + "\n"
    with open(mainMenuHtmlPath,'r',encoding="utf-8_sig") as htso:
        htmlSource = htso.read().format(subList=subjectListHtml)
    return htmlSource

#空きスペースを探してそこのキーを返す
def searchForFree(dic):
    rKeys = dic.keys()
    genKey = 0
    while str(genKey) in rKeys:
        genKey += 1
    return genKey

if __name__ == '__main__':
    thread = threading.Thread(target=organize)
    thread.daemon = True
    thread.start()
    print("定期処理スタート")
    try:
        app.run(threaded = True,debug=True,host="0.0.0.0", port=80)
    except KeyboardInterrupt:
        print("サーバー終了中")
        #ここに終了処理
    finally:
        print("サーバ終了")
