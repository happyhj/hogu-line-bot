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
from firebase import firebase

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


# init firebase 
firebase = firebase.FirebaseApplication('https://heirumi-bot.firebaseio.com', None)
#result = firebase.get('/events', None)
#print result 

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
        eventDict = json.loads(str(event));
        #firebase.post('/events', new_user)

        if not isinstance(event, MessageEvent):
            continue

        if eventDict.message.type == 'image' || eventDict.message.type == 'video':
            # getContents : eventDict.message.id and save files to firebase storage
            # after that // result = firebase.post('/events', eventDict)        



        if not isinstance(event.message, TextMessage):
            continue

        command = event.message.text.split()[0]

        if command[0] != '@':
            continue

        command = command[1:]

        if command == 'text':
            line_bot_api.reply_message(
                event.reply_token,
                #TextSendMessage(text=event.message.text)
                TextSendMessage(text='Hello world!')
            )
            continue

        if command == 'sticker':
            line_bot_api.reply_message(
                event.reply_token,
                StickerSendMessage(sticker_id=1, package_id=1)
            )
            continue 

        if command == 'image':
            line_bot_api.reply_message(
                event.reply_token,
                ImageSendMessage(
                    original_content_url='https://i.imgur.com/XkPOG6s.jpeg',
                    preview_image_url='https://i.imgur.com/WHPSX62.jpeg'
                )
            )
            continue 

        if command == 'video':
            line_bot_api.reply_message(
                event.reply_token,
                VideoSendMessage(
                    original_content_url='https://video-icn1-1.xx.fbcdn.net/v/t42.1790-2/15815603_1228027843979861_3120848989621059584_n.mp4?efg=eyJybHIiOjY4MiwicmxhIjo1MTIsInZlbmNvZGVfdGFnIjoic3ZlX3NkIn0%3D&rl=682&vabr=379&oh=e5922d382ec45c3c9b50ca0e52e0a93b&oe=586A7BCB',
                    preview_image_url='https://scontent-icn1-1.xx.fbcdn.net/v/t15.0-10/p480x480/15816042_1418185544882806_5129367115333107712_n.jpg?oh=209f20c7e6c56741c5a476b0a6f3d96e&oe=591DDD9C'
                )
            )
            continue 

        if command == 'audio':
            line_bot_api.reply_message(
                event.reply_token,
                AudioSendMessage(
                    original_content_url='http://techslides.com/demos/samples/sample.m4a',
                    duration=3000
                )
            )
            continue 

        if command == 'location':
            line_bot_api.reply_message(
                event.reply_token,
                LocationSendMessage(
                    title='첼시 마켓',
                    address='75 9th Ave, New York, NY 10011 \nchelseamarket.com',
                    latitude=40.7421218,
                    longitude=-74.0073127
                )
            )
            continue 

        if command == 'buttons':
            line_bot_api.reply_message(
                event.reply_token,
                TemplateSendMessage(
                    alt_text='[buttons] unsupported device',
                    template=ButtonsTemplate(
                        title="Menu",
                        text="Please select",
                        thumbnail_image_url='https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles9.naver.net%2F20140806_213%2Fbebop38_1407319754921zAbXb_JPEG%2F3b96436c1667e9dbae9a320745b58b25.jpg&type=sc960_832',
                        actions=[
                            PostbackTemplateAction(
                                label='Post Back',
                                data='이러한 데이터를 반환합니다.',
                                text='Post Back 으로 데이터를 반환 했습니다'
                            ),
                            MessageTemplateAction(
                                label='Message',
                                text='Message Action 으로 메시지를 전송했습니다'
                            ),
                            URITemplateAction(
                                label='Open Safari',
                                uri='https://m.naver.com/'
                            )
                        ]

                    )
                )
            )
            continue 

        if command == 'confirm':
            line_bot_api.reply_message(
                event.reply_token,
                TemplateSendMessage(
                    alt_text='[confirm] unsupported device',
                    template=ButtonsTemplate(
                        text='Are you sure?',
                        actions=[
                            PostbackTemplateAction(
                                label='Post Back',
                                data='이러한 데이터를 반환합니다.',
                                text='Post Back 으로 데이터를 반환 했습니다'
                            ),
                            MessageTemplateAction(
                                label='Message',
                                text='Message Action 으로 메시지를 전송했습니다'
                            ),
                            URITemplateAction(
                                label='Open Safari',
                                uri='https://m.naver.com/'
                            )
                        ]

                    )
                )
            )
            continue 

        if command == 'carousel':
            line_bot_api.reply_message(
                event.reply_token,
                TemplateSendMessage(
                    alt_text='[carousel] unsupported device',
                    template=CarouselTemplate(
                        columns=[
                            CarouselColumn(
                                thumbnail_image_url='https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles9.naver.net%2F20140806_213%2Fbebop38_1407319754921zAbXb_JPEG%2F3b96436c1667e9dbae9a320745b58b25.jpg&type=sc960_832',
                                title='this is menu1',
                                text='description1',
                                actions=[
                                    PostbackTemplateAction(
                                        label='postback1',
                                        text='postback text1',
                                        data='action=buy&itemid=1'
                                    ),
                                    MessageTemplateAction(
                                        label='message1',
                                        text='message text1'
                                    ),
                                    URITemplateAction(
                                        label='uri1',
                                        uri='https://m.naver.com'
                                    )
                                ]
                            ),
                            CarouselColumn(
                                thumbnail_image_url='https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles9.naver.net%2F20140806_213%2Fbebop38_1407319754921zAbXb_JPEG%2F3b96436c1667e9dbae9a320745b58b25.jpg&type=sc960_832',
                                title='this is menu2',
                                text='description2',
                                actions=[
                                    PostbackTemplateAction(
                                        label='postback2',
                                        text='postback text2',
                                        data='action=buy&itemid=2'
                                    ),
                                    MessageTemplateAction(
                                        label='message2',
                                        text='message text2'
                                    ),
                                    URITemplateAction(
                                        label='uri2',
                                        uri='https://m.naver.com'
                                    )
                                ]
                            )
                        ]
                    )
                )
            )
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
