#!/usr/bin/env python
#
# *********     Gen Write Example      *********
#
#
# Available SCServo model on this example : All models using Protocol SCS
# This example is tested with a SCServo(HLS), and an URT
#

import sys
import os
import time

sys.path.append("..")  # 将上级目录加入模块搜索路径，方便导入自定义库
from scservo_sdk import *  # 导入FTServo SDK库中的所有内容


def read(SCS_ID):
    while 1:
        # 读取指定ID舵机的当前位置和速度
        scs_present_position, scs_present_speed, scs_comm_result, scs_error = packetHandler.ReadPosSpeed(SCS_ID)
        if scs_comm_result != COMM_SUCCESS:
            # 通信失败时打印错误信息
            print(packetHandler.getTxRxResult(scs_comm_result))
        else:
            # 打印舵机ID、当前位置和速度
            print("[ID:%03d] PresPos:%d PresSpd:%d" % (SCS_ID, scs_present_position, scs_present_speed))
        if scs_error != 0:
            # 协议错误时打印错误信息
            print(packetHandler.getRxPacketError(scs_error))

        # 读取指定ID舵机的运动状态（是否在运动）
        moving, scs_comm_result, scs_error = packetHandler.ReadMoving(SCS_ID)
        if scs_comm_result != COMM_SUCCESS:
            # 通信失败时打印错误信息
            print(packetHandler.getTxRxResult(scs_comm_result))

        # 如果舵机停止运动，跳出循环
        if moving == 0:
            break
    return


# 初始化串口端口处理实例
# 设置串口路径，Linux示例为/dev/ttyUSB0
portHandler = PortHandler('/dev/ttyUSB0')

# 初始化协议处理实例，绑定端口处理实例
packetHandler = hls(portHandler)

# 打开串口
if portHandler.openPort():
    print("Succeeded to open the port")  # 打开成功提示
else:
    print("Failed to open the port")  # 打开失败提示
    quit()  # 退出程序

# 设置串口波特率为1000000
if portHandler.setBaudRate(1000000):
    print("Succeeded to change the baudrate")  # 设置成功提示
else:
    print("Failed to change the baudrate")  # 设置失败提示
    quit()  # 退出程序

while 1:
    # 发送舵机位置写入命令，ID为1，目标位置4095，最大速度60，最大加速度50，力矩500
    # 速度单位换算：60 * 0.732 = 43.92 rpm
    scs_comm_result, scs_error = packetHandler.WritePosEx(1, 4095, 60, 50, 500)
    if scs_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(scs_comm_result))  # 通信失败错误信息
    elif scs_error != 0:
        print("%s" % packetHandler.getRxPacketError(scs_error))  # 协议错误信息

    read(1)  # 读取ID为1的舵机状态，直到舵机运行到目标位置

    # 发送舵机位置写入命令，ID为1，目标位置0，最大速度60，最大加速度50，力矩500
    scs_comm_result, scs_error = packetHandler.WritePosEx(1, 0, 60, 50, 500)
    if scs_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(scs_comm_result))  # 通信失败错误信息
    elif scs_error != 0:
        print("%s" % packetHandler.getRxPacketError(scs_error))  # 协议错误信息

    read(1)  # 读取ID为1的舵机状态，直到舵机运行到目标位置

# 关闭串口
portHandler.closePort()