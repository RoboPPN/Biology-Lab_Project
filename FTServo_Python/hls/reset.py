#!/usr/bin/env python
#
# *********     Ping Example      *********
#
#
# Available SCServo model on this example : All models using Protocol SCS
# This example is tested with a SCServo(HLS), and an URT
#

import sys
import os
import time

sys.path.append("..")  # 将上级目录加入模块搜索路径，方便导入自定义库
from scservo_sdk import *                   # 导入FTServo SDK库中的所有内容


# 初始化串口端口处理实例
# 设置串口路径
# 获取PortHandlerLinux或PortHandlerWindows的方法和成员
portHandler = PortHandler('/dev/ttyUSB0') # Linux下的串口设备路径示例

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

# 舵机状态重置(清除圈数)
scs_comm_result, scs_error = packetHandler.reSet(1)  # 发送重置命令给ID为1的舵机
if scs_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(scs_comm_result))  # 通信失败错误信息
else:
    print("[ID:%03d] reset Succeeded." % (1))  # 重置成功提示
if scs_error != 0:
    print("%s" % packetHandler.getRxPacketError(scs_error))  # 协议错误信息

# 关闭串口
portHandler.closePort()