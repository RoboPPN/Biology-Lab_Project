from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from RMAxis import Axis_V6
import openpyxl
import os
import time
from datetime import datetime
from time import sleep

import pylibrm
#测试连接rtu 和 tcp
#axis_tcp = Axis_V6.create_modbus_tcp('169.254.86.223' , 502, 1)

axis_rtu =Axis_V6.create_modbus_rtu('\\\\.\\COM13', 1, 115200)
axis_rtu2 =Axis_V6.create_modbus_rtu('\\\\.\\COM13', 2, 115200)
#axis_tcp.reset_error()
print(axis_rtu.position())
print(axis_rtu2.position())
#外部传感器
#axis_out =Axis_V6.create_modbus_rtu('\\\\.\\COM5', 7, 115200)

#设置重连次数和超时时间
# axis_tcp.set_retries(10)
# axis_tcp.set_timeout(100)# 100ms

#设置DM模式的 速度、加减速度
# axis_tcp.config_motion(50.2,40.3)

# axis_tcp.set_b0_state(0)
# axis_tcp.set_b1_state(0)
# axis_tcp.set_b3_state(0)

# axis_tcp.set_f1(1.11)
# axis_tcp.set_f2(2.22)
# axis_tcp.set_f3(3.33)

# axis_tcp.set_d0(10)
# axis_tcp.set_d1(100)
# axis_tcp.set_d2(1000)


#获取DM模式的 速度、加减速度
# print(axis_tcp.read_config_motion())

# #DM模式 移动到指定位置
# axis_tcp.move_to(10)

# #回原点
# axis_tcp.go_home()
# while(not axis_tcp.is_finished(15)):#等待到位
#     pass


# #设置点位
# ##set_command 第一个参数是要设置的点位标号，第二个参数是点位内容
# ###类型：无 next:-1
# command = dict()
# command["type"] = 0
# command["next_command_index"] = -1
# axis_tcp.set_command(0,command)
# axis_tcp.wait(axis_tcp._io_gap_time)
# axis_tcp.save_command()

# ###类型：设置原点 next:0
# command = dict()
# command["type"] = 1
# command["next_command_index"] = 0
# command["origin_offset"] = 0.2
# axis_tcp.set_command(1,command)
# axis_tcp.wait(axis_tcp._io_gap_time)
# axis_tcp.save_command()

# ###类型：延时 next:1
# command = dict()
# command["type"] = 2
# command["next_command_index"] = 1
# command["ms"]=1000
# axis_tcp.set_command(2,command)
# axis_tcp.wait(axis_tcp._io_gap_time)
# axis_tcp.save_command()

# ###类型：绝对运动 next:2
# command = dict()
# command["type"] = 3
# command["next_command_index"] = 2
# command["position"] = 1.1
# command["velocity"] = 2.2
# command["acceleration"] = 3.3
# command["deceleration"] = 4.4
# command["band"] = 5.5
# axis_tcp.set_command(3,command)
# axis_tcp.wait(axis_tcp._io_gap_time)
# axis_tcp.save_command()


# ###类型：推压运动 next:3
# command = dict()
# command["type"] = 4
# command["next_command_index"] = 3
# command["distance"] = 1.1
# command["force_limit"] = 0.22 # =>22%
# command["velocity"] = 3.3
# command["acceleration"] = 4.4
# command["pos_band_mm"] = 5.5
# command["time_band_ms"] = 6.6
# axis_tcp.set_command(4,command)
# axis_tcp.wait(axis_tcp._io_gap_time)
# axis_tcp.save_command()


# ###类型：相对运动 next:4
# command = dict()
# command["type"] = 5
# command["next_command_index"] = 4
# command["distance"] = 1.1
# command["velocity"] = 2.2
# command["acceleration"] = 3.3
# command["deceleration"] = 4.4
# command["band"] = 5.5
# axis_tcp.set_command(5,command)
# axis_tcp.wait(axis_tcp._io_gap_time)
# axis_tcp.save_command()


