from gripper_sdk import *  # 导入gripper_sdk中的所有功能
import time  

if __name__ == "__main__": 
    controller = DriverApi()  # 创建驱动API的控制器实例
    controller.ConnectPort()  # 连接到设备端口
    controller.Enable()  # 使能设备
    print("Enabling...")  # 打印使能提示
    while controller.isOk():  # 循环检测设备状态是否正常
        if controller.GetEnableStatus():  # 如果设备已经使能
            print("Enable successfully")  # 打印使能成功提示
            print("move to 1.5 rad pos")  # 打印移动到1.5弧度位置提示
            controller.GripperCtrl(1.5)  # 控制设备移动到1.5弧度位置
            time.sleep(1.1)  # 等待1.1秒，确保动作完成
            print("move to 0 rad pos")  # 打印移动到0弧度位置提示
            controller.GripperCtrl(0)  # 控制设备移动到0弧度位置
            time.sleep(1.1)  # 等待1.1秒
            print("Disabling...")  # 打印禁用提示
            controller.Disable()  # 禁用设备
            exit(0)  # 退出程序