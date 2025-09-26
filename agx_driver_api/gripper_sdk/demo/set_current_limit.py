from gripper_sdk import *  # 导入gripper_sdk中的所有功能

if __name__ == "__main__":  
    controller = DriverApi()  # 创建驱动API的控制器实例
    controller.ConnectPort()  # 连接到设备端口
    # 设置零点必须失能
    controller.Disable()  # 禁用设备，确保安全设置零点
    # 设定电流限制为800
    a = controller.SetTorqueCurrentLimit(800.0)  # 发送设置限制电流命令
