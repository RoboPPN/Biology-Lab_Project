#!/usr/bin/env python
#
# *********     Sync Write Example      *********
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

while 1:
    for scs_id in range(1, 11):
        # 将舵机ID从1到10的目标位置、移动速度和加速度添加到同步写参数缓存中
        # 舵机(ID1~10)以最大速度V=60*0.732=43.92rpm和加速度A=50*8.7deg/s^2运行，目标位置P1=4095
        # 力矩设为500
        scs_addparam_result = packetHandler.SyncWritePosEx(scs_id, 4095, 60, 50, 500)  # 添加同步写参数
        if scs_addparam_result != True:
            print("[ID:%03d] groupSyncWrite addparam failed" % scs_id)  # 添加失败提示

    # 发送同步写数据包，执行所有舵机的同步动作
    scs_comm_result = packetHandler.groupSyncWrite.txPacket()
    if scs_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(scs_comm_result))  # 发送失败错误信息

    # 清空同步写参数缓存
    packetHandler.groupSyncWrite.clearParam()

    # 计算等待时间，确保所有舵机运动完成
    time.sleep(((4095-0)/(60*50) + (60*50)/(50*100) + 0.05))  # 运动时间估算公式

    for scs_id in range(1, 11):
        # 将舵机ID从1到10的目标位置、移动速度和加速度添加到同步写参数缓存中
        # 舵机(ID1~10)以最大速度V=60*0.732=43.92rpm和加速度A=50*8.7deg/s^2运行，目标位置P0=0
        # 力矩设为500
        scs_addparam_result = packetHandler.SyncWritePosEx(scs_id, 0, 60, 50, 500)  # 添加同步写参数
        if scs_addparam_result != True:
            print("[ID:%03d] groupSyncWrite addparam failed" % scs_id)  # 添加失败提示

    # 发送同步写数据包，执行所有舵机的同步动作
    scs_comm_result = packetHandler.groupSyncWrite.txPacket()
    if scs_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(scs_comm_result))  # 发送失败错误信息
    
    # 清空同步写参数缓存
    packetHandler.groupSyncWrite.clearParam()
    
    # 计算等待时间，确保所有舵机运动完成
    time.sleep(((4095-0)/(60*50) + (60*50)/(50*100) + 0.05))  # 运动时间估算公式

# 关闭串口
portHandler.closePort()