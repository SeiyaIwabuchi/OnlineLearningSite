#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template
from flask import request, jsonify
import json

app = Flask(__name__,template_folder="./")


@app.route('/')
def index():
   return render_template('index.html')

@app.route('/postText', methods=['POST'])
def receiveAnswer():
   radioRes = []
   for i in range(4):
      radioRes.append(request.json['radio%d'%(i+1)])
   print(radioRes)
   #return jsonify(ResultSet=json.dumps(return_data))


if __name__ == '__main__':
   app.run(host="127.0.0.1", port=8080)