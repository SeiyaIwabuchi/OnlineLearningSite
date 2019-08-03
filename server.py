#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template
from flask import request, jsonify
import json
import threading
import datetime
import time
import hashlib


#HTML Source path
htmlSourcePath = "./index.html"
resultSourcePath = "./result.html"
problemsFilePath = "./problems.json"
problemListHtmlSource = "./ProblemList.html"
adminHtmlSource = "./admin.html"
loginFromHtmlPath = "./auth.html"

#log path
logPath = "./log/{name}.log"
loginLogPath = "./log/login_{name}.log"

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

#ログインログ用辞書リスト
loginLogList = []


#管理画面ログ格納用
adminLog = ""

#ログインセッションリスト
loginSessionDict = {}

#連番生成用変数
serialNumber = 0

#ログインセッションデータセット
class LoginDataSet():
   def __init__(self,rmIP):
      self.lastAccessTime = datetime.datetime.today()
      self.loginAvailability = False
      self.remoteIP = rmIP
      self.hashedSerialNumber = ""

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

#jqueryでif文で必ず回答しないと送信できないようにする。  

#問題はjsonにする
#問題データ読み込み
def loadproblemsFromJson():
   global problems
   try:
      with open(problemsFilePath,"r",encoding="utf-8_sig") as prob:
         problems = json.load(prob)
      checkProblems()
      print("問題に問題はありませんでした。")
      return True,""
   except ProblemError:
      print("問題に問題がありました。")
      return False,"JSONデータに不備があります。"

#jsonデータのチェック
def checkProblems():
   for p in problems:
      if not p["正答"].isnumeric():
         raise ProblemError
#上の独自例外
class ProblemError(Exception):
   def __init__(self):
      print("JSONデータの正答欄に不備があります。正答欄には1~4の半角数字を入力できます。")

#htmlに問題データを乗せる(最初だけ)
def problemWritingToHtml(problemNum,htmlSource,sessionID):
   tmpDict = problems[problemNum]
   #print(tmpDict)
   htmlSource = htmlSource.format(
      problem = tmpDict["問題"],
      choices1 = tmpDict["選択肢1"],
      choices2 = tmpDict["選択肢2"],
      choices3 = tmpDict["選択肢3"],
      choices4 = tmpDict["選択肢4"],
      RorW = "",
      correct = "",
      sessionID = str(sessionID),
      comment = ""
      )
   return htmlSource

def raidoRes2Number(radioRes):
   for index,b in enumerate(radioRes):
      if b:
         return index

#
def judgment(problemNum,choice):
   if(int(problems[problemNum]["正答"]) == choice+1):
      return True
   else:
      return False

@app.route('/')
def index():
   sessionID = searchForFree(recordDict)
   recordDict[str(sessionID)] = RecordData()
   recordDict[str(sessionID)].remoteIP = request.remote_addr
   logList.append(request.remote_addr)
   with open(htmlSourcePath,'r',encoding="utf-8_sig") as htso:
      #htmlSource = htso.read().format(sessionID = int(sessions[len(sessions)-1]))
      htmlSource = htso.read()
      htmlSource = problemWritingToHtml(0,htmlSource,sessionID)
   return htmlSource

@app.route('/postText', methods=['POST'])
def receiveAnswer():
   #回答するを押したときの動作
   radioRes = []
   for i in range(4):
      radioRes.append(request.json['radio%d'%(i+1)])
   #print("sessionID : " + request.json["sessionID"],end=" ")
   #print("SelecedNumber : " + str(raidoRes2Number(radioRes)),end="")
   #print("problemNumber : " + str(request.json["probNum"]))

   RorW = judgment(request.json["probNum"],raidoRes2Number(radioRes))
   recordDict[request.json["sessionID"]].totalAnswers += 1
   recordDict[request.json["sessionID"]].lastAccessTime = datetime.datetime.today()
   if RorW:
      recordDict[request.json["sessionID"]].correctAnswers += 1
      recordDict[request.json["sessionID"]].correctNumber.append(int(request.json["probNum"]))
   else:
      recordDict[request.json["sessionID"]].wrongAnswers += 1
      recordDict[request.json["sessionID"]].wrongNumber.append(int(request.json["probNum"]))
   
   return_data = {
      "RorW":RorW,
      "correct":problems[int(request.json["probNum"])]["選択肢" + problems[int(request.json["probNum"])]["正答"]],
      "comment":problems[int(request.json["probNum"])]["解説"] if problems[int(request.json["probNum"])]["解説"] != "" else "特になし"
      }
   return jsonify(ResultSet=json.dumps(return_data))

