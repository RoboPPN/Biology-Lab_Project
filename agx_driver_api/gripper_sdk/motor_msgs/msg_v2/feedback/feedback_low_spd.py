#!/usr/bin/env python3
# -*-coding:utf8-*-
import math
from typing_extensions import (
    Literal,
)
class FeedbackLowSpd:
    '''
    msg_v2_feedback
    
    驱动器信息高速反馈 0x6

    节点 ID:
        0x1~0x06
    CAN ID:
        0X261~0x266

    Args:
        can_id: canid,表示当前电机序号
        vol: 当前驱动器电压
        foc_temp: 驱动器温度
        motor_temp: 电机温度
        foc_status: 驱动器状态码
        bus_current: 当前驱动器电流,单位0.001A,电机无母线电流采样,默认发送0
    
    位描述:
    
        Byte 0:电压高八位, uint16, 当前驱动器电压单位: 0.1V
        Byte 1:电压低八位
        Byte 2:驱动器温度高八位, int16, 单位: 1℃
        Byte 3:驱动器温度低八位
        Byte 4:电机温度,int8,单位: 1℃
        Byte 5:驱动器状态,uint8
            bit[0] 电源电压是否过低(0--正常; 1--过低)
            bit[1] 电机是否过温(0--正常; 1--过温)
            bit[2] 驱动器是否过流(0--正常; 1--过流)
            bit[3] 驱动器是否过温(0--正常; 1--过温)
            bit[4] 碰撞保护状态(0--正常; 1--触发保护)-7.25修改,之前为传感器状态
            bit[5] 驱动器错误状态(0: 正常; 1--错误)
            bit[6] 驱动器使能状态(1--使能; 0--失能)
            bit[7] 堵转保护状态(0--正常; 1--触发保护)-2024-7-25修改,之前为回零状态
        Byte 6:母线电流高八位,uint16,当前驱动器电流单位: 0.001A,电机无母线电流采样,默认发送0
        Byte 7:母线电流低八位
    '''
    def __init__(self, 
                 can_id: Literal[0x000, 0x521, 0x522, 0x523, 0x524, 0x524, 0x525, 0x526] = 0,
                 vol: float = 0, 
                 foc_temp: int = 0, 
                 motor_temp: int = 0,
                 foc_status: int = 0,
                 bus_current: int = 0,
                 ):
        self.can_id = can_id
        self.vol = vol
        self.foc_temp = foc_temp
        self.motor_temp = motor_temp
        self._foc_status_code = foc_status
        self.foc_status = self.FOC_Status()
        self.bus_current = bus_current

    class FOC_Status:
        def __init__(self):
            self.voltage_too_low  = False
            self.motor_overheating = False
            self.driver_overcurrent = False
            self.driver_overheating = False
            self.collision_status = False
            self.driver_error_status = False
            self.driver_enable_status = False
            self.stall_status  = False
        def __str__(self): 
            return (f"    voltage_too_low(bool): {self.voltage_too_low}\n"
                    f"    motor_overheating(bool): {self.motor_overheating}\n"
                    f"    driver_overcurrent(bool): {self.driver_overcurrent}\n"
                    f"    driver_overheating(bool): {self.driver_overheating}\n"
                    f"    collision_status(bool): {self.collision_status}\n"
                    f"    driver_error_status(bool): {self.driver_error_status}\n"
                    f"    driver_enable_status(bool): {self.driver_enable_status}\n"
                    f"    stall_status(bool): {self.stall_status}\n"
                    )

    @property
    def foc_status_code(self):
        return self._foc_status_code

    @foc_status_code.setter
    def foc_status_code(self, value: int):
        if not (0 <= value < 2**8):
            raise ValueError("foc_status_code must be an 8-bit integer between 0 and 255.")
        self._foc_status_code = value
        # Update foc_status based on the foc_status_code bits
        self.foc_status.voltage_too_low = bool(value & (1 << 0))
        self.foc_status.motor_overheating = bool(value & (1 << 1))
        self.foc_status.driver_overcurrent = bool(value & (1 << 2))
        self.foc_status.driver_overheating = bool(value & (1 << 3))
        self.foc_status.collision_status = bool(value & (1 << 4)) # 碰撞状态
        self.foc_status.driver_error_status = bool(value & (1 << 5))
        self.foc_status.driver_enable_status = bool(value & (1 << 6))
        self.foc_status.stall_status = bool(value & (1 << 7)) # 堵转状态

    def __str__(self):
        return (f"(\n"
                f"  can_id: {hex(self.can_id)}\n"
                f"  vol(V): {self.vol}\n"
                f"  foc_temp(C): {self.foc_temp }\n"
                f"  motor_temp(C): {self.motor_temp }\n"
                f"  foc_status: \n{self.foc_status}"
                f"  bus_current(mA): {self.bus_current}\n"
                f")")

    def __repr__(self):
        return self.__str__()
