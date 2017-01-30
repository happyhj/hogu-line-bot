from message_sender import (
    printStickerImage
)

def answerStickerPreview(**param):
    event = param['event']
    packageId = param['tokens'][0]
    stickerId = param['tokens'][1]
    printStickerImage(event, packageId, stickerId)