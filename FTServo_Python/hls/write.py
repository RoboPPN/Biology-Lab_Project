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
from scservo_sdk import *                      # 导入FTServo SDK库中的所有内容


# 初始化串口端口处理实例
# 设置串口路径
# 获取PortHandlerLinux或PortHandlerWindows的方法和成员
portHandler = PortHandler('/dev/ttyUSB0')  # Linux下的串口设备路径示例

# 初始化协议处理实例
# 获取协议相关的方法和成员
packetHandler = hls(portHandler)  # 使用hls协议类，绑定端口处理实例
    
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

# 舵机(ID1)
scs_comm_result, scs_error = packetHandler.WritePosEx(1, 3500, 80, 80, 800)  # 发送位置命令，参数含义依次为ID, 目标位置, 速度, 加速度, 力矩
if scs_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(scs_comm_result))  # 通信失败错误信息
elif scs_error != 0:
    print("%s" % packetHandler.getRxPacketError(scs_error))  # 协议错误信息

# 等待时间，确保舵机运动完成
time.sleep(1) 

# 舵机(ID2)
scs_comm_result, scs_error = packetHandler.WritePosEx(2, 800, 80, 80, 800)  # 发送位置命令，参数含义依次为ID, 目标位置, 速度, 加速度, 力矩
if scs_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(scs_comm_result))
elif scs_error != 0:
    print("%s" % packetHandler.getRxPacketError(scs_error))

# 等待时间，确保运动完成
time.sleep(1)

# 关闭串口
portHandler.closePort()