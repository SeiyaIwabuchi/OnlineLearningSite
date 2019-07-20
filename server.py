#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template
from flask import request, jsonify
import json

htmlSourcePath = "./index.html"
resultSourcePath = "./result.html"
problemsFilePath = "./problems.json"
problemListHtmlSource = "./ProblemList.html"

app = Flask(__name__,template_folder="./")
#セッション
sessions = [0]

#問題データセット
problems = object()

#成績リスト
recordDict = {}

#成績データ
class RecordData():
   def __init__(self):
      self.totalAnswers = 0
      self.correctAnswers = 0
      self.wrongAnswers = 0
      self.correctNumber = []
      self.wrongNumber = []
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
   with open(problemsFilePath,"r",encoding="utf-8_sig") as prob:
      problems = json.load(prob)

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
def problemWritingToHtml(problemNum,htmlSource):
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
      sessionID = str(sessions[len(sessions)-1]),
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
   global sessions
   recordDict[str(sessions[len(sessions)-1])] = RecordData()
   with open(htmlSourcePath,'r',encoding="utf-8_sig") as htso:
      #htmlSource = htso.read().format(sessionID = int(sessions[len(sessions)-1]))
      htmlSource = htso.read()
      htmlSource = problemWritingToHtml(0,htmlSource)
      sessions.append(sessions[len(sessions)-1] + 1)
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

if __name__ == '__main__':
   loadproblemsFromJson()
   app.run(threaded = True,host="0.0.0.0", port=80)