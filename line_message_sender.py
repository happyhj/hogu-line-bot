import os
from linebot import (
    LineBotApi
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

channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
line_bot_api = LineBotApi(channel_access_token)

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

def printStickerCarousel(event, altText, carouselColumnArray):
    line_bot_api.reply_message(
        event.reply_token,
        TemplateSendMessage(
            alt_text=altText,
            template=CarouselTemplate(columns=carouselColumnArray)
        )
    )