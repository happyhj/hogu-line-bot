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

def isValidRequestCommand(command):
    if(command[0] != '@'):
        return False

    return True

def answerTextMessage(message):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message)
    )

def answerPig():
    print "answerPig is here"
    answerTextMessage('불러또?')

def initActDelegateDictionary():
    dic = {
        '돼지야' : {act : answerPig}
    }
    return dic
    

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
        command = tokens[0]

        if(isValidRequestCommand(command)):
            continue

        command = command[1:]
        actDelegateMap = initActDelegateDictionary()
        actDelegateMap[command].act()
        continue;

        if command=='stk.call' and len(tokens)==3:
            line_bot_api.reply_message(
                event.reply_token,
                StickerSendMessage(package_id=tokens[1], sticker_id=tokens[2])
            )
            continue
        if command=='stk.img' and len(tokens)==3:
            line_bot_api.reply_message(
                event.reply_token,
                ImageSendMessage(
                    original_content_url='https://sdl-stickershop.line.naver.jp/products/0/0/1/'+tokens[1]+'/android/stickers/'+tokens[2]+'.png',
                    preview_image_url='https://sdl-stickershop.line.naver.jp/products/0/0/1/'+tokens[1]+'/android/stickers/'+tokens[2]+'.png'
                )
            )
            continue

        if command=='스티커' and len(tokens)==1:
            r = requests.get("https://store.line.me/stickershop/home/user/ko")
            bs = BeautifulSoup(r.content, 'html.parser')
            l = bs.find_all("li", class_="mdCMN12Li")
            carouselColumnArray = []

            for li in l:
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
            line_bot_api.reply_message(
                event.reply_token,
                TemplateSendMessage(
                    alt_text='PC에서는 볼수없또',
                    template=CarouselTemplate(columns=carouselColumnArray)
                )
            )
        if command=='stk.remove' and len(tokens) == 4:
            alias = tokens[1]
            packageId = tokens[2]
            stickerId = tokens[3]

            newStickerInfo = {'packageId' : packageId, 'stickerId' :stickerId}
            targetIdx  = -1
            # 기존 스티커 리스트를 가져와서 
            aliasInfo = firebase.get('/customSticker', alias)

            if aliasInfo is not None:
                stickerList = aliasInfo.get('list')
                # 이미 있는 스티커면 인덱스 기록
                for idx, stickerInfo in enumerate(stickerList):
                    if stickerInfo.get('packageId')==newStickerInfo.get('packageId') and stickerInfo.get('stickerId')==newStickerInfo.get('stickerId'):
                        targetIdx = idx
            else:
                return

            # targetIdx 가 -1 이 아니면 stickerList 에서 해당 스티커 삭제 
            if targetIdx!=-1:
                stickerList.pop(targetIdx)
                aliasInfo = { "list": stickerList }

                # save custom sticker in firebase. use patch and add last slash to remove unique number
                firebase.patch('/customSticker/' + alias + '/', aliasInfo)
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text='스티커가 ' + alias + '에서 지오져또..')
                )
        if command=='stk.list' and len(tokens) == 2:
            alias = tokens[1]
            # 해당하는 스티커 목록을 가져온다 
            aliasInfo = firebase.get('/customSticker', alias)
            stickerList = []
            if aliasInfo is not None:
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
                line_bot_api.reply_message(
                    event.reply_token,
                    TemplateSendMessage(
                        alt_text='PC에서는 볼수없또',
                        template=CarouselTemplate(columns=carouselColumnArray)
                    )
                )
            else:
                print "그런거 없또"
            return
        if command=='stk.list' and len(tokens) == 1:
            allStickerInfo = firebase.get('/customSticker', None)
            aliasList = allStickerInfo.keys()
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=', '.join(aliasList) + ' 가 이또!!')
            )
            continue
        if command=='stk.add' and len(tokens) == 4:
            alias = tokens[1]
            packageId = tokens[2]
            stickerId = tokens[3]

            newStickerInfo = {'packageId' : packageId, 'stickerId' :stickerId}
        
            # 기존 스티커 리스트를 가져와서 
            aliasInfo = firebase.get('/customSticker', alias)

            # 리스트가 아니면 리스트로 만들어 준다
            if aliasInfo is None:
                stickerList = [ newStickerInfo ]
                aliasInfo = { "list": stickerList }
            else:
                stickerList = aliasInfo.get('list')
                if len(stickerList)>=5:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text='스티커는 5개 넘게 저장할 수 없또')
                    )
                    return 'OK'
                # 이미 있는 스티커면 무시
                for stickerInfo in stickerList:
                    if stickerInfo.get('packageId')==newStickerInfo.get('packageId') and stickerInfo.get('stickerId')==newStickerInfo.get('stickerId'):
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text='이미 그렇게 등록되어있또')
                        )                    
                        return 'OK'
                # 현재 없는 새로운 스티커라면 등록 
                stickerList.append(newStickerInfo)
                aliasInfo = { "list": stickerList }

            # save custom sticker in firebase. use patch and add last slash to remove unique number
            firebase.patch('/customSticker/' + alias + '/', aliasInfo)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='스티커가 ' + alias + '로 저장되어또!!!')
            )
        if command=='stk' and len(tokens) == 2:
            alias = tokens[1]
            aliasInfo = firebase.get('/customSticker', alias)

            if aliasInfo is not None:
                # 랜덤하게 하나를 고른다
                stickerList = aliasInfo.get('list')
                stickerInfo = random.choice(stickerList)

                packageId = stickerInfo['packageId']
                stickerId = stickerInfo['stickerId']

                # 스티커 전송 API 는 기본 내장 스티커만 전송 가능하므로, 이미지 메시지 전송 API 를 사용한다.
                line_bot_api.reply_message(
                    event.reply_token,
                    ImageSendMessage(
                        original_content_url='https://sdl-stickershop.line.naver.jp/products/0/0/1/'+packageId+'/android/stickers/'+stickerId+'.png',
                        preview_image_url='https://sdl-stickershop.line.naver.jp/products/0/0/1/'+packageId+'/android/stickers/'+stickerId+'.png' 
                    )
                )
                continue
        else:
            # 커맨드 분석 메시지 
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='커맨드 ' + command +', 인자 [' + tokens[1] +'] 을 입력 받았또!!!')
            )


    return 'OK'

if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=port, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(host='0.0.0.0', debug=options.debug, port=options.port)