#次の問題をクリックされた時のメソッド
@app.route('/nextPoroblem', methods=['POST'])
def nextPoroblem():
   #サーバー側では問題jsonの組み立てを行う
   probNum = request.json["requestProblem"]
   try:
      problemJson = {
         "problem":problems[probNum]["問題"],
         "choice1":problems[probNum]["選択肢1"],
         "choice2":problems[probNum]["選択肢2"],
         "choice3":problems[probNum]["選択肢3"],
         "choice4":problems[probNum]["選択肢4"],
         "finsh":"false"
      }
   except IndexError:
      #次の問題がないときはIndexErrorとなる
      problemJson = {
         "problem":"",
         "choice1":"",
         "choice2":"",
         "choice3":"",
         "choice4":"",
         "finsh":"true"
      }
   finally:
      #print(problemJson)
      return jsonify(ResultSet=json.dumps(problemJson))

#結果表示用メソッド
"""
data = [ 
         self.totalAnswers,
         self.correctAnswers,
         self.wrongAnswers,
         self.correctAnswers / self.totalAnswers,
         self.wrongAnswers / self.totalAnswers
         ]
"""
@app.route("/result/<sessionID>")
def setResult(sessionID=None):
   try:
      resultData = recordDict[sessionID].getStatistics()
      resultHtmlTmp = "\
      <tr>\n\
         {trText}\n\
      </tr>\
      "
      tdTagTmp = "<td>{rdText}</td>\n"
      htmlResultTable = ""
      #print("SessionID : " + sessionID)
      #print(recordDict[sessionID].correctNumber)
      #print(recordDict[sessionID].wrongNumber)
      for i in range(resultData[0]):
         htmlResultTable += resultHtmlTmp.format(trText = tdTagTmp.format(rdText = problems[i]["問題"]) + tdTagTmp.format(rdText = "○" if recordDict[sessionID].getRorW(i) == True else "×"))
      with open(resultSourcePath,'r',encoding="utf-8_sig") as htso:
         htmlSource = htso.read().format(
            sID = sessionID,
            probNum = resultData[0],
            corrNum = resultData[1],
            wrongNum = resultData[2],
            corrRate = str(float(resultData[3])*100) + "%",
            wrongRate = str(float(resultData[4])*100) + "%",
            resultTable = resultHtmlTmp.format(trText = htmlResultTable)
            )
      return htmlSource
   except KeyError:
      ret = "<h1>指定されたページは存在しません</h1>"
      return ret
   except ZeroDivisionError:
      ret = "<h1>指定されたページは存在しません</h1>"
      return ret

#問題一覧表示用
@app.route("/ProblemList.html")
def getProblemList():
   resultHtmlTmp = "\
   <tr>\n\
      {trText}\n\
   </tr>\
   "
   tdTagTmp = "<td>{rdText}</td>\n"
   htmlResultTable = ""
   for p in problems:
      htmlResultTable += resultHtmlTmp.format(trText = \
         tdTagTmp.format(rdText = p["番号"])  + \
         tdTagTmp.format(rdText = p["問題"])  + \
         tdTagTmp.format(rdText = p["選択肢" + p["正答"]]) \
      )
   with open(problemListHtmlSource,'r',encoding="utf-8_sig") as htso:
      htmlSource = htso.read().format(
         resultTable = resultHtmlTmp.format(trText = htmlResultTable)
         )
   return htmlSource

#管理用画面表示
@app.route("/admin.html/<hashedValue>")
def getAdmin(hashedValue=None):
   loginAvailability = False
   for lsd in list(loginSessionDict.values()):
      if lsd.hashedSerialNumber == hashedValue:
         loginAvailability = True
   if loginAvailability:
      htmlSource = ""
      with open(adminHtmlSource,'r',encoding="utf-8_sig") as htso:
         htmlSource = htso.read()
      return htmlSource.format(log=adminLog)
   else:
      return "<h1>認証エラー</h1>"

