# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

from __future__ import unicode_literals
from bs4 import BeautifulSoup
from firebase import firebase
import random

import requests
import json
import os
import sys
from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    ImageSendMessage,
    VideoSendMessage,
    AudioSendMessage,
    LocationSendMessage,
    StickerSendMessage,
    TemplateSendMessage,

    ButtonsTemplate,
    ConfirmTemplate,
    CarouselTemplate, 
    CarouselColumn,

    PostbackTemplateAction, 
    MessageTemplateAction,
    URITemplateAction,
)

app = Flask(__name__)

firebase = firebase.FirebaseApplication('https://hogu-line-bot.firebaseio.com', None)     

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
port = os.getenv('PORT', None);

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

def props(x):
    return dict((key, getattr(x, key)) for key in dir(x) if key not in dir(x.__class__))

def printTextMessage(event, message):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message)
    )

def printStickerMessage(event, packageId, stickerId):
    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(package_id=packageId, sticker_id=stickerId)
    )

def printStickerImage(event, packageId, stickerId):
    line_bot_api.reply_message(
        event.reply_token,
        ImageSendMessage(
            original_content_url='https://sdl-stickershop.line.naver.jp/products/0/0/1/'+packageId+'/android/stickers/'+stickerId+'.png',
            preview_image_url='https://sdl-stickershop.line.naver.jp/products/0/0/1/'+packageId+'/android/stickers/'+stickerId+'.png'
        )
    )

def answerStickerMessgae(**param):
    event = param['event']
    packageId = param['tokens'][0]
    stickerId = param['tokens'][1]
    printStickerMessage(event, packageId, stickerId)

def answerStickerImage(**param):
    event = param['event']
    packageId = param['tokens'][0]
    stickerId = param['tokens'][1]
    printStickerImage(event, packageId, stickerId)

def printStickerCarousel(event, altText, carouselColumnArray):
    line_bot_api.reply_message(
        event.reply_token,
        TemplateSendMessage(
            alt_text=altText,
            template=CarouselTemplate(columns=carouselColumnArray)
        )
    )

def answerPig(**param):
    event = param['event']
    printTextMessage(event, '불러또?')

def actEvent(command, **param):
    actDispatcher[command](**param)

def parseHtml():
    r = requests.get("https://store.line.me/stickershop/home/user/ko")
    bs = BeautifulSoup(r.content, 'html.parser')
    l = bs.find_all("li", class_="mdCMN12Li")
    return l

def hasStickerInfo(aliasInfo, newStickerInfo):
    targetIdx  = -1
    stickerList = aliasInfo.get('list')

    if aliasInfo is not None:
        # 이미 있는 스티커면 인덱스 기록
        for idx, stickerInfo in enumerate(stickerList):
            if stickerInfo.get('packageId')==newStickerInfo.get('packageId') and stickerInfo.get('stickerId')==newStickerInfo.get('stickerId'):
                targetIdx = idx
    
    return targetIdx

def buildCarouselList(liList):
    carouselColumnArray = []

    for li in liList:
        if len(carouselColumnArray)==5:
            continue
        href = 'https://store.line.me' + li.a.get('href')
        packageId = li.a.find(class_='mdCMN06Img').img.get('src').split('product/')[1].split('/ANDROID')[0]

        thumbnail_image_url = 'https://sdl-stickershop.line.naver.jp/products/0/0/1/'+packageId+'/iphone/main@2x.png'

        title = li.a.find(class_='mdCMN06Ttl').getText()

        carouselColumnArray.append(
            CarouselColumn(
                thumbnail_image_url=thumbnail_image_url,
                title=title,
                text='살려줘',
                actions=[
                    URITemplateAction(
                        label='보기',
                        uri=href
                    )
                ]
            )
        )
    return carouselColumnArray

def answerStickerWithCarousel(**param):
    event = param['event']
    liList = parseHtml()
    carouselColumnArray = buildCarouselList(liList)
    printStickerCarousel(event, 'PC에서는 볼수없또', carouselColumnArray)

def answerStickerRemoveCarousel(**param):
    event = param['event']
    tokens = param['tokens']
    alias = tokens[0]
    packageId = tokens[1]
    stickerId = tokens[2]

    newStickerInfo = {'packageId' : packageId, 'stickerId' :stickerId}

    # 기존 스티커 리스트를 가져와서 
    aliasInfo = firebase.get('/customSticker', alias)
    stickerList = aliasInfo.get('list')
    targetIdx = hasStickerInfo(aliasInfo, newStickerInfo)

    # targetIdx 가 -1 이면 리턴(삭제할 대상이 없음)
    if targetIdx == -1:
        printTextMessage(event, '지울 게 없또!')
        return

    stickerList.pop(targetIdx)
    aliasInfo = { "list": stickerList }

    # save custom sticker in firebase. use patch and add last slash to remove unique number
    firebase.patch('/customSticker/' + alias + '/', aliasInfo)
    printTextMessage(event, '스티커가 ' + alias + '에서 지오져또..')

