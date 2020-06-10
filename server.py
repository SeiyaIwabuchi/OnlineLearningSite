#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, make_response
from flask import request, jsonify, send_file
import json
import threading
import datetime
import time
import hashlib
import sys
import random
import math
import pickle
import socket

#教科管理用
startedServers = []

#教科一覧のテンプレート
subjectListTemp = """\t<tr>\n\t<td>{subName}</td>\n\t<td align="right"><button onclick="location.href='{URL}'" class="btn btn-secondary" id="{subName2}">開始</button></td>\n</tr>"""
subjectMngListTemp = "\
   <tr>\
      <td>{subName}</td>\
      <td align=\"right\">\
            <input type=\"text\" id=\"{subText}\"></input>\
      </td>\
      <td align=\"right\">\
            <button  class=\"btn btn-secondary mngButton\" id=\"{subMod}\">変更</button>\
      </td>\
      <td align=\"right\">\
         <button class=\"btn btn-secondary mngButton\" id=\"{subDel}\">削除</button>\
      </td>\
   </tr>"
#問題編集用テンプレ
problemPullDownTemp = "<option value=\"{subName}\">{subName}</option>"
problemMngListTemp = "\
   <tr>\
      <td>{no}</td>\
      <td>{prob}</td>\
      <td class=\"ButtonSell\">\
         <button  class=\"btn btn-secondary mngButton\" id=\"{probMod}\">変更</button>\
         <button class=\"btn btn-secondary mngButton\" id=\"{probDel}\">削除</button>\
      </td>\
   </tr>"

#serverDmain
serverAddress = "iwabuchi.ddns.net"

#portNum
portNum = None

#domainToIpDict
dTi = {}

#問題更新日時
problemUpdateTime = datetime.datetime.now()

#debugMode
isLocalhost = False

#sessionクラス
class Session:
   NoSession = "NoSession"
   sessionID = "sessionID"

#ログインセッションデータセット
class LoginDataSet():
   def __init__(self,rmIP):
      self.lastAccessTime = datetime.datetime.today()
      self.loginAvailability = False
      self.remoteIP = rmIP
      self.hashedSerialNumber = ""

