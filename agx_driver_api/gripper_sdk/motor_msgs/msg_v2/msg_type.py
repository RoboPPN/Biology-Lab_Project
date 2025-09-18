#!/usr/bin/env python3
# -*-coding:utf8-*-

from enum import Enum, auto

class MsgType(Enum):
    # feedback
    Unkonwn = 0x00             #未知类型
    FeedbackHighSpdIndex = auto()
    FeedbackLowSpdIndex = auto()
    # transmit
    #----------------------------------基于V1.5-2版本后---------------------------------------------#
    MitCtrlIndex = auto()
    #---------------------------------------------------------------------------------------------#
    LightCtrl=auto()
    FirmwareRead=auto()
    def __str__(self):
        return f"{self.name} (0x{self.value:X})"
    def __repr__(self):
        return f"{self.name}: 0x{self.value:X}"