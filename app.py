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

import requests
import json
import os
from argparse import ArgumentParser

from flask import Flask, request, abort

from linebot.exceptions import (
    InvalidSignatureError
)

from linebot.models import (
    MessageEvent,
    TextMessage,
)

from message_receiver import (
    getParser
)

from message_sender import (
    printTextMessage,
    printStickerMessage,
    printStickerImage,
    printStickerCarousel,
)

from storage import (
    saveEvent
)

from sticker_alias_service import (
    answerAliasList,
    addStickerAlias,
    answerStickerAlias,
    answerStickerAliasList,
    removeStickerFromAliasList
)

from sticker_preview_service import (
    answerStickerPreview
)

from piggy_service import (
    hello,
    happyNewYear
)

app = Flask(__name__)
port = os.getenv('PORT', None);
parser = getParser()

def parseToken(event):
    message = event.message.text
    if '@' not in message:
        return [None, None]
    
    tokens = message.split('@', 1)[1].split()
    if len(tokens) == 0:
        return [None, None]

    return [tokens[0], tokens[1:]]

def actEvent(command, **param):
    try:
        actDispatcher[command](**param)
    except KeyError:
        return 

def answerCommandList(**param):
    event = param['event']
    commandDescriptions = """
        돼지야 : 테스트용
        stk.img (packageId) (stickerId) : 스티커 미리보기
        스티커목록 : 스티커 리스트 보기
        stk (alias): alias에 등록된 스티커 중 하나 랜덤으로 불러오기
        stk.add (alias) (packageId) (stickerId) : 스티커 추가
        stk.list (alias) : alias에 등록된 스티커 목록 보기 
        stk.remove (alias) (packageId) (stickerId) : alias에서 지정한 스티커 제거하기
    """
    printTextMessage(event, commandDescriptions)
    
actDispatcher = {
    'help' : answerCommandList,
    '돼지야' : hello,
    '새해복많이받아~돼지야' : happyNewYear,           # 새해 기념 추가 이벤트

    'stk.img' : answerStickerPreview,           # 해당 (packageId, stickerId)의 스티커 미리보기
    
    '스티커목록' : answerAliasList,                # 전체 스티커 명령어 목록 확인
    'stk' : answerStickerAlias,                 # 스티커 하나 불러오기
    'stk.add' : addStickerAlias,                # 스티커 추가
    'stk.list' : answerStickerAliasList,        # 해당 명령어에 추가된 스티커 리스트 불러오기
    'stk.remove' : removeStickerFromAliasList,  # 해당 명령어에서 스티커 제거하기
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

    for event in events:
        # log every event to firebase
        eventDict = json.loads(str(event))
        saveEvent(eventDict)
        print eventDict

        if not isinstance(event, MessageEvent):
            continue

        if not isinstance(event.message, TextMessage):
            continue

        command, parameters = parseToken(event)
        
        if command is None:
            continue

        # is Command
        if command in actDispatcher:
            actEvent(command, event=event, tokens=parameters)
            continue

        # try as sticker 
        answerStickerAlias(event=event, tokens=parameters, alias=command)

    return 'OK'

if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=port, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(host='0.0.0.0', debug=options.debug, port=options.port)