#成績データ
class RecordData():
   def __init__(self,subName,shuffle=True):
      self.totalAnswers = 0
      self.correctAnswers = 0
      self.wrongAnswers = 0
      self.correctNumber = []
      self.wrongNumber = []
      self.lastAccessTime = datetime.datetime.today()
      self.remoteIP = ""
      self.answers = []
      self.problemNumberList = [] #出題する問題の並びを制御する
      self.subName = subName
      if shuffle:
        self.shuffle()
      self.cookieCreateTime = datetime.datetime.now()
   def getStatistics(self):
      data = [
         self.totalAnswers,
         self.correctAnswers,
         self.wrongAnswers,
         self.correctAnswers / self.totalAnswers,
         self.totalAnswers / len(problems[self.subName])
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
   def normalSequence(self):
      for i in range(len(problems[self.subName])):
         self.problemNumberList.append(i)
   def shuffle(self):
      self.normalSequence()
      i = len(problems[self.subName]) - 1
      while (i > 0):
         j = math.floor(random.random() * (i + 1))
         swap = self.problemNumberList[i]
         self.problemNumberList[i] = self.problemNumberList[j]
         self.problemNumberList[j] = swap
         i = (i - 1)
      self.problemNumberList.append(len(problems[self.subName]))

#URL
URL_root = "/"
URL_answerRequest = URL_root + "<subName>/postText"
URL_nextProblem = URL_root + "<subName>/nextPoroblem"
URL_result = URL_root + "<subName>/result"
URL_ProblemList = URL_root + "<subName>/ProblemList.html"
URL_admin = URL_root + "adminTop/<hashedValue>"
URL_upProblem = URL_root + "<subName>/upProblem"
URL_login = URL_root + "/login"
URL_auth = URL_root + "auth"
URL_deleteAdminURL = URL_root + "deleteAdminURL/<palmt>"
URL_mainMenu = URL_root + "mainmenu"
URL_deleteRecord = URL_root + "<subName>/deleteRecord"
URL_updateCookie = URL_root + "<subName>/updateCookie"
URL_problemJsonDownload = URL_root + "<subName>/problemJsonDownload"
URL_onlyMistakes = URL_root + "<subName>/onlyMistakes"
#教科管理URL
URL_manageSubject = URL_root + "mngSubject/<hashedValue>"
URL_editSubject = URL_root + "mngSubject/<hashedValue>/<mode>/<subName>/<aSubName>"
#問題管理URL
URL_manageProblem = URL_root + "mngProblem/<hashedValue>/<subName>"
URL_editProblem = URL_root + "mngProblem/<hashedValue>/<subName>/<mode>/<probNo>"
#問題編集URL(POSTのURL)
URL_editProblemPost = URL_root + "<hashedValue>/posting"

#HTMLソースパス
htmlSourcePath = "./index.html"
resultSourcePath = "./result.html"
problemListHtmlSource = "./ProblemList.html"
adminHtmlSource = "./mngTop.html"
loginFromHtmlPath = "./auth.html"
mainMenuHtmlPath = "./mainmanu.html"
mngSubjHtmlPath = "./mngSubj.html"
mngProblemjHtmlPath = "./mngProblem.html"
mngProblemEditorjHtmlPath = "./problemEdit.html"

#log path
logPath = "./log/{name}.log"
loginLogPath = "./log/login_{name}.log"

#time
scanInterval = 60 * 60 #秒指定 定期処理タイマー
liveLimit = 60 * 60  * 24 * 120 #秒指定

#サーバーインスタンス
app = Flask(__name__,template_folder="./")

#教科名
subjectNameList = []

#問題jsonパス
problemsFilePathTemp = "./problems_{subjectName}.json"
problemsFilePathsDict = {}

#教科リストファイルパス
subjectNameListPath = "./subjectList.json"

#問題データセット
problems = {}

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

#jqueryでif文で必ず回答しないと送信できないようにする。  

#問題はjsonにする
#問題データ読み込み
def loadproblemsFromJson():
   global problems
   global problemUpdateTime
   global startedServers
   for subName in subjectNameList:
      try:
         with open(problemsFilePathsDict[subName],"r",encoding="utf-8-sig") as prob:
            problems[subName] = json.load(prob)
         checkProblems(subName)
         print("{}:問題に問題はありませんでした。".format(subName))
         problemUpdateTime = datetime.datetime.now()
         print(problemUpdateTime)
         startedServers.append(subName)
      except ProblemError:
         print("{}:問題に問題がありました。".format(subName),file=sys.stderr)
      except FileNotFoundError:
         print("{sn}:問題ファイル:{probName}がありませんでした。ファイルを作成します。".format(sn=subName,probName=problemsFilePathsDict[subName],file=sys.stderr))
         with open(problemsFilePathsDict[subName],mode="w",encoding="utf-8-sig") as probJson:
            probJson.write("""[{"番号":"1","問題":"問題ファイルを更新してください","選択肢1":"管理者に連絡する","選択肢2":"自分で更新する","選択肢3":"サーバーをぶっ壊す","選択肢4":"寝る","正答":"3","解説":"回答しても何も起きませんよ。"}]""")
         loadproblemsFromJson()

#jsonデータのチェック
def checkProblems(subName):
   for p in problems[subName]:
      if not p["正答"].isnumeric():
         raise ProblemError
#上の独自例外
class ProblemError(Exception):
   def __init__(self):
      print("JSONデータの正答欄に不備があります。正答欄には1~4の半角数字を入力できます。",file=sys.stderr)

#htmlに問題データを乗せる(最初だけ)
def problemWritingToHtml(problemNum,htmlSource,sessionID,subName):
   try:
      tmpDict = problems[subName][problemNum]
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
         comment = "",
         subName=subName
         )
      return htmlSource
   except IndexError:
      return "<script> location.href='/" + subName + "/result'; </script>"
   #except KeyError:
   #   return "<script> alert(\"指定されたページまたは教科は存在しません。\"); location.href=\"/\"</script>"
   

def raidoRes2Number(radioRes):
   for index,b in enumerate(radioRes):
      if b:
         return index

#回答時に呼び出される。正誤を返す。
def judgment(problemNum,choice,subName):
   if(int(problems[subName][problemNum]["正答"]) == choice+1):
      return True
   else:
      return False

