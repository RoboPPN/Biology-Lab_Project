# pylibrm

Python lib for RobustMotion's axis.


# 夹持电机
axis_rtu.move_to(15)
夹紧范围（0~15）
0：张开最大
15：夹最紧



# #精密推压 (距离10mm，受力50%，速度系数 0，冲击系数 0 ，力定位范围0.1N，稳压时间 100ms)
#axis_tcp.precise_push(10,0.5, 0, 0, 0.1, 100)

# ##绝对运动 (位置10mm，速度50mm/s，加速度 500mm/s2，减速度 500mm/s2 ，力定位范围0.1N)
#axis_tcp.move_absolute(10,50, 500, 500, 0.1)

#推压运动 (距离10mm，速度 20mm/s，出力15%，加速度 500mm/s2 ，位置范围0.1mm，时间范围500ms)
#axis_tcp.push(10, 20, 500, 0.15, 0.1, 500)

# #精密推压（距离10mm,受力10N,速度系数1，冲击系数0，力定位范围0.1N，稳压时,500ms）
# axis_tcp.precise_push(10,10,1,0,0.1,500)


# 旋转电机（用来拧盖子那个）
范围：0~无穷大  360°转一圈，以此类推



print(axis_rtu.position())  # 打印当前位置


# ##获取当前位置
# axis_tcp.position()