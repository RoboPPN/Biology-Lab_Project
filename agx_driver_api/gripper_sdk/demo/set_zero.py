from gripper_sdk import *  # 导入gripper_sdk中的所有功能
import time  

if __name__ == "__main__":  
    controller = DriverApi()  # 创建驱动API的控制器实例
    controller.ConnectPort()  # 连接到设备端口
    # 设置零点必须失能
    controller.Disable()  # 禁用设备，确保安全设置零点
    # 设定零点
    a = controller.SetZero()  # 发送设置零点命令
    while True:  # 循环等待零点设置响应
        # 检测设置零点是否成功
        if(controller.GetRespSetZero().msg.zero_val == 0xAC):  # 判断响应消息中的零点值是否为0xAC，表示成功
            print(controller.GetRespSetZero())  # 打印响应消息
            print("Set zero successfully!!")  # 打印成功提示
            controller.ClearRespSetZero()  # 清除零点响应消息缓存
            exit(0)  # 退出程序
        time.sleep(0.01)  # 每次循环等待10毫秒，避免CPU占用过高
    print("Is Not Ok, exit")  # 如果循环结束，打印失败提示