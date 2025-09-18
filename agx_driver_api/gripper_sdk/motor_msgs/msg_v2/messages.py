#!/usr/bin/env python3
# -*-coding:utf8-*-

from abc import ABC, abstractmethod
import time
from enum import Enum, auto
import can
from can.message import Message

from typing import (
    Optional,
)
from .msg_type import MsgType
# 导入 feedback 子模块的类
from .feedback import *
# 导入 transmit 子模块的类
from .transmit import *

class Message:
    '''
    msg_v2
    
    全部消息,为所有消息的汇总
    '''
    def __init__(self, 
                #  反馈
                 type_: MsgType = None,
                 time_stamp: float = 0.0,
                 high_spd_feedback:FeedbackHighSpd=None,
                 low_spd_feedback:FeedbackLowSpd=None,
                #  发送
                 mit_ctrl: MitCtrl=None
                 ):
        #-------------------------------反馈-------------------------------------------
        # 初始化数据帧类型
        self.type_ = type_
        # 时间戳
        self.time_stamp = time_stamp
        # 驱动器信息高速反馈
        self.high_spd_feedback = high_spd_feedback if high_spd_feedback else FeedbackHighSpd()
        # 驱动器信息低速反馈
        self.low_spd_feedback = low_spd_feedback if low_spd_feedback else FeedbackLowSpd()
        # mit控制
        self.mit_ctrl = mit_ctrl if mit_ctrl else MitCtrl()
        self.firmware_data = bytearray()

    def __str__(self):
        # feedback
        if(self.type_ == MsgType.FeedbackHighSpdIndex):
            return (f"Type: {self.type_}\n"f"High Spd Feedback: {self.high_spd_feedback}\n")
        elif(self.type_ == MsgType.FeedbackLowSpdIndex):
            return (f"Type: {self.type_}\n"f"Low Spd Feedback: {self.low_spd_feedback}\n")
        else:    
            return (f"Type: {self.type_}\n")

    def __repr__(self):
        return self.__str__()