#メインメニュー表示メソッド
@app.route("/mainmenu")
def getMainMenu():
   #IPアドレスの関係
   if not (request.remote_addr in dTi.keys()):
      dTi[request.remote_addr] = reverse_lookup(request.remote_addr)
   print("Access from : ",end="")
   print(dTi[request.remote_addr] if dTi[request.remote_addr] != False else request.remote_addr)
   #ログ
   logList.append(request.remote_addr)
   subjectListHtml = ""
   for subName in subjectNameList:
      subjectListHtml += subjectListTemp.format(URL="/" + subName,subName=subName,subName2=subName) + "\n"
   with open(mainMenuHtmlPath,'r',encoding="utf-8-sig") as htso:
      htmlSource = htso.read().format(buttons=subjectListHtml)
   return htmlSource

@app.route("/")
def redirectToMainmenu():
   return "<script> location.href='/mainmenu'</script>"

@app.route("/<subName>")
def index(subName=None):
   #IPアドレスの関係
   if not (request.remote_addr in dTi.keys()):
      dTi[request.remote_addr] = reverse_lookup(request.remote_addr)
   else:
      print("Access from : ",end="")
      print(dTi[request.remote_addr] if dTi[request.remote_addr] != False else request.remote_addr,end=" ,IP : ")
      print(request.remote_addr)
   #セッション管理の関係
   sessionID = request.cookies.get(Session.sessionID,Session.NoSession)
   if sessionID == Session.NoSession or not (sessionID in recordDict.keys()):
      #新規ユーザーへの処理
      print("new user")
      sessionID = searchForFree(recordDict)
      recordDict[str(sessionID)] = RecordData(subName)
   elif recordDict[sessionID].cookieCreateTime < problemUpdateTime: #念のために10秒進める。
      print("old user")
      sdkjs = """問題が更新されました。\\n新しい問題を回答しますか？\\n(新しい問題に切り替えると進捗がすべて消えます。\\n現在の回答終了後に「最初から始める」から更新後の問題を解くことができます。)""".encode("shift_jis").decode("shift_jis")
      return "\
         <script>\
            if(window.confirm(\""+sdkjs+"\")){\
               location.href = '/" + subName + "/deleteRecord'\
            }else{\
               location.href = '/" + subName + "/updateCookie'\
            }\
         </script>\
      "
   #ロギング
   recordDict[str(sessionID)].remoteIP = request.remote_addr
   logList.append(request.remote_addr)

   probNum = recordDict[str(sessionID)].problemNumberList[recordDict[str(sessionID)].totalAnswers]

   #クライアントへの返答
   with open(htmlSourcePath,'r',encoding="utf-8-sig") as htso:
      htmlSource = htso.read()
      htmlSource = problemWritingToHtml(probNum,htmlSource,sessionID,subName)
      response = make_response(htmlSource)
      # Cookieの設定を行う
      max_age = liveLimit
      expires = int(datetime.datetime.now().timestamp()) + max_age
      response.set_cookie(Session.sessionID, value=str(sessionID), max_age=max_age, expires=expires, path='/', secure=None, httponly=False)
   return response

#回答するを押したときの動作
@app.route(URL_answerRequest, methods=['POST'])
def receiveAnswer(subName=None):
   radioRes = []
   sessionID = request.cookies.get(Session.sessionID,None)
   probNum = recordDict[str(sessionID)].problemNumberList[recordDict[str(sessionID)].totalAnswers]
   oldProbNum = recordDict[str(sessionID)].problemNumberList[recordDict[str(sessionID)].totalAnswers]
   
   for i in range(4):
      radioRes.append(request.json['radio%d'%(i+1)])

   recordDict[sessionID].answers.append(raidoRes2Number(radioRes))
   RorW = judgment(probNum,recordDict[sessionID].answers[len(recordDict[sessionID].answers)-1],subName)
   recordDict[sessionID].totalAnswers += 1
   recordDict[sessionID].lastAccessTime = datetime.datetime.today()
   if RorW:
      recordDict[sessionID].correctAnswers += 1
      recordDict[sessionID].correctNumber.append(recordDict[str(sessionID)].totalAnswers-1)
   else:
      recordDict[sessionID].wrongAnswers += 1
      recordDict[sessionID].wrongNumber.append(recordDict[str(sessionID)].totalAnswers-1)

   return_data = {
      "RorW":RorW,
      "correct":problems[subName][oldProbNum]["選択肢" + problems[subName][oldProbNum]["正答"]],
      "comment":problems[subName][oldProbNum]["解説"] if problems[subName][oldProbNum]["解説"] != "" else "特になし"
      }
   return jsonify(ResultSet=json.dumps(return_data))

