import os
import sys

from linebot import (
    LineBotApi, WebhookParser
)

def getParser():
    # get channel_secret and channel_access_token from your environment variable
    channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
    if channel_secret is None:
        print('Specify LINE_CHANNEL_SECRET as environment variable.')
        sys.exit(1)

    parser = WebhookParser(channel_secret)
    return parser