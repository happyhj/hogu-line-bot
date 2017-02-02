# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from storage import (
    loadAllCustomStickerKeys,
    saveCustomSticker,
    loadCustomSticker,
    loadCustomStickerList,
    updateCustomSticker
)

from carousel_helper import (
    buildSavedStickerInfoCarousel
)

from message_sender import (
    printTextMessage,
    printStickerImage,
    printStickerCarousel
)

def answerAliasList(**param):
    event = param['event']

    aliasList = loadAllCustomStickerKeys()
    printTextMessage(event, ', '.join(aliasList) + ' 가 이또!!')

def addStickerAlias(**param):
    event = param['event']
    tokens = param['tokens']
    alias = tokens[0]
    packageId = tokens[1]
    stickerId = tokens[2]

    newStickerInfo = {'packageId' : packageId, 'stickerId' :stickerId}
        
    saveCustomSticker(alias, newStickerInfo)
    printTextMessage(event, '스티커가 ' + alias + '로 저장되어또!!!')

def answerStickerAlias(**param):
    event = param['event']
    if 'alias' in param: # 파라미터를 외부주입 받은 경우
        alias = param['alias']
    else:
        alias = param['tokens'][0]

    stickerInfo = loadCustomSticker(alias)
    if stickerInfo is None:
        return

    packageId = stickerInfo['packageId']
    stickerId = stickerInfo['stickerId']

    # 스티커 전송 API 는 기본 내장 스티커만 전송 가능하므로, 이미지 메시지 전송 API 를 사용한다.
    printStickerImage(event, packageId, stickerId)

def answerStickerAliasList(**param):
    event = param['event']
    tokens = param['tokens']
    alias = tokens[0]

    # 해당하는 스티커 목록을 가져온다 
    stickerList = loadCustomStickerList(alias)
    if stickerList is None:
        printTextMessage(event, '그런거 없또')
        return
    
    carouselColumnArray = buildSavedStickerInfoCarousel(stickerList, alias)
    printStickerCarousel(event, 'PC에서는 볼수없또', carouselColumnArray)

def removeStickerFromAliasList(**param):
    event = param['event']
    tokens = param['tokens']
    alias = tokens[0]
    packageId = tokens[1]
    stickerId = tokens[2]

    stickerToRemove = {'packageId' : packageId, 'stickerId' :stickerId}

    # 기존 스티커 리스트를 가져와서 
    stickerList = loadCustomStickerList(alias)
    if stickerList is None:
        printTextMessage(event, '그런거 없또')
        return

    if stickerToRemove not in stickerList:
        printTextMessage(event, '지울 게 없또!')
        return

    stickerList.pop(stickerList.index(stickerToRemove))
    aliasInfo = { "list": stickerList }

    updateCustomSticker(alias, aliasInfo)
    printTextMessage(event, '스티커가 ' + alias + '에서 지오져또..')