# ###类型：精密推压 next:5
# command = dict()
# command["type"] = 6
# command["next_command_index"] = 5
# command["distance"] = 1.1
# command["force"] = 2.2
# command["velocity_factor"] = 3.3
# command["impact_factor"] = 4.4
# command["band_n"] = 5.5
# command["band_ms"] = 6.6
# axis_tcp.set_command(6,command)
# axis_tcp.wait(axis_tcp._io_gap_time)
# axis_tcp.save_command()


# ###类型：重置力 next:6
# command = dict()
# command["type"] = 7
# command["next_command_index"] = 6

# axis_tcp.set_command(7,command)
# axis_tcp.wait(axis_tcp._io_gap_time)
# axis_tcp.save_command()


# ###类型：停止 next:7
# command = dict()
# command["type"] = 8
# command["next_command_index"] = 7

# axis_tcp.set_command(8,command)
# axis_tcp.wait(axis_tcp._io_gap_time)
# axis_tcp.save_command()

 
# # freq_hz 采集频率
# # count 采集数量
# # length 采集频道数 （最大值为3，对应下发三个参数是否生效）
# # var_0
# # var_1
# # var_2
# # 以上三个参数可以填入一下index：
# # 0 当前位置
# # 1 当前速度
# # 2 当前出力
# # 3 目标位置
# # 4 当前受力
# ###类型：开始采集 next:8
# command = dict()
# command["type"] = 9
# command["next_command_index"] = 8
# command["freq_hz"] = 1000
# command["length"] = 2 
# command["count"] = 3
# command["var_0"] = 4
# command["var_1"] = 5
# command["var_2"] = 6
# axis_tcp.set_command(9,command)
# axis_tcp.wait(axis_tcp._io_gap_time)
# axis_tcp.save_command()


# ###类型：Z回原点 next:9
# command = dict()
# command["type"] = 10
# command["next_command_index"] = 9
# command["distance"] = 1.1
# command["force_limit"] = 0.5 # ->50%
# command["velocity"] = 3.3
# command["acceleration"] = 4.4
# command["band_mm"] = 5.5
# axis_tcp.set_command(10,command)
# axis_tcp.wait(axis_tcp._io_gap_time)
# axis_tcp.save_command()


# ###类型：精密触碰 next:10
# command = dict()
# command["type"] = 11
# command["next_command_index"] = 10
# command["distance"] = 1.1
# command["velocity"] = 2.2
# command["acceleration"] = 3.3
# command["force_threshold"] = 4.4
# command["band_mm"] = 5.5
# axis_tcp.set_command(11,command)
# axis_tcp.wait(axis_tcp._io_gap_time)
# axis_tcp.save_command()


# #获取点位信息
# print(axis_tcp.get_command(0))
# print(axis_tcp.get_command(1))
# print(axis_tcp.get_command(2))
# print(axis_tcp.get_command(3))
# print(axis_tcp.get_command(4))
# print(axis_tcp.get_command(5))
# print(axis_tcp.get_command(6))
# print(axis_tcp.get_command(7))
# print(axis_tcp.get_command(8))
# print(axis_tcp.get_command(9))
# print(axis_tcp.get_command(10))
# print(axis_tcp.get_command(11))

##触发点位  获取到位信号
# command = dict()
# command["type"] = 3
# command["next_command_index"] = 15
# command["position"] = 20
# command["velocity"] = 50    
# command["acceleration"] = 50
# command["deceleration"] = 50
# command["band"] = 0.1
# axis_tcp.set_command(3,command)
# axis_tcp.wait(axis_tcp._io_gap_time)
# axis_tcp.save_command()
# axis_tcp.wait(axis_tcp._io_gap_time)
# axis_tcp.trig_command(3)
##判断到位信号
# while(not axis_tcp.is_finished(15)):
#     pass

# #保存点位
# axis_tcp.save_command()

# #保存参数
# axis_tcp.save_parameters()

