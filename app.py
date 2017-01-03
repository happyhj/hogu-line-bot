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

#for li in lImg:
#    print li.img.get('src')

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

firebase = firebase.FirebaseApplication('https://hogu-line-bot.firebaseio.com', None)



def props(x):
    return dict((key, getattr(x, key)) for key in dir(x) if key not in dir(x.__class__))

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
        eventDict = json.loads(str(event));
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

        if command[0] != '@':
            continue

        command = command[1:]

        if command=='sticker' and len(tokens)==3:
            line_bot_api.reply_message(
                event.reply_token,
                StickerSendMessage(package_id=tokens[1], sticker_id=tokens[2])
            )
            continue
        if command=='stickerImg' and len(tokens)==3:
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

            li = l[0]
            href = li.a.get('href')
            thumbnail_image_url = li.a.find(class_='mdCMN06Img').img.get('src')
            title = li.a.find(class_='mdCMN06Ttl').getText()
            # for li in l:
            #     if len(carouselColumnArray)==5:
            #         continue
            #     href = li.a.get('href')
            #     thumbnail_image_url = li.a.find(class_='mdCMN06Img').img.get('src')
            #     title = li.a.find(class_='mdCMN06Ttl').getText()
            #     carouselColumnArray.append(
            #         CarouselColumn(
            #             thumbnail_image_url=thumbnail_image_url,
            #             title=title,
            #             text='',
            #             actions=[
            #                 URITemplateAction(
            #                     label='보기',
            #                     uri=href
            #                 )
            #             ]
            #         )
            #     )

            line_bot_api.reply_message(
                event.reply_token,
                TemplateSendMessage(
                    alt_text='PC에서는 볼수없또',
                    template=CarouselTemplate(columns=[
                        carouselColumnArray.append(
                            CarouselColumn(
                                thumbnail_image_url=thumbnail_image_url,
                                title=title,
                                text='',
                                actions=[
                                    URITemplateAction(
                                        label='보기',
                                        uri=href
                                    )
                                ]
                            )
                        )
                    ])
                )
            )
            continue
        else:
            # 커맨드 분석 메시지 
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='커맨드 ' + command +', 인자 ' + param +' 을 입력 받았또!!!')
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
