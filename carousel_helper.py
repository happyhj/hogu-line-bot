from linebot.models import (
    CarouselTemplate, 
    CarouselColumn,
    MessageTemplateAction,
)

def buildSavedStickerInfoCarousel(stickerList, alias):
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
                        label='delete',
                        text='@stk.remove '+alias+ ' '+ packageId + ' ' + stickerId
                    )
                ]
            )
        )
    return carouselColumnArray