# #执行点位
# command = dict()
# command["type"] = 3
# command["next_command_index"] = 15
# command["position"] = 20
# command["velocity"] = 50    
# command["acceleration"] = 50
# command["deceleration"] = 50
# command["band"] = 0.1
# axis_tcp.exec_command(command)


# #离线采集  获取采集结果
# command = dict()
# command["type"] = 3
# command["next_command_index"] =15
# command["position"] = 20
# command["velocity"] = 50
# command["acceleration"] = 50
# command["deceleration"] = 50
# command["band"] = 0.5
# axis_tcp.set_command(1,command)
# axis_tcp.wait(axis_tcp._io_gap_time)
# axis_tcp.save_command()
# axis_tcp.start_monitor(1,1000,1,200,0,0,0)
# sample_result =axis_tcp.sample_result()
# print(sample_result)

# #精密推压 (距离10mm，受力50%，速度系数 0，冲击系数 0 ，力定位范围0.1N，稳压时间 100ms)
#axis_tcp.precise_push(10,0.5, 0, 0, 0.1, 100)

# ##绝对运动 (位置10mm，速度50mm/s，加速度 500mm/s2，减速度 500mm/s2 ，力定位范围0.1N)
#axis_tcp.move_absolute(10,50, 500, 500, 0.1)

#推压运动 (距离10mm，速度 20mm/s，出力15%，加速度 500mm/s2 ，位置范围0.1mm，时间范围500ms)
#axis_tcp.push(10, 20, 500, 0.15, 0.1, 500)

# #精密推压（距离10mm,受力10N,速度系数1，冲击系数0，力定位范围0.1N，稳压时,500ms）
# axis_tcp.precise_push(10,10,1,0,0.1,500)


# #Z回原点(距离10mm,速度20mm/s,加速度100mm/s2,出力15%,定位范围0.1mm)
# axis_tcp.go_home_z(10,20,100,0.15,0.1)

# #精密触碰(距离10mm,速度20mm/s,加速度100mm/s2,力阈值 0.1N,定位范围0.1mm)
# axis_tcp.precise_touch(10,20,100,0.1,0.1)


# #到位信号判断 0~15
# axis_tcp.is_finished(0)

# #只能用于判断指令15是否完成,且速度达标(+-2以内) 判断是否在moving
# axis_tcp.is_moving()

# #判断夹持（推压运动）
# axis_tcp.is_captured()

# #只能判断 绝对运动,精密推压,相對運動
# axis_tcp.is_reached()

# #状态0 pending, 1完成   2停止   3位置到达   4力到达
# axis_tcp.get_command_status()

# # #获取错误码
# # #0  无错误
# # #-10  位置超差

# # #-20  速度超差
# # #-30  位置超差 + 速度超差 

# # #-40  堵转

# # #-60  力阈值报警
  
# # #-50  堵转 + 位置超差
# # #-60  堵转 + 速度超差
# # #-70  堵转 + 位置超差 + 速度超差


# axis_tcp.error_code()

# ##重置错误
# axis_tcp.reset_error()

# ##重置力
# axis_tcp.reset_force()

# ##设置私服状态 1:开 0:g关
# axis_tcp.set_servo_on_off(1)

# ##停止
# axis_tcp.stop()

# ##获取当前位置
# axis_tcp.position()

# ##获取当前速度
# axis_tcp.velocity()

# ##获取当前位力矩
# axis_tcp.torque()

# ##获取当前受力
# axis_tcp.force_sensor()

# ##使能位置、速度、堵转警报
# axis_tcp.enable_error_position_deviation_overflow(1)
# axis_tcp.enable_error_velocity_deviation_overflow(1)
# axis_tcp.enable_motor_stuck(1)

# ## 精密推压 传入点位序号2 和 力的大小20N
# axis_tcp.set_command_force(2, 20)

# ## 绝对运动 传入点位序号2 和 移动的位置20mm
# axis_tcp.set_command_pos(2, 20)

#获取外部传感器读数
# axis_out.read_external_force()
