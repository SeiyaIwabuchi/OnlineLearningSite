#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template
from flask import request, jsonify
import json

htmlSourcePath = "./index.html"
probremsFilePath = "./probrems.json"

app = Flask(__name__,template_folder="./")
#セッション
sessions = [0]

#問題データセット
probrems = object()

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
def loadProbremsFromJson():
   global probrems
   with open(probremsFilePath,"r",encoding="utf-8_sig") as prob:
      probrems = json.load(prob)

#htmlに問題データを乗せる
def problemWritingToHtml(probremNum):
   pass

@app.route('/')
def index():
   global sessions
   with open(htmlSourcePath,'r',encoding="utf-8_sig") as htso:
      htmlSource = htso.read()%sessions[len(sessions)-1]
      sessions.append(sessions[len(sessions)-1] + 1)
   return htmlSource

@app.route('/postText', methods=['POST'])
def receiveAnswer():
   radioRes = []
   for i in range(4):
      radioRes.append(request.json['radio%d'%(i+1)])
   print("sessionID : " + request.json["sessionID"],end="")
   print(radioRes)
   #return jsonify(ResultSet=json.dumps(return_data))

def raidoRes2Number(radioRes):
   for index,b in enumerate(radioRes):
      if b:
         return index

if __name__ == '__main__':
   app.run(host="127.0.0.1", port=8080)