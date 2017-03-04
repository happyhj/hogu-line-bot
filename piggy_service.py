# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from message_sender import (
    printTextMessage
)

def hello(**param):
    event = param['event']
    printTextMessage(event, '불러또?')

def happyNewYear(**param):
    event = param['event']
    printTextMessage(event, "고마오 닝겐들아!! 새해 복 많이 받고 올해는 꼭 탈때지해야돼얌!")