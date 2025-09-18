from RMAxis import Axis_V6
import time

axis_rtu =Axis_V6.create_modbus_rtu('/dev/ttyUSB0', 115200, 1)

axis_rtu2 =Axis_V6.create_modbus_rtu('/dev/ttyUSB0', 115200, 2)

print(axis_rtu.position())

# axis_rtu.go_home()
# axis_rtu2.go_home()

# axis_rtu.move_to(0)

##绝对运动 (位置10mm，速度50mm/s，加速度 500mm/s2，减速度 500mm/s2 ，力定位范围0.1N)、
axis_rtu.move_absolute(10,500, 500, 500, 0.1)

#推压运动 (往前推进距离5mm，速度 20mm/s，出力15%，加速度 500mm/s2 ，位置范围0.1mm，时间范围500ms)
axis_rtu.push(5, 20, 500, 0.6, 0.1, 500)


##绝对运动 (位置10mm，速度50mm/s，加速度 500mm/s2，减速度 500mm/s2 ，力定位范围0.1N)
axis_rtu2.move_absolute(720,500, 500, 500, 0.1)

time.sleep(2)

##绝对运动 (位置10mm，速度50mm/s，加速度 500mm/s2，减速度 500mm/s2 ，力定位范围0.1N)、
axis_rtu.move_absolute(0,500, 500, 500, 0.1)


##绝对运动 (位置10mm，速度50mm/s，加速度 500mm/s2，减速度 500mm/s2 ，力定位范围0.1N)
axis_rtu2.move_absolute(0,500, 500, 500, 0.1)


# print("ERROR CODE: ",axis_rtu.error_code())
# print("ERROR CODE: ",axis_rtu2.error_code())


# axis_rtu.reset_error()