#ファイルアップロードメソッド
@app.route("/upProblem", methods=['POST'])
def upProblem():
   the_file = request.files['file_1']
   the_file.save("./" + the_file.filename) #自動で上書きされる
   resultB,msg = loadproblemsFromJson()
   return the_file.filename + "がアップロードされ、問題の更新が" + "成功" if resultB else "失敗" + "しました。" + msg

#ログイン認証画面
@app.route("/login")
def login():
   sessionID = searchForFree(loginSessionDict)
   loginSessionDict[str(sessionID)] = LoginDataSet(request.remote_addr)
   logList.append(request.remote_addr) #ログイン試行なのか問題を解きに来ただけなのか区別する必要がある。
   htmlSource = ""
   with open(loginFromHtmlPath,mode="r",encoding="utf-8_sig") as htso:
      htmlSource = htso.read().format(sID=str(sessionID))
   return htmlSource

#ログインログ用辞書を返すメソッド
def createLoginLogDict(date,IPaddr,loginID,passwd,available,hashedSerial):
   return {"date":date,"IPaddr":IPaddr,"loginID":loginID,"passwd":passwd,"available":available,"hashedSerial":hashedSerial}

#ログイン認証処理
@app.route("/auth",methods=['POST'])
def auth():
   global serialNumber
   global loginLogList
   loginID = "seiya"
   passwd = "nN49KOMDK"
   retJson = {}
   print(request.json)
   if request.json["loginID"] == loginID and request.json["pass"] == passwd:
      print("ログイン成功")
      retJson["Result"] = "True"
      loginSessionDict[request.json["sessionID"]].loginAvailability = True
      loginSessionDict[request.json["sessionID"]].hashedSerialNumber = hashlib.sha256(str(serialNumber).encode()).hexdigest()
      serialNumber += 1
      retJson["adminURL"] = "/admin.html/" + loginSessionDict[request.json["sessionID"]].hashedSerialNumber
   else:
      print("ログイン失敗")
      retJson["Result"] = "False"
      retJson["adminURL"] = ""
   print(retJson)
   loginLogList.append(createLoginLogDict(
      datetime.datetime.now(),\
      request.remote_addr,\
      request.json["loginID"],\
      request.json["pass"],\
      False if retJson["Result"] == "False" else True,\
      retJson["adminURL"][11:]\
      ))
   return jsonify(ResultSet=json.dumps(retJson))

#しばらく使われていないセッションを削除するメソッドその他定期処理
def organize():
   global recordDict
   global adminLog
   global loginLogList
   global logList
   while True:
      time.sleep(scanInterval)
      print("organizeTask")
      for n,s in list(recordDict.items()):
         if datetime.datetime.today() - s.lastAccessTime >= datetime.timedelta(seconds=liveLimit):
            print(s.remoteIP + " is deleted.")
            recordDict.pop(n)
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
      #ログイン試行ログの保存
      #何時何分に誰（IP）がログインID＋パスワードでログインを試みたかを残しておく
      loginLogFormat = "{date} : [{IPaddr}] ID={loginID}, PASS={passwd}, available={avl},hashedSerial={hsdSerl}\n"
      #{"date":date,"IPaddr":IPaddr,"loginID":loginID,"passwd":passwd,"available":available,"hashedSerial":hashedSerial}
      loginLogText = ""
      for lll in loginLogList:
         loginLogText += loginLogFormat.format(
            date = lll["date"],
            IPaddr = lll["IPaddr"],
            loginID = lll["loginID"],
            passwd = lll["passwd"],
            avl = lll["available"],
            hsdSerl = lll["hashedSerial"]
         )
      #クリア
      loginLogList.clear()
      with open(loginLogPath.format(name="{0:%Y-%m-%d_%H-%M-%S}".format(datetime.datetime.today())),mode="w") as l:
         l.write(loginLogText)

@app.route("/deleteAdminURL/<palmt>")
def deleteAdminURL(palmt=None):
   print(palmt)

#空きスペースを探してそこのキーを返す
def searchForFree(dic):
   rKeys = dic.keys()
   genKey = 0
   while str(genKey) in rKeys:
      genKey += 1
   return genKey

if __name__ == '__main__':
   loadproblemsFromJson()
   thread = threading.Thread(target=organize)
   thread.start()
   app.run(threaded = True,debug=True,host="0.0.0.0", port=80)