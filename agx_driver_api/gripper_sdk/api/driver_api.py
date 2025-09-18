#!/usr/bin/env python3
# -*-coding:utf8-*-

import time
import can
from can.message import Message
from typing import (
    Optional,
    Type
)
from typing_extensions import (
    Literal,
)
from queue import Queue
import threading
import math
import struct
from ..hardware_port import *
from ..protocol.protocol_interface import ParserInterface
from ..motor_msgs.msg_v2 import *
from ..utils import *
from ..utils import logger, global_area
from ..version import ApiVersion

class DriverApi():
    '''
    Args:
        can_name(str): can port name
        judge_flag(bool): Determines if the CAN port is functioning correctly.
                        When using a PCIe-to-CAN module, set to false.
        can_auto_init(bool): Determines if the CAN port is automatically initialized.
        dh_is_offset([0,1] -> default 0x01): Does the j1-j2 offset by 2° in the DH parameters? 
                    0 -> No offset
                    1 -> Offset applied
        start_sdk_joint_limit(bool -> False):Whether to enable the software joint limit of SDK
        start_sdk_gripper_limit(bool -> False):Whether to enable the software gripper limit of SDK
    '''
    
    class MotorInfo():
        '''
        电机驱动高速反馈信息
        '''
        def __init__(self):
            self.time_stamp: float=0
            self.Hz: float = 0
            self.msg=FeedbackHighSpd()
        def __str__(self):
            return (f"time_stamp:{self.time_stamp}\n"
                    f"Hz:{self.Hz}\n"
                    f"msg:{self.msg}\n")
    
    class DriverInfo():
        '''
        电机驱动低速反馈信息
        '''
        def __init__(self):
            self.time_stamp: float=0
            self.Hz: float = 0
            self.msg=FeedbackLowSpd()
        def __str__(self):
            return (f"time_stamp:{self.time_stamp}\n"
                    f"Hz:{self.Hz}\n"
                    f"msg:{self.msg}\n")
    
    class RespSetZero():
        '''
        电机驱动低速反馈信息
        '''
        def __init__(self):
            self.time_stamp: float=0
            self.msg=FeedbackRespSetZero()
        def __str__(self):
            return (f"time_stamp:{self.time_stamp}\n"
                    f"msg:{self.msg}\n")
    
    _instances = {}  # 存储不同参数的实例
    _lock = threading.Lock()

    def __new__(cls, 
                can_name:str="can0", 
                judge_flag=True,
                can_auto_init=True,
                # reconnect_after_disconnection:bool = False,
                logger_level:LogLevel = LogLevel.WARNING,
                log_to_file:bool = False,
                log_file_path = None):
        """
        实现单例模式：
        - 相同 can_name参数，只会创建一个实例
        - 不同参数，允许创建新的实例
        """
        key = (can_name)  # 生成唯一 Key
        with cls._lock:
            if key not in cls._instances:
                instance = super().__new__(cls)  # 创建新实例
                instance._initialized = False  # 确保 init 只执行一次
                cls._instances[key] = instance  # 存入缓存
        return cls._instances[key]

    def __init__(self,
                can_name:str="can0",
                judge_flag=True,
                can_auto_init=True,
                # reconnect_after_disconnection:bool = False,
                logger_level:LogLevel = LogLevel.WARNING,
                log_to_file:bool = False,
                log_file_path = None) -> None:
        if getattr(self, "_initialized", False): 
            return  # 避免重复初始化
        # log
        LogManager.update_logger(global_area=global_area,
                                 local_area="InterfaceV2", 
                                 level=logger_level, 
                                 log_to_file=log_to_file, 
                                 log_file_path=log_file_path,
                                 file_mode='a',
                                 force_update=True)
        self.__local_area = self._instances
        self.logger = LogManager.get_logger(global_area, self.__local_area)
        logging.getLogger("can").setLevel(logger_level)
        self.logger.info("CAN interface created")
        self.logger.info("%s = %s", "can_name", can_name)
        self.logger.info("%s = %s", "judge_flag", judge_flag)
        self.logger.info("%s = %s", "can_auto_init", can_auto_init)
        # self.logger.info("%s = %s", "reconnect_after_disconnection", reconnect_after_disconnection)
        self.logger.info("%s = %s", "logger_level", logger_level)
        self.logger.info("%s = %s", "log_to_file", log_to_file)
        self.logger.info("%s = %s", "log_file_path", LogManager.get_log_file_path(global_area))
        self.__can_channel_name:str
        if isinstance(can_name, str):
            self.__can_channel_name = can_name
        else:
            raise IndexError("Input can name is not str type")
        self.__num = 7
        self.__can_judge_flag = judge_flag
        self.__can_auto_init = can_auto_init
        # self.__reconnect_after_disconnection = reconnect_after_disconnection
        try:
            self.__can_inter=CanInterface(can_name, "socketcan", 1000000, judge_flag, can_auto_init, self.ParseCANFrame)
        except Exception as e:
            self.logger.error(e)
            raise ConnectionError("['%s' Interface __init__ ERROR]" % can_name)
            # self.logger.error("exit...")
            # exit()
        self.__start_sdk_fk_cal = False
        # protocol
        self.__parser: Type[ParserInterface] = ParserInterface()
        # thread
        self.__read_can_stop_event = threading.Event()  # 控制 ReadCan 线程
        self.__can_monitor_stop_event = threading.Event()  # 控制 CanMonitor 线程
        self.__lock = threading.Lock()  # 保护线程安全
        self.__can_deal_th = None
        self.__can_monitor_th = None
        self.__connected = False  # 连接状态
        # FPS cal
        self.__fps_counter = FpsCounter()
        self.__fps_counter.set_cal_fps_time_interval(0.1)
        self.__fps_counter.add_variable("CanMonitor")
        self.__q_can_fps = Queue(maxsize=5)
        self.__is_ok_mtx = threading.Lock()
        self.__is_ok = True
        self.__fps_counter.add_variable("FpsMotorInfo")
        self.__fps_counter.add_variable("FpsDriverInfo")
        # 固件版本
        self.__firmware_data_mtx = threading.Lock()
        self.__firmware_data = bytearray()

        self.__motor_info_mtx = threading.Lock()
        self.__motor_info = self.MotorInfo()

        self.__driver_info_low_spd_mtx = threading.Lock()
        self.__driver_info_low_spd = self.DriverInfo()

        self.__resp_set_zero_mtx = threading.Lock()
        self.__resp_set_zero = self.RespSetZero()

        self._initialized = True  # 标记已初始化
    
    @classmethod
    def get_instance(cls, can_name="can0", judge_flag=True, can_auto_init=True):
        """获取实例，简化调用"""
        return cls(can_name, judge_flag, can_auto_init)
    
    def get_connect_status(self):
        return self.__connected

    def ConnectPort(self, 
                    can_init :bool = False, 
                    device_init :bool = True, 
                    start_thread :bool = True):
        '''
        Starts a thread to process data from the connected CAN port.
        
        Args:
            can_init(bool): can port init flag, Behind you using DisconnectPort(), you should set it True.
            device_init(bool): Execute the robot arm initialization function
            start_thread(bool): Start the reading thread
        '''
        if(can_init or not self.__connected):
            self.logger.info("[ConnectPort] Start Can Init")
            init_status = None
            try:
                # self.__can_inter=CanInterface(self.__can_channel_name, "socketcan", 1000000, False, False, self.ParseCANFrame)
                init_status = self.__can_inter.Init()
            except Exception as e:
                # self.__can_inter = None
                self.logger.error("[ConnectPort] can bus create: %s", e)
            self.logger.info("[ConnectPort] init_status: %s", init_status)
        # 检查线程是否开启
        with self.__lock:
            if self.__connected:
                return
            self.__connected = True
            self.__read_can_stop_event.clear()
            self.__can_monitor_stop_event.clear()  # 允许线程运行
        # 读取can数据线程----------------------------------------------------------
        def ReadCan():
            self.logger.info("[ReadCan] ReadCan Thread started")
            while not self.__read_can_stop_event.is_set():
                # self.__fps_counter.increment("CanMonitor")
                # if(self.__can_inter is None):
                #     try:
                #         self.logger.debug("[ReadCan] __can_inter create")
                #         self.__can_inter=CanInterface(self.__can_channel_name, "socketcan", 1000000, self.__can_judge_flag, False, self.ParseCANFrame)
                #     except Exception as e:
                #         pass
                #     continue
                try:
                    read_status = self.__can_inter.ReadCanMessage()
                    # if(read_status != self.__can_inter.CAN_STATUS.READ_CAN_MSG_OK):
                    #     time.sleep(0.00002)
                    # if self.__reconnect_after_disconnection:
                    #     if(read_status != self.__can_inter.CAN_STATUS.READ_CAN_MSG_OK):
                    #         try:
                    #             self.logger.debug("[ReadCan] can_reconnect -> close")
                    #             self.__can_inter.Close()
                    #             self.logger.debug("[ReadCan] can_reconnect -> init")
                    #             self.__can_inter.Init()
                    #         except Exception as e:
                    #             pass
                    # self.logger.debug("[ReadCan] read_status: %s", read_status)
                except can.CanOperationError:
                    self.logger.error("[ReadCan] CAN is closed, stop ReadCan thread")
                    break
                except Exception as e:
                    self.logger.error("[ReadCan] 'error: %s'", e)
                    break
        #--------------------------------------------------------------------------
        def CanMonitor(): 
            self.logger.info("[ReadCan] CanMonitor Thread started")
            while not self.__can_monitor_stop_event.is_set():
                try:
                    self.__CanMonitor()
                except Exception as e:
                    self.logger.error("CanMonitor() exception: %s", e)
                    break
                # try:
                #     self.__CanMonitor()
                #     is_exist = self.__can_inter.is_can_socket_available(self.__can_channel_name)
                #     is_up = self.__can_inter.is_can_port_up(self.__can_channel_name)
                #     if(is_exist != self.__can_inter.CAN_STATUS.CHECK_CAN_EXIST or 
                #        is_up != self.__can_inter.CAN_STATUS.CHECK_CAN_UP):
                #         print("[ERROR] CanMonitor ", is_exist, is_up)
                # except Exception as e:
                #     print(f"[ERROR] CanMonitor() 发生异常: {e}")
                #     # break
                self.__can_monitor_stop_event.wait(0.05)
        #--------------------------------------------------------------------------

        try:
            if start_thread:
                if not self.__can_deal_th or not self.__can_deal_th.is_alive():
                    self.__can_deal_th = threading.Thread(target=ReadCan, daemon=True)
                    self.__can_deal_th.start()
                if not self.__can_monitor_th or not self.__can_monitor_th.is_alive():
                    self.__can_monitor_th = threading.Thread(target=CanMonitor, daemon=True)
                    self.__can_monitor_th.start()
                self.__fps_counter.start()
            if device_init and self.__can_inter is not None:
                pass
                # self.Init()
        except Exception as e:
            self.logger.error("[ConnectPort] 'Thread start failed: %s'", e)
            self.__connected = False  # 回滚状态
            self.__read_can_stop_event.set()
            self.__can_monitor_stop_event.set()  # 确保线程不会意外运行
    
    def DisconnectPort(self, thread_timeout=0.1):
        '''
        断开端口但不阻塞主线程
        '''
        with self.__lock:
            if not self.__connected:
                return
            self.__connected = False
            self.__read_can_stop_event.set()

        if hasattr(self, 'can_deal_th') and self.__can_deal_th.is_alive():
            self.__can_deal_th.join(timeout=thread_timeout)  # 加入超时，避免无限阻塞
            if self.__can_deal_th.is_alive():
                self.logger.warning("[DisconnectPort] The [ReadCan] thread failed to exit within the timeout period")

        # if hasattr(self, 'can_monitor_th') and self.__can_monitor_th.is_alive():
        #     self.__can_monitor_th.join(timeout=thread_timeout)
        #     if self.__can_monitor_th.is_alive():
        #         self.logger.warning("The CanMonitor thread failed to exit within the timeout period")

        try:
            self.__can_inter.Close()  # 关闭 CAN 端口
            self.logger.info("[DisconnectPort] CAN port is closed")
        except Exception as e:
            self.logger.error("[DisconnectPort] 'An exception occurred while closing the CAN port: %s'", e)

    def ParseCANFrame(self, rx_message: Optional[can.Message]):
        '''can协议解析函数

        Args:
            rx_message (Optional[can.Message]): can接收的原始数据
        '''
        '''CAN protocol parsing function.

        Args:
            rx_message (Optional[can.Message]): The raw data received via CAN.
        '''
        self.__fps_counter.increment("CanMonitor")
        self.__UpdateMotorInfoFeedback(rx_message)
        self.__UpdateDriverInfoFeedback(rx_message)
        self.__UpdateRespSetZeroFeedback(rx_message)
        # self.__UpdateFirmware(msg)
    
    def Init(self):
        '''
        Description
        ----------
        初始化
        '''
        self.SetNum(7)
        self.SetTorqueCurrentLimit()
    
    # 获取反馈值------------------------------------------------------------------------------------------------------
    def GetNum(self):
        '''
        Description
        ----------
        获取电机序号, 默认为7
        '''
        return self.__num

    def GetCanBus(self):
        '''
        Description
        ----------
        获取can的总线, 可以使用其中有关can硬件的函数
        '''
        return self.__can_inter
    
    def GetCanName(self):
        '''
        Description
        ----------
        获取当前类读取的canport名称
        '''
        return self.__can_channel_name
    
    def GetCurrentApiVersion(self):
        '''
        Description
        ----------
        获取当前api版本
        '''
        return ApiVersion.API_CURRENT_VERSION
    
    def GetCurrentProtocolVersion(self):
        '''
        Description
        ----------
        获取当前协议版本
        '''
        return self.__parser.GetParserProtocolVersion()
    
    def GetCanFps(self):
        '''
        Description
        ----------
        获取can总线的总fps帧率
        '''
        return self.__fps_counter.get_fps("CanMonitor")
    
    def GetMotorInfo(self):
        '''
        Description
        ----------
        获取电机消息

        Returns
        -------
        time_stamp : float
            时间戳
        Hz : float
            消息帧率,正常为150Hz
        msg : FeedbackHighSpd
            驱动器相关信息，包括：
            
            - can_id (int): 当前电机的 CAN ID
            - motor_speed (float): 电机当前转速(rad/s)
            - current (int): 电机当前电流(mA)
            - pos (float): 电机当前位置(rad)
        )
        '''
        with self.__motor_info_mtx:
            self.__motor_info.Hz = self.__fps_counter.cal_average(self.__fps_counter.get_fps('FpsMotorInfo'))
            return self.__motor_info
    
    def GetDriverInfo(self):
        '''
        Description
        ----------
        获取驱动器消息

        Returns
        -------
        time_stamp : float
            时间戳
        Hz : float
            消息帧率，正常为 10Hz
        msg : FeedbackLowSpd
            驱动器相关信息，包括：

            - can_id (int): 当前电机的 CAN ID
            - vol (float): 母线电压 (V)
            - foc_temp (int): 驱动器温度 (°C)
            - motor_temp (int): 电机温度 (°C)
            - foc_status (dict): 电机与驱动器状态，包含：
            {
                * voltage_too_low (bool): 电源电压是否过低, True为过低
                * motor_overheating (bool): 电机是否过温, True为过温
                * driver_overcurrent (bool): 驱动器是否过流, True为过流
                * driver_overheating (bool): 驱动器是否过温, True为过温
                * collision_status (bool): 碰撞保护状态, True为触发碰撞保护
                * driver_error_status (bool): 驱动器错误状态, True为驱动器报错
                * driver_enable_status (bool): 驱动器使能状态, True为使能
                * stall_status (bool): 堵转保护状态, True为触发堵转保护
            }
            - bus_current (int): 母线电流 (mA)
        '''
        with self.__driver_info_low_spd_mtx:
            self.__driver_info_low_spd.Hz = self.__fps_counter.cal_average(self.__fps_counter.get_fps('FpsDriverInfo'))
            return self.__driver_info_low_spd
    
    def GetPos(self)->float:
        '''
        Description
        ----------
        获取电机当前位置

        Returns
        -------
        pos : float
            电机当前位置, 单位rad
        '''
        return self.__motor_info.msg.pos

    def GetVel(self)->float:
        '''
        Description
        ----------
        获取电机当前速度

        Returns
        -------
        motor_speed : float
            电机当前速度, 单位rad/s
        '''
        return self.__motor_info.msg.motor_speed

    def GetEnableStatus(self)->bool:
        '''
        Description
        ----------
        获取驱动器失能状态
        
        Returns
        -------
        driver_enable_status : bool
            驱动器使能状态, True为使能
        '''
        return self.__driver_info_low_spd.msg.foc_status.driver_enable_status
    
    def GetTemp(self)->int:
        '''
        Description
        ----------
        获取电机温度

        Returns
        -------
        motor_temp : int
            电机温度 (°C)
        '''
        return self.__driver_info_low_spd.msg.motor_temp

    def GetRespSetZero(self):
        '''
        Description
        ----------
        获取发送设置零点后的应答反馈

        Returns
        -------
        time_stamp : float
            时间戳
        msg : FeedbackRespSetZero
            零点设定相关应答信息：
            
            - zero_val (int): 作为应答数据时, 0xAC为执行成功, 0xEE为失败
            - save_flash (int): 是否写入到flash, 当作为应答反馈时, 该位无意义
        )
        '''
        with self.__resp_set_zero_mtx:
            return self.__resp_set_zero
    
    def isOk(self):
        '''
        Description
        ----------
        判断can总线上是否有数据

        Returns
        -------
        is_ok : bool
            can总线是否有数据, 如果没有数据也就是帧率为0, 反馈为False
        '''
        with self.__is_ok_mtx:
            return self.__is_ok
    # 发送控制值-------------------------------------------------------------------------------------------------------

    # 接收反馈函数------------------------------------------------------------------------------------------------------
    def __CanMonitor(self):
        '''
        can数据帧率检测
        '''
        '''
        CAN data frame rate detection
        '''
        if self.__q_can_fps.full():
            self.__q_can_fps.get()
        self.__q_can_fps.put(self.GetCanFps())
        with self.__is_ok_mtx:
            if self.__q_can_fps.full() and all(x == 0 for x in self.__q_can_fps.queue):
                    self.__is_ok = False
            else:
                self.__is_ok = True
    
    def __UpdateMotorInfoFeedback(self, can_data: Optional[can.Message]):
        '''更新驱动器信息反馈, 高速

        Args:
            msg (Message): 输入为消息汇总
        '''
        with self.__motor_info_mtx:
            if(can_data.arbitration_id == 0x510 + self.GetNum()):
                try:
                    data:bytearray = can_data.data
                    self.__fps_counter.increment("FpsMotorInfo")
                    self.__motor_info.time_stamp = can_data.timestamp
                    self.__motor_info.msg.can_id = can_data.arbitration_id
                    self.__motor_info.msg.motor_speed = round(
                        self.__parser.ConvertToNegative_16bit(self.__parser.ConvertBytesToInt(data,0,2)) / 1000, 3)
                    self.__motor_info.msg.current = self.__parser.ConvertToNegative_16bit(self.__parser.ConvertBytesToInt(data,2,4))
                    # self.__motor_info.msg.pos = self.__parser.ConvertToNegative_32bit(self.__parser.ConvertBytesToInt(data,4,8,'little'))
                    # 从 data 第4字节到第8字节，按 little-endian float32 解析
                    raw_bytes = data[4:8]
                    value = struct.unpack('<f', raw_bytes)[0]   # '<f' 表示 little-endian float32

                    self.__motor_info.msg.pos = value
                    return self.__motor_info
                except Exception as e:
                    self.logger.error("[__UpdateMotorInfoFeedback] 'UpdateError: %s'", e)
    
    def __UpdateDriverInfoFeedback(self, can_data: Optional[can.Message]):
        '''更新驱动器信息反馈, 低速

        Args:
            msg (Message): 输入为消息汇总
        '''
        with self.__driver_info_low_spd_mtx:
            if(can_data.arbitration_id == 0x520 + self.GetNum()):
                try:
                    data:bytearray = can_data.data
                    self.__fps_counter.increment("FpsDriverInfo")
                    self.__driver_info_low_spd.time_stamp = can_data.timestamp
                    self.__driver_info_low_spd.msg.can_id = can_data.arbitration_id
                    self.__driver_info_low_spd.msg.vol = round(
                        self.__parser.ConvertToNegative_16bit(self.__parser.ConvertBytesToInt(data,0,2),False) / 10, 1)
                    self.__driver_info_low_spd.msg.foc_temp = self.__parser.ConvertToNegative_16bit(self.__parser.ConvertBytesToInt(data,2,4))
                    self.__driver_info_low_spd.msg.motor_temp = self.__parser.ConvertToNegative_8bit(self.__parser.ConvertBytesToInt(data,4,5))
                    self.__driver_info_low_spd.msg.foc_status_code = self.__parser.ConvertToNegative_8bit(self.__parser.ConvertBytesToInt(data,5,6),False)
                    self.__driver_info_low_spd.msg.bus_current = self.__parser.ConvertToNegative_16bit(self.__parser.ConvertBytesToInt(data,6,8),False)
                    return self.__driver_info_low_spd
                except Exception as e:
                    self.logger.error("[__UpdateDriverInfoFeedback] 'UpdateError: %s'", e)
    
    def __UpdateRespSetZeroFeedback(self, can_data: Optional[can.Message]):
        with self.__resp_set_zero_mtx:
            if(can_data.arbitration_id == 0x020 + self.GetNum()):
                try:
                    data:bytearray = can_data.data
                    self.__resp_set_zero.time_stamp = can_data.timestamp
                    self.__resp_set_zero.msg.zero_val = self.__parser.ConvertToNegative_32bit(self.__parser.ConvertBytesToInt(data,0,4))
                    self.__resp_set_zero.msg.save_flash = self.__parser.ConvertToNegative_8bit(self.__parser.ConvertBytesToInt(data,4,5),False)
                    return self.__resp_set_zero
                except Exception as e:
                    self.logger.error("[__UpdateRespSetZeroFeedback] 'UpdateError: %s'", e)

    def __UpdateFirmware(self, msg:Message):
        with self.__firmware_data_mtx:
            if(msg.type_ == MsgType.FirmwareRead):
                self.__firmware_data = self.__firmware_data + msg.firmware_data
            return self.__firmware_data
    
    # 控制发送函数------------------------------------------------------------------------------------------------------
    def SetNum(self, num:int=7):
        '''
        Description
        ----------
        设置内部数字值，并返回设置后的值。

        Parameters
        ----------
        num : int, optional
            要设置的数字，默认值为 7。

        Returns
        -------
        int
            设置后的数字值。
        '''
        self.__num = num
        return self.__num

    def ClearRespSetZero(self):
        '''
        Description
        ----------
        清除设定零点的反馈消息缓存
        '''
        self.__resp_set_zero.time_stamp = 0
        self.__resp_set_zero.msg.zero_val = 0
        self.__resp_set_zero.msg.save_flash = 0

    def Enable(self):
        '''
        Description
        ----------
        使能电机
        '''
        tx_can = Message()
        tx_can.arbitration_id = 0x420 + self.GetNum()
        tx_can.data = [0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        feedback = self.__can_inter.SendCanMessage(tx_can.arbitration_id, tx_can.data)
        if feedback is not self.__can_inter.CAN_STATUS.SEND_MESSAGE_SUCCESS:
            self.logger.error("Enable send failed: SendCanMessage(%s)", feedback)
    
    def Disable(self):
        '''
        Description
        ----------
        失能电机
        '''
        tx_can = Message()
        tx_can.arbitration_id = 0x420 + self.GetNum()
        tx_can.data = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        feedback = self.__can_inter.SendCanMessage(tx_can.arbitration_id, tx_can.data)
        if feedback is not self.__can_inter.CAN_STATUS.SEND_MESSAGE_SUCCESS:
            self.logger.error("Disable send failed: SendCanMessage(%s)", feedback)
    
    def SetTorqueCurrentLimit(self, current_limit: float):
        '''
        Description
        ----------
        设置内部数字值，并返回设置后的值。

        Parameters
        ----------
        current_limit : float, optional
            力矩电流限制设定, 单位为A
        '''
        tx_can = Message()
        tx_can.arbitration_id = 0x450 + self.GetNum()
        # 打包成 float32 小端字节
        raw_bytes = struct.pack('<f', current_limit)
        # 转成 list
        byte_list = list(raw_bytes)
        if len(byte_list) == 4:
            tx_can.data = byte_list + [0x00] * 4
        else: # 1.5A
            tx_can.data = [0, 0, 192, 63] + [0x00] * 4
        feedback = self.__can_inter.SendCanMessage(tx_can.arbitration_id, tx_can.data)
        if feedback is not self.__can_inter.CAN_STATUS.SEND_MESSAGE_SUCCESS:
            self.logger.error("SetTorqueCurrentLimit send failed: SendCanMessage(%s)", feedback)
    
    def SetZero(self):
        '''
        Description
        ----------
        设定当前位置为零点

        Attention
        ------
        只有在电机为失能状态下才能够执行
        '''
        tx_can = Message()
        tx_can.arbitration_id = 0x020 + self.GetNum()
        tx_can.data = [0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00]
        feedback = self.__can_inter.SendCanMessage(tx_can.arbitration_id, tx_can.data)
        if feedback is not self.__can_inter.CAN_STATUS.SEND_MESSAGE_SUCCESS:
            self.logger.error("SetZero send failed: SendCanMessage(%s)", feedback)

    def GripperCtrl(self, pos:float):
        self.MitCtrl(pos,0,10,0.8,0)
    def MitCtrl(self,
                pos_ref:float, vel_ref:float, kp:float, kd:float, t_ref:float,
                p_min:float=-12.5,      p_max:float=12.5, 
                v_min:float=-45.0,      v_max:float=45.0, 
                kp_min:float=0.0,       kp_max:float=500.0, 
                kd_min:float=-5.0,      kd_max:float=5.0,
                t_min:float=-8.0,       t_max:float=8.0):
        '''
        Description
        ----------
        MIT控制指令
        
        CAN ID:
            0x41x
        
        注意:p_min,p_max,v_min,v_max,kp_min,kp_max,kd_min,kd_max,t_min,t_max参数为固定,不要更改
        
        Parameters
        ----------
        pos_ref : float
            设定期望的目标位置, 单位为rad
        vel_ref : float
            设定电机运动的速度, 单位为rad/s
        kp : float
            比例增益,控制位置误差对输出力矩的影响
        kd : float
            微分增益,控制速度误差对输出力矩的影响
        t_ref : float
            目标力矩参考值,用于控制电机施加的力矩或扭矩, 单位为 N.m
        '''
        pos_tmp = self.__parser.FloatToUint(pos_ref, p_min, p_max, 16)
        vel_tmp = self.__parser.FloatToUint(vel_ref, v_min, v_max, 12)
        kp_tmp = self.__parser.FloatToUint(kp, kp_min, kp_max, 12)
        kd_tmp = self.__parser.FloatToUint(kd, kd_min, kd_max, 12)
        t_tmp = self.__parser.FloatToUint(t_ref, t_min, t_max, 8)
        tx_can = Message()
        mit_ctrl = MitCtrl(  pos_ref=pos_tmp, 
                                    vel_ref=vel_tmp,
                                    kp=kp_tmp, 
                                    kd=kd_tmp,
                                    t_ref=t_tmp)
        msg = Message(type_=MsgType.MitCtrlIndex, mit_ctrl=mit_ctrl)
        self.__parser.EncodeMessage(msg, tx_can)
        feedback = self.__can_inter.SendCanMessage(tx_can.arbitration_id + self.GetNum(), tx_can.data)
        if feedback is not self.__can_inter.CAN_STATUS.SEND_MESSAGE_SUCCESS:
            self.logger.error("MitCtrl send failed: SendCanMessage(%s)", feedback)