def buildSavedStickerInfoCarousel(aliasInfo, alias):
    stickerList = aliasInfo.get('list')
    carouselColumnArray = []
    for idx, stickerInfo in enumerate(stickerList):
        packageId = stickerInfo.get('packageId')
        stickerId = stickerInfo.get('stickerId')
        # print 'https://sdl-stickershop.line.naver.jp/products/0/0/1/'+packageId+'/android/stickers/'+stickerId+'.png'
        # print alias
        # print str(idx)
        # print '@stk.remove '+alias+ ' '+ packageId + ' ' + stickerId
        carouselColumnArray.append(
            CarouselColumn(
                thumbnail_image_url='https://sdl-stickershop.line.naver.jp/products/0/0/1/'+packageId+'/android/stickers/'+stickerId+'.png',
                title=alias,
                text=str(idx),
                actions=[
                    MessageTemplateAction(
                        label='지우기',
                        text='@stk.remove '+alias+ ' '+ packageId + ' ' + stickerId
                    )
                ]
            )
        )
    return carouselColumnArray

def answerStickerList(**param):
    event = param['event']
    tokens = param['tokens']

    if len(tokens) == 0 :
        allStickerInfo = firebase.get('/customSticker', None)
        aliasList = allStickerInfo.keys()
        printTextMessage(event, ', '.join(aliasList) + ' 가 이또!!')

    if len(tokens) == 1 :
        alias = tokens[0]
        # 해당하는 스티커 목록을 가져온다 
        aliasInfo = firebase.get('/customSticker', alias)

        if aliasInfo is None:
            printTextMessage(event, '그런거 없또')
            return
        
        carouselColumnArray = buildSavedStickerInfoCarousel(aliasInfo, alias)
        printStickerCarousel(event, 'PC에서는 볼수없또', carouselColumnArray)               

    return

def validateStickAdd(stickerList, newStickerInfo, event):
    # 하나의 키워드마다 스티커 저장 개수 벨리데이션
    if len(stickerList)>=5 :
        printTextMessage(event, '스티커는 5개 넘게 저장할 수 없또')
        return False

    # 이미 있는 스티커면 무시
    for stickerInfo in stickerList:
        if stickerInfo.get('packageId')==newStickerInfo.get('packageId') and stickerInfo.get('stickerId')==newStickerInfo.get('stickerId'):
            printTextMessage(event, '이미 그렇게 등록되어있또')
            return False
        
    return True

def answerStickAdd(**param):
    event = param['event']
    tokens = param['tokens']
    alias = tokens[0]
    packageId = tokens[1]
    stickerId = tokens[2]

    newStickerInfo = {'packageId' : packageId, 'stickerId' :stickerId}
        
    # 기존 스티커 리스트를 가져와서 
    aliasInfo = firebase.get('/customSticker', alias)    
    
    # 이전에 저장된 값이 없다면 리스트로 만들어 초기화
    if aliasInfo is None:
        stickerList = [ newStickerInfo ]
        aliasInfo = { "list": stickerList }
    else:
        stickerList = aliasInfo.get('list')
        if not validateStickAdd(stickerList, newStickerInfo, event):
            return

        # 현재 없는 새로운 스티커라면 등록 
        stickerList.append(newStickerInfo)
        aliasInfo = { "list": stickerList }

    # save custom sticker in firebase. use patch and add last slash to remove unique number
    firebase.patch('/customSticker/' + alias + '/', aliasInfo)
    printTextMessage(event, '스티커가 ' + alias + '로 저장되어또!!!')

def answerSticker(**param):
    event = param['event']
    if 'alias' in param: # 파라미터를 외부주입 받은 경우
        alias = param['alias']
    else:
        alias = param['tokens'][0]

    aliasInfo = firebase.get('/customSticker', alias)

    if aliasInfo is None:
        return

    # 랜덤하게 하나를 고른다
    stickerList = aliasInfo.get('list')
    stickerInfo = random.choice(stickerList)

    packageId = stickerInfo['packageId']
    stickerId = stickerInfo['stickerId']

    # 스티커 전송 API 는 기본 내장 스티커만 전송 가능하므로, 이미지 메시지 전송 API 를 사용한다.
    printStickerImage(event, packageId, stickerId)

def answerHappyNewYear(**param):
    event = param['event']
    printTextMessage(event, "고마오 닝겐들아!! 새해 복 많이 받고 올해는 꼭 탈때지해야돼얌!")

def findCommandIdx(tokens):
    for idx, token in enumerate(tokens):
        if token[0] == '@':
            return idx
    
    return None

actDispatcher = {
    '돼지야' : answerPig,
    'stk.call' : answerStickerMessgae,
    'stk.img' : answerStickerImage,
    '스티커' : answerStickerWithCarousel,
    'stk.remove' : answerStickerRemoveCarousel,
    'stk.list' : answerStickerList,
    'stk.add' : answerStickAdd,
    'stk' : answerSticker,
    # 새해 기념 추가 이벤트
    '새해복많이받아~돼지야' : answerHappyNewYear
}

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        # log every event to firebase
        eventDict = json.loads(str(event))
        firebase.post('/events', eventDict)
        print eventDict

        if not isinstance(event, MessageEvent):
            continue

        if event.message.type=='image':
            event.message.id
            continue

        if not isinstance(event.message, TextMessage):
            continue

        tokens = event.message.text.split()
        commandIdx = findCommandIdx(tokens)
        if commandIdx is None:
            continue

        command = tokens[commandIdx][1:]
        parameters = tokens[commandIdx+1:]

        # 채팅 도중에 @로 호출한 스티커는 곧바로 예약스티커 로직 태운다.
        if(commandIdx != 0):
            answerSticker(event=event, tokens=parameters, alias=command)

        actEvent(command, event=event, tokens=parameters)
        continue

    return 'OK'

if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=port, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(host='0.0.0.0', debug=options.debug, port=options.port)
