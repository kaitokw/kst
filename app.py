#!/usr/bin/python
#-*-coding: utf-8 -*-
##from __future__ import absolute_import
###
from flask import Flask, jsonify, render_template, request
import json
import numpy as np
import pandas as pd
import geopy.distance as ps
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,TemplateSendMessage,ImageSendMessage, StickerSendMessage, AudioSendMessage
)
from linebot.models.template import *
from linebot import (
    LineBotApi, WebhookHandler
)

app = Flask(__name__)

lineaccesstoken = 'F7p77Oy6+pQ7D3zh+dJv1hHWg2Fh2FmRnrRneZoz6OP1e1PFk/F0Wv0jYOAhx7hpF63nOuFCNnFaqavShreVny/b1g5+CAOksfaNSj6ES4ZTA20cXL/xUlWRDq+Oa2zW40IPhJ+qeEwhpOjBrG74KQdB04t89/1O/w1cDnyilFU='
line_bot_api = LineBotApi(lineaccesstoken)

station= pd.read_excel('location.xlsx')

####################### new ########################
@app.route('/')
def index():
    return "Hello World!"


@app.route('/webhook', methods=['POST'])
def callback():
    json_line = request.get_json(force=False,cache=False)
    json_line = json.dumps(json_line)
    decoded = json.loads(json_line)
    no_event = len(decoded['events'])
    for i in range(no_event):
        event = decoded['events'][i]
        event_handle(event)
    return '',200


def event_handle(event):
    print(event)
    try:
        userId = event['source']['userId']
    except:
        print('error cannot get userId')
        return ''

    try:
        rtoken = event['replyToken']
    except:
        print('error cannot get rtoken')
        return ''
    try:
        msgId = event["message"]["id"]
        msgType = event["message"]["type"]
    except:
        print('error cannot get msgID, and msgType')
        sk_id = np.random.randint(1,17)
        replyObj = StickerSendMessage(package_id=str(1),sticker_id=str(sk_id))
        line_bot_api.reply_message(rtoken, replyObj)
        return ''

    if msgType == "text":
        msg = str(event["message"]["text"])
        replyObj = TextSendMessage(text=msg)
        line_bot_api.reply_message(rtoken, replyObj)

    if msgType == "location":
        lat = event["message"]["latitude"]
        lng = event["message"]["longitude"]
        txtresult = handle_location(lat,lng,station,5)
        replyObj = TextSendMessage(text=txtresult)
        line_bot_api.reply_message(rtoken, replyObj)
    else:
        sk_id = np.random.randint(1,17)
        replyObj = StickerSendMessage(package_id=str(1),sticker_id=str(sk_id))
        line_bot_api.reply_message(rtoken, replyObj)
    return ''

def handle_location(lat,lng,stn,topK):
    result = getdistace(lat, lng,stn)
    result = result.sort_values(by='km')
    result = result.iloc[0:topK]
    txtResult = ''
    for i in range(len(result)):
        kmdistance = '%.1f'%(result.iloc[i]['km'])
        name = str(result.iloc[i]['name'])
        txtResult = txtResult + 'ห่าง %s กิโลเมตร\n%s\n\n'%(kmdistance,name)
    return txtResult[0:-2]


def getdistace(latitude, longitude,stn):
  coords_1 = (float(latitude), float(longitude))
  ## create list of all reference locations from a pandas DataFrame
  latlngList = stn[['Latitude','Longitude']].values
  ## loop and calculate distance in KM using geopy.distance library and append to distance list
  kmsumList = []
  for latlng in latlngList:
    coords_2 = (float(latlng[0]),float(latlng[1]))
    kmsumList.append(ps.vincenty(coords_1, coords_2).km)
  stn['km'] = kmsumList
  return stn


if __name__ == '__main__':
    app.run(debug=True)
