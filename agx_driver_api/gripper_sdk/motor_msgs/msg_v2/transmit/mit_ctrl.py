#!/usr/bin/env python3
# -*-coding:utf8-*-

class MitCtrl():
    '''
    msg_v2_transmit
    
    mit控制
    
    CAN ID:
        0x41x
    
    Args:
        pos_ref: 设定期望的目标位置
        vel_ref: 设定电机运动的速度
        kp: 比例增益，控制位置误差对输出力矩的影响
        kd: 微分增益，控制速度误差对输出力矩的影响
        t_ref: 目标力矩参考值，用于控制电机施加的力矩或扭矩
        crc: 循环冗余校验，用于数据完整性验证
    
    位描述:
    
        Byte 0: Pos_ref [bit15~bit8] 高8位
        Byte 1: Pos_ref [bit7~bit0]  低8位
        Byte 2: Vel_ref [bit11~bit4] 低12位
        Byte 3: Vel_ref [bit3~bit0], Kp [bit11~bit8]
        Byte 4: Kp [bit7~bit0],      Kp给定参考值: 10
        Byte 5: Kd [bit11~bit4]      低12位,Kd给定参考值: 0.8
        Byte 6: Kd [bit3~bit0] T_ref [bit7~bit4]
        Byte 7: T_ref [bit3~bit0] CRC [bit3~bit0]
    '''
    def __init__(self, 
                 pos_ref = 0, 
                 vel_ref = 0, 
                 kp = 10, 
                 kd = 0.8,
                 t_ref = 0, 
                 crc = 0):
        self.pos_ref = pos_ref
        self.vel_ref = vel_ref
        self.kp = kp
        self.kd = kd
        self.t_ref = t_ref
        self.crc = crc
    
    def __str__(self):
        # 将角度乘以0.001，并保留三位小数
        mit_args = [
            ("pos_ref", self.pos_ref),
            ("vel_ref", self.vel_ref ),
            ("kp", self.kp ),
            ("kd", self.kd ),
            ("t_ref", self.t_ref ),
            ("crc", self.crc )
        ]

        # 生成格式化字符串，保留三位小数
        formatted_str = "\n".join([f"{name}: {param}" for name, param in mit_args])
        
        return f"MitCtrl:\n{formatted_str}"
    
    def __repr__(self):
        return self.__str__()
