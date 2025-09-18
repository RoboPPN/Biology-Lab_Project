from gripper_sdk import *  # 导入gripper_sdk中的所有功能
import time  

if __name__ == "__main__":  # 判断是否为主程序入口
    controller = DriverApi()  # 创建驱动API的控制器实例
    controller.ConnectPort()  # 连接到设备端口
    while controller.isOk():  # 循环检测设备状态是否正常
       
        gripper_pos = controller.GetPos()  # 获取电机当前位置，单位：弧度(rad)
        print("夹爪当前位置：", gripper_pos)  # 打印当前位置
        
        motor_vel = controller.GetVel()  # 获取电机当前速度,单位：rad/s
        print("电机当前速度：", motor_vel)  # 打印电机速度
        
        motor_temp = controller.GetTemp()  # 获取电机温度,单位：摄氏度(℃)
        print("电机温度：", motor_temp)  # 打印电机温度
        
        time.sleep(0.01)  # 每次循环等待10毫秒，避免CPU占用过高