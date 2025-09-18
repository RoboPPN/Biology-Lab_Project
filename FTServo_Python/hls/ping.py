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

sys.path.append("..")  # 将上级目录加入模块搜索路径，方便导入自定义库
from scservo_sdk import *  # 导入FTServo SDK库中的所有内容


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

# 尝试ping ID为1的舵机，获取其型号信息
scs_model_number, scs_comm_result, scs_error = packetHandler.ping(1)
if scs_comm_result != COMM_SUCCESS:
    # 通信失败时打印错误信息
    print("%s" % packetHandler.getTxRxResult(scs_comm_result))
else:
    # 通信成功时打印舵机ID和型号
    print("[ID:%03d] ping Succeeded. SCServo model number : %d" % (1, scs_model_number))
if scs_error != 0:
    # 协议错误时打印错误信息
    print("%s" % packetHandler.getRxPacketError(scs_error))

# 关闭串口
portHandler.closePort()