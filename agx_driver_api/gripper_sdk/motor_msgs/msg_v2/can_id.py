#!/usr/bin/env python3
# -*-coding:utf8-*-

from enum import Enum, auto

class CanID(Enum):
    #----------------------------------基于V1.5-2版本后---------------------------------------------#
    MIT_CTRL_INDEX = 0x410
    #---------------------------------------------------------------------------------------------#
    #灯光控制
    LIGHT_CTRL_INDEX = 0x720 #灯光控制指令
    #驱动器信息高速反馈
    FEEDBACK_HIGH_SPD_INDEX = 0x510
    #驱动器信息低速反馈
    FEEDBACK_LOW_SPD_INDEX = 0x520
    # 固件读取指令
    FIRMWARE_READ = 0x4AF
    def __str__(self):
        return f"{self.name} (0x{self.value:X})"
    def __repr__(self):
        return f"{self.name}: 0x{self.value:X}"