#次の問題をクリックされた時のメソッド
@app.route(URL_nextProblem, methods=['POST'])
def nextPoroblem(subName=None):
   #サーバー側では問題jsonの組み立てを行う
   sessionID = request.cookies.get(Session.sessionID,None)
   try:
      probNum = recordDict[str(sessionID)].problemNumberList[recordDict[str(sessionID)].totalAnswers]
      problemJson = {
         "problem":problems[subName][probNum]["問題"],
         "choice1":problems[subName][probNum]["選択肢1"],
         "choice2":problems[subName][probNum]["選択肢2"],
         "choice3":problems[subName][probNum]["選択肢3"],
         "choice4":problems[subName][probNum]["選択肢4"],
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
@app.route(URL_result)
def setResult(subName):
   sessionID = request.cookies.get(Session.sessionID,None)
   try:
      resultData = recordDict[sessionID].getStatistics()
      resultHtmlTmp = "\
      <tr>\n\
         {trText}\n\
      </tr>\
      "
      tdTagTmp = "<td>{rdText}</td>\n"
      htmlResultTable = ""
      for i in range(recordDict[sessionID].totalAnswers):
         probNum = recordDict[sessionID].problemNumberList[i]
         htmlResultTable += resultHtmlTmp.format(trText = tdTagTmp.format(rdText = problems[subName][probNum]["問題"]) + tdTagTmp.format(rdText = problems[subName][probNum]["選択肢" + str(recordDict[sessionID].answers[i]+1)]) + tdTagTmp.format(rdText = "○" if recordDict[sessionID].getRorW(i) == True else "×"))
      with open(resultSourcePath,'r',encoding="utf-8-sig") as htso:
         htmlSource = htso.read().format(
            sID = sessionID,
            probNum = resultData[0],
            corrNum = resultData[1],
            wrongNum = resultData[2],
            corrRate = str(float(resultData[3])*100)[:5] + "%",
            wrongRate = str(float(resultData[4])*100)[:5] + "%",
            resultTable = resultHtmlTmp.format(trText = htmlResultTable),
            subName=subName
            )
      return htmlSource
   except KeyError:
      ret = "<h1>指定されたページは存在しません</h1>"
      return ret
   except ZeroDivisionError:
      ret = "<h1>指定されたページは存在しません</h1>"
      return ret

#問題一覧表示用
@app.route(URL_ProblemList)
def getProblemList(subName=None):
   resultHtmlTmp = "\
   <tr>\n\
      {trText}\n\
   </tr>\
   "
   tdTagTmp = "<td>{rdText}</td>\n"
   htmlResultTable = ""
   for p in problems[subName]:
      htmlResultTable += resultHtmlTmp.format(trText = \
         tdTagTmp.format(rdText = p["番号"])  + \
         tdTagTmp.format(rdText = p["問題"])  + \
         tdTagTmp.format(rdText = p["選択肢" + p["正答"]]) \
      )
   with open(problemListHtmlSource,'r',encoding="utf-8-sig") as htso:
      htmlSource = htso.read().format(
         resultTable = resultHtmlTmp.format(trText = htmlResultTable),
         subName=subName
         )
   return htmlSource

#管理用画面表示
@app.route(URL_admin)
def getAdmin(hashedValue=None,subName=None):
   loginAvailability = False
   for lsd in list(loginSessionDict.values()):
      if lsd.hashedSerialNumber == hashedValue:
         loginAvailability = True
   if loginAvailability:
      htmlSource = ""
      with open(adminHtmlSource,'r',encoding="utf-8-sig") as htso:
         htmlSource = htso.read()
      return htmlSource.format(log=adminLog,subName=subName)
   else:
      return "<h1>認証エラー</h1>"

#ファイルアップロードメソッド
@app.route(URL_upProblem, methods=['POST'])
def upProblem(subName=None):
   the_file = request.files['file_1']
   the_file.save(problemsFilePathsDict[subName]) #自動で上書きされる
   loadproblemsFromJson()
   return the_file.filename + "がアップロードされ、問題の更新がリロードされました"
#ログイン認証画面
@app.route(URL_login)
def login():
   sessionID = searchForFree(loginSessionDict)
   loginSessionDict[str(sessionID)] = LoginDataSet(request.remote_addr)
   logList.append(request.remote_addr) #ログイン試行なのか問題を解きに来ただけなのか区別する必要がある。
   htmlSource = ""
   with open(loginFromHtmlPath,mode="r",encoding="utf-8-sig") as htso:
      htmlSource = htso.read().format(sID=str(sessionID),subName=None)
   return htmlSource

#ログインログ用辞書を返すメソッド
def createLoginLogDict(date,IPaddr,loginID,passwd,available,hashedSerial):
   return {"date":date,"IPaddr":IPaddr,"loginID":loginID,"passwd":passwd,"available":available,"hashedSerial":hashedSerial}

#ログイン認証処理
@app.route(URL_auth,methods=['POST'])
def auth():
   global serialNumber
   global loginLogList
   loginID = "0af7aa0126b5ac4a701c0088a4acdb21b478c2ed1560349656758001575542f0"
   passwd = "ff0c4171b80ea5297040caf898228b6e7e7fc6002caf1dd932de99b036f6f0c3"
   retJson = {}
   print(request.json)
   if request.json["loginID"] == loginID and request.json["pass"] == passwd:
      print("ログイン成功")
      retJson["Result"] = "True"
      loginSessionDict[request.json["sessionID"]].loginAvailability = True
      loginSessionDict[request.json["sessionID"]].hashedSerialNumber = hashlib.sha256(str(serialNumber).encode()).hexdigest()
      serialNumber += 1
      retJson["adminURL"] = "/adminTop/" + loginSessionDict[request.json["sessionID"]].hashedSerialNumber
   else:
      print("ログイン失敗")
      retJson["Result"] = "False"
      retJson["adminURL"] = ""
   print(retJson)
   try:
      loginLogList.append(createLoginLogDict(
         datetime.datetime.now(),\
         dTi[request.remote_addr] if dTi[request.remote_addr] != False else request.remote_addr,\
         request.json["loginID"],\
         request.json["pass"],\
         False if retJson["Result"] == "False" else True,\
         retJson["adminURL"][11:]\
      ))
   except KeyError:
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
            tmpDict[dTi[ipAddr] if dTi[ipAddr] != False else ipAddr] += 1
         else:
            tmpDict[dTi[ipAddr] if dTi[ipAddr] != False else ipAddr] = 1
      #クリア
      logList.clear()
      #保存用テキスト
      logTextTmplt = "{ip} : {num}\n"
      logText = ""
      #テキスト組み立て
      for ipAddr,tnum in list(tmpDict.items()):
         logText += logTextTmplt.format(ip=ipAddr,num=tnum)
      adminLog = logText
      #保存 何もないなら保存しない
      if logText != "":
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
      if loginLogText != "":
         with open(loginLogPath.format(name="{0:%Y-%m-%d_%H-%M-%S}".format(datetime.datetime.today())),mode="w") as l:
            l.write(loginLogText)

#ブラウザを閉じるときにアクセスURL辞書から削除する
@app.route(URL_deleteAdminURL)
def deleteAdminURL(palmt=None):
   hsn = str(palmt)
   for lsd_key,lsd_value in list(loginSessionDict.items()):
      if lsd_value.hashedSerialNumber == hsn:
         loginSessionDict.pop(lsd_key)
         print(palmt + " is deleted.")
   return ""

#空きスペースを探してそこのキーを返す
def searchForFree(dic):
   rKeys = dic.keys()
   genKey = 0
   while str(genKey) in rKeys:
      genKey += 1
   return genKey


#教科一覧を読み込む
def loadSubjects():
   global subjectNameList
   try:
      with open(subjectNameListPath,"r",encoding="utf-8-sig") as snlp:
         subjectNameList = json.load(snlp)
   except FileNotFoundError:
      print("subjectList.jsonが見つかりません。作成します。")
      with open(subjectNameListPath,"w",encoding="utf-8-sig") as snlp:
         snlp.write("[]")
      with open(subjectNameListPath,"r",encoding="utf-8-sig") as snlp:
         subjectNameList = json.load(snlp)

def main():
   global problemsFilePathsDict
   global recordDict
   global serialNumber
   global portNum
   print("サーバー起動")
   loadSubjects()
   for subName in subjectNameList:
      problemsFilePathsDict[subName] = problemsFilePathTemp.format(subjectName=subName)
   loadproblemsFromJson()
   thread = threading.Thread(target=organize)
   thread.daemon = True
   thread.start()
   print("定期処理スタート")
   try:
      with open("./recordDic.bin","rb") as rd:
         recordDict = pickle.load(rd)
      with open("./serialNumber.bin","rb") as rd:
         serialNumber = pickle.load(rd)
   except FileNotFoundError:
      pass
   except EOFError:
      pass
   try:
      app.run(threaded = True,debug=True,host="0.0.0.0", port=80)
   except KeyboardInterrupt:
      print("サーバー終了中",file=sys.stderr)
      #ここに終了処理
   finally:
      with open("./recordDic.bin","wb") as rd:
         pickle.dump(recordDict,rd)
      with open("./serialNumbersu.bin","wb") as rd:
         pickle.dump(serialNumber,rd)
      print("サーバ終了",file=sys.stderr)

@app.after_request
def add_header(r):
   """
   Add headers to both force latest IE rendering engine or Chrome Frame,
   and also to cache the rendered page for 10 minutes.
   """
   r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
   r.headers["Pragma"] = "no-cache"
   r.headers["Expires"] = "0"
   r.headers['Cache-Control'] = 'public, max-age=0'
   return r

@app.route(URL_deleteRecord)
def deleteRecord(subName=None):
   global recordDict
   sessionID = request.cookies.get(Session.sessionID,None)
   recordDict[sessionID] = RecordData(recordDict[sessionID].subName)
   return "<script> location.href='/" + subName + "' </script>"

@app.route("/test")
def testFunc():
   sessionID = request.cookies.get(Session.sessionID,None)
   return  str(recordDict[str(sessionID)].problemNumberList)

@app.route(URL_updateCookie)
def updateCookie(subName=None):
   global recordDict
   sessionID = request.cookies.get(Session.sessionID,None)
   recordDict[sessionID].cookieCreateTime = datetime.datetime.now()
   return "<script> location.href='/" + subName + "' </script>"

@app.route(URL_problemJsonDownload)
def problemJsonDownload(subName=None):
   return send_file(problemsFilePathsDict[subName])

def reverse_lookup(ip):
	try:
		return socket.gethostbyaddr(str(ip))[0]
	except:
		return False

@app.route(URL_onlyMistakes)
def onlyMistakes(subName=None):
    global recordDict
    sessionID = request.cookies.get(Session.sessionID,None)
    mistakeProb = ""
    tmpProbList = recordDict[str(sessionID)].problemNumberList.copy()
    tmpWrongList = recordDict[str(sessionID)].wrongNumber
    if len(tmpWrongList) > 0:
        recordDict[str(sessionID)] = RecordData(subName,shuffle=False)
        for Num in tmpWrongList:
            recordDict[str(sessionID)].problemNumberList.append(tmpProbList[Num])
        return "<script> window.location.href = \"/\" + location.href.split(\"/\")[location.href.split(\"/\").length-2] </script>"
    else:
        return "<script> alert('間違った問題はありません。もう一度最初から始めます。'); window.location.href = \"/\" + location.href.split(\"/\")[location.href.split(\"/\").length-2] + \"/deleteRecord\" </script>"
    #return "間違った問題数:" + str(len(tmpWrongList)) + ",次の問題リスト:" + str(recordDict[str(sessionID)].problemNumberList)
    
#教科管理画面
@app.route(URL_manageSubject)
def getMngSubj(hashedValue=None):
   loginAvailability = False
   for lsd in list(loginSessionDict.values()):
      if lsd.hashedSerialNumber == hashedValue:
         loginAvailability = True
   if loginAvailability:
      #IPアドレスの関係
      if not (request.remote_addr in dTi.keys()):
         dTi[request.remote_addr] = reverse_lookup(request.remote_addr)
      print("Access from : ",end="")
      print(dTi[request.remote_addr] if dTi[request.remote_addr] != False else request.remote_addr)
      #ログ
      logList.append(request.remote_addr)
      subjectListHtml = ""
      for subName in subjectNameList:
         subjectListHtml += subjectMngListTemp.format(subName=subName,subText=subName + "_text",subMod=subName + "_mod",subDel=subName + "_del") + "\n"
      with open(mngSubjHtmlPath,'r',encoding="utf-8-sig") as htso:
         htmlSource = htso.read().format(buttons=subjectListHtml)
      return htmlSource
   else:
      return "<h1>認証エラー</h1>"

#問題管理画面
@app.route(URL_manageProblem)
def getMngProblem(hashedValue=None,subName=None):
   loginAvailability = False
   for lsd in list(loginSessionDict.values()):
      if lsd.hashedSerialNumber == hashedValue:
         loginAvailability = True
   if loginAvailability:
      #IPアドレスの関係
      if not (request.remote_addr in dTi.keys()):
         dTi[request.remote_addr] = reverse_lookup(request.remote_addr)
      print("Access from : ",end="")
      print(dTi[request.remote_addr] if dTi[request.remote_addr] != False else request.remote_addr)
      #ログ
      logList.append(request.remote_addr)
      subjectListHtml = ""
      problemListHtml = ""
      subjectListHtml += problemPullDownTemp.format(subName="") + "\n"
      idx = 0
      for sn in subjectNameList:
         subjectListHtml += problemPullDownTemp.format(subName=sn) + "\n"
      if subName != "None":
         for prob in problems[subName]:   
            problemListHtml += problemMngListTemp.format(no=str(idx),prob=prob["問題"],probMod=str(idx) + "_mod",probDel=str(idx) + "_del")
            idx += 1
      else:
         problemListHtml += problemMngListTemp.format(no="0",prob="教科を上のプルダウンから選択してください",probMod="",probDel="")
      with open(mngProblemjHtmlPath,'r',encoding="utf-8-sig") as htso:
         htmlSource = htso.read().format(opt=subjectListHtml,buttons=problemListHtml)
      return htmlSource
   else:
      return "<h1>認証エラー</h1>"

#教科管理画面の教科追加
@app.route(URL_editSubject)
def addSubj(hashedValue=None,mode=None,subName=None,aSubName=None):
   global subjectNameList
   loginAvailability = False
   for lsd in list(loginSessionDict.values()):
      if lsd.hashedSerialNumber == hashedValue:
         loginAvailability = True
   if loginAvailability:
      #IPアドレスの関係
      if not (request.remote_addr in dTi.keys()):
         dTi[request.remote_addr] = reverse_lookup(request.remote_addr)
      print("Access from : ",end="")
      print(dTi[request.remote_addr] if dTi[request.remote_addr] != False else request.remote_addr)
      #ログ
      logList.append(request.remote_addr)
      if mode == "addSubj":
         subjectNameList.append(subName)
      elif mode == "delSubj":
         subjectNameList.remove(subName)
      elif mode == "modSubj":
         with open(problemsFilePathTemp.format(subjectName=aSubName),"w",encoding="utf-8-sig") as sf:
            json.dump(problems[subName],sf, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
         subjectNameList.remove(subName)
         subjectNameList.append(aSubName)
      with open(subjectNameListPath,"w",encoding="utf-8-sig") as sf:
            json.dump(subjectNameList,sf, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
      loadSubjects()
      for subName in subjectNameList:
          problemsFilePathsDict[subName] = problemsFilePathTemp.format(subjectName=subName)
      loadproblemsFromJson()
      return "<script> window.location.href = \"/mngSubject/{}\"</script>".format(hashedValue)
   else:
      return "<h1>認証エラー</h1>"

#問題管理
@app.route(URL_editProblem)
def editProblem(hashedValue=None,mode=None,subName=None,probNo=None):
   global subjectNameList
   loginAvailability = False
   for lsd in list(loginSessionDict.values()):
      if lsd.hashedSerialNumber == hashedValue:
         loginAvailability = True
   if loginAvailability:
      #IPアドレスの関係
      if not (request.remote_addr in dTi.keys()):
         dTi[request.remote_addr] = reverse_lookup(request.remote_addr)
      print("Access from : ",end="")
      print(dTi[request.remote_addr] if dTi[request.remote_addr] != False else request.remote_addr)
      #ログ
      logList.append(request.remote_addr)
      with open(mngProblemEditorjHtmlPath,"r",encoding="utf-8-sig") as f:
         htmlSource = f.read()
      if mode == "add":
         if probNo != "dummy":
            pass
         else:
            htmlSource = htmlSource.format(problemText="",No1="",No2="",No3="",No4="",comentTextArea="",selected1="",selected2="",selected3="",selected4="")
            return htmlSource
      elif mode == "del":
         problems[subName].pop(int(probNo))
      elif mode == "mod":
         probNo = int(probNo)%len(problems[subName])
         selectedList = ["" for i in range(4)]
         selectedList[int(problems[subName][probNo]["正答"])-1] = "selected"
         htmlSource = htmlSource.format(problemText=problems[subName][probNo]["問題"],No1=problems[subName][probNo]["選択肢1"],No2=problems[subName][probNo]["選択肢2"],No3=problems[subName][probNo]["選択肢3"],No4=problems[subName][probNo]["選択肢4"],comentTextArea=problems[subName][probNo]["解説"],selected1=selectedList[0],selected2=selectedList[1],selected3=selectedList[2],selected4=selectedList[3])
         return htmlSource
      with open(problemsFilePathsDict[subName],"w",encoding="utf-8-sig") as sf:
            json.dump(problems[subName],sf, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
      loadproblemsFromJson()
      return "<script> window.location.href = \"/mngProblem/{}/{}\"</script>".format(hashedValue,subName)
   else:
      return "<h1>認証エラー</h1>"

#問題管理
@app.route(URL_editProblemPost, methods=['POST'])
def editProblemPost(hashedValue=None):
   global subjectNameList
   reciveJson = dict(request.json)
   loginAvailability = False
   for lsd in list(loginSessionDict.values()):
      if lsd.hashedSerialNumber == hashedValue:
         loginAvailability = True
   if loginAvailability:
      #IPアドレスの関係
      if not (request.remote_addr in dTi.keys()):
         dTi[request.remote_addr] = reverse_lookup(request.remote_addr)
      print("Access from : ",end="")
      print(dTi[request.remote_addr] if dTi[request.remote_addr] != False else request.remote_addr)
      #ログ
      logList.append(request.remote_addr)
      if reciveJson["mode"] == "mod":
         probNum = int(reciveJson["probNum"])
         problems[reciveJson["subName"]][probNum]["問題"] = reciveJson["problemStatement"]
         problems[reciveJson["subName"]][probNum]["正答"] = reciveJson["correctAnswer"]
         problems[reciveJson["subName"]][probNum]["解説"] = reciveJson["coment"]
         problems[reciveJson["subName"]][probNum]["選択肢1"] = reciveJson["choise1"]
         problems[reciveJson["subName"]][probNum]["選択肢2"] = reciveJson["choise2"]
         problems[reciveJson["subName"]][probNum]["選択肢3"] = reciveJson["choise3"]
         problems[reciveJson["subName"]][probNum]["選択肢4"] = reciveJson["choise4"]
      elif reciveJson["mode"] == "add":
         problems[reciveJson["subName"]].append(dict())
         probNum = len(problems[reciveJson["subName"]])-1
         problems[reciveJson["subName"]][probNum]["問題"] = reciveJson["problemStatement"]
         problems[reciveJson["subName"]][probNum]["正答"] = reciveJson["correctAnswer"]
         problems[reciveJson["subName"]][probNum]["解説"] = reciveJson["coment"]
         problems[reciveJson["subName"]][probNum]["選択肢1"] = reciveJson["choise1"]
         problems[reciveJson["subName"]][probNum]["選択肢2"] = reciveJson["choise2"]
         problems[reciveJson["subName"]][probNum]["選択肢3"] = reciveJson["choise3"]
         problems[reciveJson["subName"]][probNum]["選択肢4"] = reciveJson["choise4"]
      with open(problemsFilePathsDict[reciveJson["subName"]],"w",encoding="utf-8-sig") as sf:
         json.dump(problems[reciveJson["subName"]],sf, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
      loadproblemsFromJson()
      return str(probNum)
   else:
      return "<h1>認証エラー</h1>"

if __name__ == '__main__':
   main()