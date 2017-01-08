from __future__ import unicode_literals

import line_message_sender
from firebase import firebase

firebase = firebase.FirebaseApplication('https://hogu-line-bot.firebaseio.com', None)     

def isValidRequestCommand(command):
    if(command[0] != '@'):
        return False

    return True

def answerStickerMessgae(**param):
    event = param['event']
    packageId = param['tokens'][0]
    stickerId = param['tokens'][1]
    line_message_sender.printStickerMessage(event, packageId, stickerId)

def answerStickerImage(**param):
    event = param['event']
    packageId = param['tokens'][0]
    stickerId = param['tokens'][1]
    line_message_sender.printStickerImage(event, packageId, stickerId)

def answerPig(**param):
    event = param['event']
    line_message_sender.printTextMessage(event, '불러또?')

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
    line_message_sender.printStickerCarousel(event, 'PC에서는 볼수없또', carouselColumnArray)

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
        line_message_sender.printTextMessage(event, '지울 게 없또!')
        return

    stickerList.pop(targetIdx)
    aliasInfo = { "list": stickerList }

    # save custom sticker in firebase. use patch and add last slash to remove unique number
    firebase.patch('/customSticker/' + alias + '/', aliasInfo)
    line_message_sender.printTextMessage(event, '스티커가 ' + alias + '에서 지오져또..')

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
        line_message_sender.printTextMessage(event, ', '.join(aliasList) + ' 가 이또!!')

    if len(tokens) == 1 :
        alias = tokens[0]
        # 해당하는 스티커 목록을 가져온다 
        aliasInfo = firebase.get('/customSticker', alias)

        if aliasInfo is None:
            line_message_sender.printTextMessage(event, '그런거 없또')
            return
        
        carouselColumnArray = buildSavedStickerInfoCarousel(aliasInfo, alias)
        line_message_sender.printStickerCarousel(event, 'PC에서는 볼수없또', carouselColumnArray)               

    return

def validateStickAdd(stickerList, newStickerInfo, event):
    # 하나의 키워드마다 스티커 저장 개수 벨리데이션
    if len(stickerList)>=5 :
        line_message_sender.printTextMessage(event, '스티커는 5개 넘게 저장할 수 없또')
        return False

    # 이미 있는 스티커면 무시
    for stickerInfo in stickerList:
        if stickerInfo.get('packageId')==newStickerInfo.get('packageId') and stickerInfo.get('stickerId')==newStickerInfo.get('stickerId'):
            line_message_sender.printTextMessage(event, '이미 그렇게 등록되어있또')
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
    line_message_sender.printTextMessage(event, '스티커가 ' + alias + '로 저장되어또!!!')

def answerSticker(**param):
    event = param['event']
    tokens = param['tokens']
    alias = tokens[0]
    aliasInfo = firebase.get('/customSticker', alias)

    if aliasInfo is None:
        return

    # 랜덤하게 하나를 고른다
    stickerList = aliasInfo.get('list')
    stickerInfo = random.choice(stickerList)

    packageId = stickerInfo['packageId']
    stickerId = stickerInfo['stickerId']

    # 스티커 전송 API 는 기본 내장 스티커만 전송 가능하므로, 이미지 메시지 전송 API 를 사용한다.
    line_message_sender.printStickerImage(event, packageId, stickerId)