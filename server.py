#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template
from flask import request, jsonify
import json

htmlSourcePath = "./index.html"
problemsFilePath = "./problems.json"

app = Flask(__name__,template_folder="./")
#セッション
sessions = [0]

#問題データセット
problems = object()

#成績データ
class RecordData():
   totalAnswers = 0
   correctAnswers = 0
   wrongAnswers = 0
   def getStatistics(self):
      data = [ 
         self.totalAnswers,
         self.correctAnswers,
         self.wrongAnswers,
         self.correctAnswers / self.totalAnswers,
         self.wrongAnswers / self.totalAnswers
         ]
      return data
   correctNumber = []
   wrongNumber = []

#jqueryでif文で必ず回答しないと送信できないようにする。  

#問題はjsonにする
#問題データ読み込み
def loadproblemsFromJson():
   global problems
   with open(problemsFilePath,"r",encoding="utf-8_sig") as prob:
      problems = json.load(prob)

#htmlに問題データを乗せる(最初だけ)
def problemWritingToHtml(problemNum,htmlSource):
   tmpDict = problems[problemNum]
   print(tmpDict)
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
   with open(htmlSourcePath,'r',encoding="utf-8_sig") as htso:
      #htmlSource = htso.read().format(sessionID = int(sessions[len(sessions)-1]))
      htmlSource = htso.read()
      htmlSource = problemWritingToHtml(0,htmlSource)
      sessions.append(sessions[len(sessions)-1] + 1)
   return htmlSource

@app.route('/postText', methods=['POST'])
def receiveAnswer():
   radioRes = []
   for i in range(4):
      radioRes.append(request.json['radio%d'%(i+1)])
   print("sessionID : " + request.json["sessionID"],end=" ")
   print("SelecedNumber : " + str(raidoRes2Number(radioRes)))
   print("problemNumber : " + str(request.json["probNum"]))
   return_data = {
      "RorW":judgment(request.json["probNum"],raidoRes2Number(radioRes)),
      "correct":problems[int(request.json["probNum"])]["正答"],
      "comment":problems[int(request.json["probNum"])]["解説"]
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
      print(problemJson)
      return jsonify(ResultSet=json.dumps(problemJson))

@app.route("/result/<sessionID>")
def setResult(sessionID=None):
   pass

if __name__ == '__main__':
   loadproblemsFromJson()
   app.run(host="127.0.0.1", port=8080)