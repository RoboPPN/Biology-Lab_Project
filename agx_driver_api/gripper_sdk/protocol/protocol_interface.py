#!/usr/bin/env python3
# -*-coding:utf8-*-
#协议V1版本，为方便后续修改协议升级，继承自base
import can
from typing import (
    Optional,
)

# import sys,os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from .protocol_base import ParserBase
from ..motor_msgs.msg_v2 import (
    MsgType, 
    CanID,
    MessageMapping,
    Message
)

class ParserInterface(ParserBase):
    '''
    can解析数据类V2版本
    '''
    def __init__(self) -> None:
        super().__init__()
        pass

    def GetParserProtocolVersion(self):
        '''
        获取当前协议版本,当前为V2
        '''
        '''
        Get the current protocol version, currently V2.
        '''
        return self.ProtocolVersion.PROROCOL_V2

    def DecodeMessage(self, rx_can_frame: Optional[can.Message], msg:Message):
        '''解码消息,将can数据帧转为设定的类型

        Args:
            rx_can_frame (Optional[can.Message]): can 数据帧, 为输入
            msg (Message): 自定义中间层数据, 为输出

        Returns:
            bool:
                can消息的id如果存在, 反馈True

                can消息的id若不存在, 反馈False
        '''
        '''Decode the message, convert the CAN data frame to the specified type.

        Args:

            rx_can_frame (Optional[can.Message]): CAN data frame, input.
            msg (Message): Custom intermediate data, output.

        Returns:

            bool:
                If the CAN message ID exists, return True.
                If the CAN message ID does not exist, return False.
        '''
        ret:bool = True
        can_id:int = rx_can_frame.arbitration_id
        can_data:bytearray = rx_can_frame.data
        can_time_now = rx_can_frame.timestamp
        # 固件版本
        if(can_id == CanID.FIRMWARE_READ.value):
            msg.type_ = MessageMapping.get_mapping(can_id=can_id)
            msg.time_stamp = can_time_now
            msg.firmware_data = can_data
        else:
            ret = False
        return ret

    def EncodeMessage(self, msg:Message, tx_can_frame: Optional[can.Message]):
        '''将消息转为can数据帧

        Args:
            msg (Message): 自定义数据
            tx_can_frame (Optional[can.Message]): can要发送的数据

        Returns:
            bool:
                msg消息的type如果存在, 反馈True

                msg消息的type若不存在, 反馈False
        '''
        '''Convert the message to CAN data frame

        Args:
            msg (Message): Custom data
            tx_can_frame (Optional[can.Message]): CAN data to be sent

        Returns:
            bool:
                Returns True if the msg message type exists
                Returns False if the msg message type does not exist
        '''
        ret:bool = True
        msg_type_ = msg.type_
        tx_can_frame.arbitration_id = MessageMapping.get_mapping(msg_type=msg_type_)
        # MIT单独控制电机
        if(msg_type_ == MsgType.MitCtrlIndex):
            tx_can_frame.data = self.ConvertToList_16bit(msg.mit_ctrl.pos_ref,False) + \
                                self.ConvertToList_8bit(((msg.mit_ctrl.vel_ref >> 4)&0xFF),False) + \
                                self.ConvertToList_8bit(((((msg.mit_ctrl.vel_ref&0xF)<<4)&0xF0) | 
                                                         ((msg.mit_ctrl.kp>>8)&0x0F)),False) + \
                                self.ConvertToList_8bit(msg.mit_ctrl.kp&0xFF,False) + \
                                self.ConvertToList_8bit((msg.mit_ctrl.kd>>4)&0xFF,False) + \
                                self.ConvertToList_8bit(((((msg.mit_ctrl.kd&0xF)<<4)&0xF0)|
                                                         ((msg.mit_ctrl.t_ref>>4)&0x0F)),False)
            crc = (tx_can_frame.data[0]^tx_can_frame.data[1]^tx_can_frame.data[2]^tx_can_frame.data[3]^tx_can_frame.data[4]^tx_can_frame.data[5]^ \
                tx_can_frame.data[6])&0x0F
            msg.mit_ctrl.crc = crc
            tx_can_frame.data = tx_can_frame.data + self.ConvertToList_8bit((((msg.mit_ctrl.t_ref<<4)&0xF0) | crc),False)
        else:
            ret = False
        return ret
            

