#!/usr/bin/env python3
# -*-coding:utf8-*-
import math
from typing_extensions import (
    Literal,
)
class FeedbackHighSpd:
    '''
    msg_v2_feedback
    
    驱动器信息高速反馈 0x5

    节点 ID:
        0x1~0x06
    
    CAN ID:
        0X251~0x256

    Args:
        can_id: 当前canid,用来代表序号
        motor_speed: 电机当前转速
        current: 电机当前电流
        pos: 电机当前位置
        effort: 经过固定系数转换的力矩,单位0.001N/m
    
    位描述:

        Byte 0: 转速高八位, int16, 电机当前转速 单位: 0.001rad/s
        Byte 1: 转速低八位
        Byte 2: 电流高八位, uint16, 电机当前电流 单位: 0.001A
        Byte 3: 电流低八位
        Byte 4: 位置最高位, int32, 电机当前位置 单位: rad
        Byte 5: 位置次高位
        Byte 6: 位置次低位
        Byte 7: 位置最低位
    '''
    def __init__(self, 
                 can_id: Literal[0x000, 0x511, 0x512, 0x513, 0x514, 0x515, 0x516] = 0,
                 motor_speed: float = 0, 
                 current: int = 0, 
                 pos: float = 0
                 ):
        self.can_id = can_id
        self.motor_speed = motor_speed
        self.current = current
        self.pos = pos

    def __str__(self):
        return (f"(\n"
                f"  can_id: {hex(self.can_id)}\n"
                f"  motor_speed(rad/s): {self.motor_speed}\n"
                f"  current(mA): {self.current}\n"
                f"  pos(rad): {self.pos}\n"
                f")")

    def __repr__(self):
        return self.__str__()
