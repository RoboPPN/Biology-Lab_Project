#!/usr/bin/env python3
# -*-coding:utf8-*-

from typing import (
    Optional,
)
from .msg_type import MsgType
from .can_id import CanID

class MessageMapping:
    # 初始化映射字典
    id_to_type_mapping = {
        # 反馈,feedback
        CanID.FEEDBACK_HIGH_SPD_INDEX.value: MsgType.FeedbackHighSpdIndex,
        CanID.FEEDBACK_LOW_SPD_INDEX.value: MsgType.FeedbackLowSpdIndex,
        # 发送,transmit
        #----------------------------------基于V1.5-2版本后---------------------------------------------#
        CanID.MIT_CTRL_INDEX.value: MsgType.MitCtrlIndex,
        #---------------------------------------------------------------------------------------------#
        CanID.LIGHT_CTRL_INDEX.value: MsgType.LightCtrl,
        CanID.FIRMWARE_READ.value: MsgType.FirmwareRead,
    }

    type_to_id_mapping = {v: k for k, v in id_to_type_mapping.items()}

    @staticmethod
    def get_mapping(can_id: Optional[int] = None, msg_type: Optional[MsgType] = None):
        '''
        根据输入的参数返回对应的映射值，输入 id 返回类型，输入类型返回 id
        
        :param can_id: CAN ID
        :param msg_type: 消息类型
        :return: 对应的类型或 id
        '''
        if can_id is not None and msg_type is not None:
            raise ValueError("只能输入 CAN ID 或消息类型中的一个")

        if can_id is not None:
            if can_id in MessageMapping.id_to_type_mapping:
                return MessageMapping.id_to_type_mapping[can_id]
            else:
                raise ValueError(f"CAN ID {can_id} 不在映射中")

        if msg_type is not None:
            if msg_type in MessageMapping.type_to_id_mapping:
                return MessageMapping.type_to_id_mapping[msg_type]
            else:
                raise ValueError(f"消息类型 {msg_type} 不在映射中")

        raise ValueError("必须输入 CAN ID 或消息类型中的一个")

# # 测试代码
# if __name__ == "__main__":
#     # 根据 ID 查找类型
#     print(MessageMapping.get_mapping(can_id=0x2A2))

#     # 根据类型查找 ID
#     print(MessageMapping.get_mapping(msg_type=MsgType.MitCtrlIndex))  # 输出: 0x2A7
