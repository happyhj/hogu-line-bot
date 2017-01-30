# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random
from firebase import firebase

firebase = firebase.FirebaseApplication('https://hogu-line-bot.firebaseio.com', None)

def loadAllCustomStickerKeys():
    allStickerInfo = firebase.get('/customSticker', None)
    aliasList = allStickerInfo.keys()
    return aliasList

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

def saveCustomSticker(alias, stickerInfo):
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

# alias 내에 저장된 스티커 목록
def loadCustomStickerList(alias):
    aliasInfo = firebase.get('/customSticker', alias)
    if aliasInfo is None:
        return
    return aliasInfo.get('list')

# alias 내에 저장된 스티커 중 하나를 랜덤으로 뽑아 리턴
def loadCustomSticker(alias):
    stickerList = loadCustomStickerList(alias)

    if stickerList is None:
        return

    # 랜덤하게 하나를 고른다
    stickerInfo = random.choice(stickerList)
    return stickerInfo

def updateCustomStkicker(alias, aliasInfo):
    firebase.patch('/customSticker/' + alias + '/', aliasInfo)

def saveEvent(event):
    firebase.post('/events', event)
