from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
from pylibrm.constant import const
import struct
import time
import math
from pymodbus.exceptions import ModbusIOException
import struct


def __version__():
    return "0.0.8"    

class Axis_V6(object):
    _modbus_clients = {}  # 字典保存不同端口对应的 ModbusClient 对象

    def __init__(self, client: ModbusClient, slave_id: int,timeout =100):
        self._slave_id = slave_id
        self._client = client
        self._io_gap_time = 50  # ms
        self._retries = 20
        
        self._is_debug = False
        pass

    def _print(self, v):
        if self._is_debug:
            print(v)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
    def wait(self, time_in_ms):
        time.sleep(time_in_ms / 1000.0)

    def wait_for_reached(self, timeout):
        timeout = timeout/1000.
        start_time = time.time()
        while True:
            last_time = time.time() - start_time
            if last_time > timeout:
                break
            is_reached = self.is_reached()
            if is_reached:
                break
        pass

    def retry(self, func):
        def wrapper(*args, **kwargs):
            count = 0
            while count <= self._retries:
                r = func(*args, **kwargs)
                if not r.isError():
                    break
                else:
                    self._print(r)
                count += 1
                self._print(f"axis{self._slave_id} retry {func}{args}")
            if count > self._retries:
                raise ModbusIOException("Modbus communication retry limit exceeded")
            return r

        return wrapper
    
    @staticmethod
    def get_modbus_client(port, baudrate=115200):
        if port not in Axis_V6._modbus_clients:
            Axis_V6._modbus_clients[port] = ModbusClient(
                method="rtu",
                port=port,
                stopbits=1,
                timeout=0.1,
                bytesize=8,
                parity='N',
                baudrate=baudrate,
                retries=30,
                strict=False
            )
        return Axis_V6._modbus_clients[port]

    @staticmethod
    def create_modbus_rtu(port, baudrate ,slave_id):
        client = Axis_V6.get_modbus_client(port, baudrate)
        connection = client.connect()
        return Axis_V6(client, slave_id)

    @staticmethod
    def create_modbus_tcp(host, port, slave_id):
        client = ModbusTcpClient(host, port,retries=30, timeout=0.1)
        client.connect()
        return Axis_V6(client, slave_id)
    

    def set_retries(self,max_retry):
        self._client.retries = max_retry
    
    def set_timeout(self,timeout_ms):
        self._client.timeout = timeout_ms/1000
        
    def read_int32(self, address, func):
        r = self.retry(func)(address, 2, unit=self._slave_id)
        return BinaryPayloadDecoder.fromRegisters(r.registers, wordorder=Endian.Little, byteorder=Endian.Big)

    def read_float(self, address, func):
        r = self.retry(func)(address, 2, unit=self._slave_id)
        decoder = BinaryPayloadDecoder.fromRegisters(r.registers, wordorder=Endian.Little, byteorder=Endian.Big)
        return decoder.decode_32bit_float()
    
    def read_input_registers_float_with_quantity(self, address, quantity, func):
        try:
            float_values = []
       
            r = self.retry(func)(address, quantity, unit=self._slave_id)
            for i in range(0, len(r.registers), 2):
                registers_slice = r.registers[i:i+2]
                decoder = BinaryPayloadDecoder.fromRegisters(registers_slice, wordorder=Endian.Little, byteorder=Endian.Big)
                decoded_value = decoder.decode_32bit_float()
                float_values.append(decoded_value)
            return float_values
        except ModbusIOException as e:
            print(f"Modbus communication error: {e}")
        
    def read_input_registers_float_array(self, address, quantity):
        return self.read_input_registers_float_with_quantity(address, quantity,self._client.read_input_registers)
    
    def read_input_int32(self, address):
        return self.read_int32(address, self._client.read_input_registers).decode_32bit_int()

    def read_input_float(self, address):
        return self.read_float(address, self._client.read_input_registers)

    def read_holding_int32(self, address):
        return self.read_int32(address, self._client.read_holding_registers).decode_32bit_int()

    def read_holding_float(self, address):
        return self.read_float(address, self._client.read_holding_registers)

    def read_float_with_quantity(self, address,quantity, func):
        try:
            float_values = []
            r = self.retry(func)(address, quantity, unit=self._slave_id)
            for i in range(0, len(r.registers), 2):
                registers_slice = r.registers[i:i+2]
                decoder = BinaryPayloadDecoder.fromRegisters(registers_slice, wordorder=Endian.Little, byteorder=Endian.Big)
                decoded_value = decoder.decode_32bit_float()
                float_values.append(decoded_value)
            return float_values
        except ModbusIOException as e:
            print(f"Modbus communication error: {e}")

    def read_holding_float_with_quantity(self, address,quantity):
        return self.read_float_with_quantity(address, quantity,self._client.read_holding_registers)


    def write_regs(self, address, data):
        @self.retry
        def write_with_retry(address, data):
            return self._client.write_registers(address, data, skip_encode=True, unit=self._slave_id)
        return write_with_retry(address, data)
       

    def write_int32(self, address, value):
        builder = BinaryPayloadBuilder(wordorder=Endian.Little, byteorder=Endian.Big)
        builder.add_32bit_int(int(value))
        return self.write_regs(address, builder.build())

    def write_float(self, address, value):
        
        builder = BinaryPayloadBuilder(wordorder=Endian.Little, byteorder=Endian.Big)
        
        builder.add_32bit_float(float(value))
        return self.write_regs(address, builder.build())
    
    def write_holding_float(self, address, value):
        self.write_float(address, value)

    def write_holding_int32(self, address, value):
        self.write_int32(address, value)

    def write_coil(self, address, value,func):
        self._client.write_coil(address, value, unit=self._slave_id)
        #r = self.retry(func)(address, value, unit=self._slave_id)

    def trig_coil(self, address):
        self.write_coil(address, False,self._client.write_coil)
        self.wait(self._io_gap_time)
        self.write_coil(address, True,self._client.write_coil)

    def read_coil(self, address):
        r = self._client.read_coils(address, unit=self._slave_id)
        return r.bits[0]
    
    def read_discrete_inputs(self, address):
        r = self._client.read_discrete_inputs(address,1, unit=self._slave_id)
        return r.bits[0]
    
    def read_discrete_inputs_with_retry(self, address, max_retries=1):
        for _ in range(max_retries):
            try:
                r = self._client.read_discrete_inputs(address, 1, unit=self._slave_id)
                if hasattr(r, 'bits'):
                    return r.bits[0] if r.bits else False
                else:
                    return False
            except ModbusIOException as e:
                print(f"Modbus IO exception: {e}")
        return False

    def get_version(self):
        version = dict()
        version["major"] = self.read_input_int32(8)
        version["minor"] = self.read_input_int32(10)
        version["build"] = self.read_input_int32(12)
        version["type"] = self.read_input_int32(14)
        return version

    def config_motion(self, velocity, acceleration):
        self.write_holding_float(const.DIRECT_MOTION_VELOCITY, velocity)
        self.write_holding_float(const.DIRECT_MOTION_ACCELERATION, acceleration)

    def read_config_motion(self):
        return [self.read_holding_float(const.DIRECT_MOTION_VELOCITY), self.read_holding_float(const.DIRECT_MOTION_ACCELERATION)]

    def move_to(self, position):
        self.write_holding_float(const.DIRECT_MOTION_POSITION, position)

    def set_command(self, index, command):
        builder = BinaryPayloadBuilder(wordorder=Endian.Little, byteorder=Endian.Big)
        builder.add_32bit_int(int(command["type"]))
        builder.add_32bit_int(int(command["next_command_index"]))
        
        if command["type"] ==  const.COMMAND_GO_HOME:
            builder.add_32bit_float(float(command["origin_offset"]))
        elif command["type"] ==  const.COMMAND_DELAY:
            builder.add_32bit_int(int(command["ms"]))
        elif command["type"] ==  const.COMMAND_MOVE_ABSOLUTE:
            builder.add_32bit_float(float(command["position"]))
            builder.add_32bit_float(float(command["velocity"]))
            builder.add_32bit_float(float(command["acceleration"]))
            builder.add_32bit_float(float(command["deceleration"]))
            builder.add_32bit_float(float(command["band"]))
        elif command["type"] ==  const.COMMAND_MOVE_RELATIVE:
            builder.add_32bit_float(float(command["distance"]))
            builder.add_32bit_float(float(command["velocity"]))
            builder.add_32bit_float(float(command["acceleration"]))
            builder.add_32bit_float(float(command["deceleration"]))
            builder.add_32bit_float(float(command["band"]))
        elif command["type"] == const.COMMAND_PUSH:
            builder.add_32bit_float(float(command["distance"]))
            builder.add_32bit_float(float(command["velocity"]))
            builder.add_32bit_float(float(command["acceleration"]))
            builder.add_32bit_float(float(command["force_limit"]))
            builder.add_32bit_float(float(command["pos_band_mm"]))
            builder.add_32bit_float(float(command["time_band_ms"]))
        elif command["type"] ==  const.COMMAND_PRECISE_PUSH:
            builder.add_32bit_float(float(command["distance"]))
            builder.add_32bit_float(float(command["force"]))
            builder.add_32bit_float(float(command["velocity_factor"]))
            builder.add_32bit_float(float(command["impact_factor"]))
            builder.add_32bit_float(float(command["band_n"]))
            builder.add_32bit_float(float(command["band_ms"]))
        elif command["type"] ==  const.COMMAND_GO_HOME_Z:
            builder.add_32bit_float(float(command["distance"]))
            builder.add_32bit_float(float(command["velocity"]))
            builder.add_32bit_float(float(command["acceleration"]))
            builder.add_32bit_float(float(command["force_limit"]))
            builder.add_32bit_float(float(command["band_mm"]))
        elif command["type"] ==  const.COMMAND_PRECISE_TOUCH:
            builder.add_32bit_float(float(command["distance"]))
            builder.add_32bit_float(float(command["velocity"]))
            builder.add_32bit_float(float(command["acceleration"]))
            builder.add_32bit_float(float(command["force_threshold"]))
            builder.add_32bit_float(float(command["band_mm"]))
        elif command["type"] == const.COMMAND_START_MONITOR:
            builder.add_32bit_int(int(command["freq_hz"]))
            builder.add_32bit_int(int(command["length"]))
            builder.add_32bit_int(int(command["count"]))
            builder.add_32bit_int(int(command["var_0"]))
            builder.add_32bit_int(int(command["var_1"]))
            builder.add_32bit_int(int(command["var_2"]))
        return self.write_regs(5000 + index * 16, builder.build())

    def get_command(self,index):
        command_table_address = 5000
        command_entry_size = 32 / 2
        
        command_table_address = int(command_table_address)
        command_entry_size = int(command_entry_size)
        
        command_type = self.read_holding_int32(command_table_address + command_entry_size * index)
        
        next_command_index = self.read_holding_int32(command_table_address + command_entry_size * index  + 2)
        if command_type == const.COMMAND_NONE:
            return {"type": command_type,"next_command_index": next_command_index}
        if command_type == const.COMMAND_GO_HOME:
            origin_offset = self.read_holding_float(command_table_address + command_entry_size * index + 4)
            return {"type": command_type,"next_command_index": next_command_index, "origin_offset": origin_offset}
        elif command_type == const.COMMAND_DELAY:
            ms = self.read_holding_int32(command_table_address + command_entry_size * index + 4)
            return {"type": command_type,"next_command_index": next_command_index, "ms": ms}
        elif command_type == const.COMMAND_MOVE_ABSOLUTE:
            position = self.read_holding_float(command_table_address + command_entry_size * index + 4)
            velocity = self.read_holding_float(command_table_address + command_entry_size * index + 6)
            acceleration = self.read_holding_float(command_table_address + command_entry_size * index + 8)
            deceleration = self.read_holding_float(command_table_address + command_entry_size * index + 10)
            band = self.read_holding_float(command_table_address + command_entry_size * index + 12)
            return {"type": command_type,"next_command_index": next_command_index,"position": position, "velocity": velocity,
                    "acceleration": acceleration, "deceleration": deceleration, "band": band}
        elif command_type ==  const.COMMAND_PUSH:
            distance = self.read_holding_float(command_table_address + command_entry_size * index + 4)
            force_limit = self.read_holding_float(command_table_address + command_entry_size * index + 10)
            velocity = self.read_holding_float(command_table_address + command_entry_size * index + 6)
            acceleration = self.read_holding_float(command_table_address + command_entry_size * index + 8)
            pos_band_mm = self.read_holding_float(command_table_address + command_entry_size * index + 12)
            time_band_ms= self.read_holding_float(command_table_address + command_entry_size * index + 14)
            return {"type": command_type,"next_command_index": next_command_index,"distance": distance,  "force_limit": force_limit,"velocity": velocity, "acceleration": acceleration,
                    "pos_band_mm": pos_band_mm, "time_band_ms": time_band_ms}
        
        elif command_type ==  const.COMMAND_MOVE_RELATIVE:
            distance = self.read_holding_float(command_table_address + command_entry_size * index + 4)
            velocity = self.read_holding_float(command_table_address + command_entry_size * index + 6)
            acceleration = self.read_holding_float(command_table_address + command_entry_size * index + 8)
            deceleration = self.read_holding_float(command_table_address + command_entry_size * index + 10)
            band = self.read_holding_float(command_table_address + command_entry_size * index + 12)
            return {"type": command_type,"next_command_index": next_command_index,"distance": distance, "velocity": velocity,
                    "acceleration": acceleration, "deceleration": deceleration, "band": band}
        elif command_type ==  const.COMMAND_PRECISE_PUSH:
            distance = self.read_holding_float(command_table_address + command_entry_size * index + 4)
            force = self.read_holding_float(command_table_address + command_entry_size * index + 6)
            velocity_factor = self.read_holding_float(command_table_address + command_entry_size * index + 8)
            impact_factor = self.read_holding_float(command_table_address + command_entry_size * index + 10)
            band_n = self.read_holding_float(command_table_address + command_entry_size * index + 12)
            band_ms = self.read_holding_float(command_table_address + command_entry_size * index + 14)
            return {"type": command_type,"next_command_index": next_command_index,"distance": distance, "force": force,
                    "velocity_factor": velocity_factor, "impact_factor": impact_factor, "band_n": band_n, "band_ms": band_ms}
        elif command_type ==  const.COMMAND_RESET_FORCE:
            return {"type": command_type,"next_command_index": next_command_index}
        elif command_type ==  const.COMMAND_STOP:
            return {"type": command_type,"next_command_index": next_command_index}
        elif command_type ==  const.COMMAND_START_MONITOR:
            freq_hz = self.read_holding_int32(command_table_address + command_entry_size * index + 4)
            length = self.read_holding_int32(command_table_address + command_entry_size * index + 6)
            count = self.read_holding_int32(command_table_address + command_entry_size * index + 8)
            var_0 = self.read_holding_int32(command_table_address + command_entry_size * index + 10)
            var_1 = self.read_holding_int32(command_table_address + command_entry_size * index + 12)
            var_2 = self.read_holding_int32(command_table_address + command_entry_size * index + 14)
            return {"type": command_type,"next_command_index": next_command_index,"freq_hz": freq_hz, "length": length,
                    "count": count, "var_0": var_0, "var_1": var_1, "var_2": var_2}
        elif command_type ==  const.COMMAND_GO_HOME_Z:
            distance = self.read_holding_float(command_table_address + command_entry_size * index + 4)
            velocity = self.read_holding_float(command_table_address + command_entry_size * index + 6)
            acceleration = self.read_holding_float(command_table_address + command_entry_size * index + 8)
            force_limit = self.read_holding_float(command_table_address + command_entry_size * index + 10)
            band_mm = self.read_holding_float(command_table_address + command_entry_size * index + 12)
            return {"type": command_type,"next_command_index": next_command_index,"distance": distance, "velocity": velocity,
                    "acceleration": acceleration, "force_limit": force_limit, "band_mm": band_mm}
        elif command_type ==  const.COMMAND_PRECISE_TOUCH:
            distance = self.read_holding_float(command_table_address + command_entry_size * index + 4)
            velocity = self.read_holding_float(command_table_address + command_entry_size * index + 6)
            acceleration = self.read_holding_float(command_table_address + command_entry_size * index + 8)
            force_threshold = self.read_holding_float(command_table_address + command_entry_size * index + 10)
            band_mm = self.read_holding_float(command_table_address + command_entry_size * index + 12)
            return {"type": command_type,"next_command_index": next_command_index,"distance": distance, "velocity": velocity,
                    "acceleration": acceleration, "force_threshold": force_threshold, "band_mm": band_mm}
    
    def trig_command(self, index):
        self.write_holding_int32(const.CMD_MANAGER_PENDING_COMMAND_INDEX, index)
        self.wait(self._io_gap_time)
        self.trig_coil(const.VIRTUAL_IO_COMMAND_START)
        self.wait(self._io_gap_time)

    def save_command(self):
        self.trig_coil(const.VIRTUAL_IO_SAVE_COMMANDS)

    def save_parameters(self):
        self.trig_coil(const.VIRTUAL_IO_SAVE_PARAMETERS)

    def exec_command(self, command):
        if command["type"] == const.COMMAND_START_MONITOR:
            self.set_command(40, command)
            self.wait(self._io_gap_time)
            #self.save_command()
            self.wait(self._io_gap_time)
            self.trig_command(40)
            self.wait(self._io_gap_time)
        elif command["type"] == const.COMMAND_MOVE_RELATIVE:
            #保存当前位置到寄存器内
            now_pos = self.position()
            self.wait(self._io_gap_time)
            self.write_holding_float(const.F9, now_pos)
            self.wait(self._io_gap_time)
            self.save_parameters()
            self.wait(self._io_gap_time)
            self.set_command(32, command)
            self.wait(self._io_gap_time)
            #self.save_command()
            self.wait(self._io_gap_time)
            self.trig_command(32)
            self.wait(self._io_gap_time)
        else:
            self.set_command(32, command)
            self.wait(self._io_gap_time)
            self.trig_command(32)
            self.wait(self._io_gap_time)
        
        
        

    #freq_hz 采集频率
	# length 采集频道数 （最大值为3，对应下发三个参数是否生效）
	# count 采集数量
	# var_0
	# var_1
	# var_2
	# 以上三个参数可以填入一下index：
	# 0 当前位置
	# 1 当前速度
	# 2 当前出力
	# 3 目标位置
	# 4 当前受力
    def start_monitor(self, next,freq_hz, length, count, var_0, var_1, var_2):
        command = dict()
        command["type"] = const.COMMAND_START_MONITOR
        command["next_command_index"] = next
        command["freq_hz"] = freq_hz
        command["length"] = length
        command["count"] = count
        command["var_0"] = var_0
        command["var_1"] = var_1
        command["var_2"] = var_2
        self.exec_command(command)

    def sample_result(self):
        sample_size = 0
        while not self.read_discrete_inputs_with_retry(const.VIRTUAL_IO_MONITOR_FULL):
            pass
        sample_size = self.read_input_int32(24575)
        block_size = 200
        block_count = sample_size / block_size
        block_count =int(block_count)
        remainder_size = sample_size - block_count * block_size
        sample_result =[]
        for i in range(block_count):
            result = self.read_input_registers_float_array(0x6000 + i, block_size // 2)
            result = result if result is not None else []
            sample_result[i * block_size: (i + 1) * block_size] = result
        # 处理剩余的数据
        if remainder_size > 0:
            result = self.read_input_registers_float_array(0x6000 + block_count * block_size, math.ceil(remainder_size / 2))
            result = result if result is not None else []
            sample_result[block_count * block_size:] = result
        return sample_result
    
    def precise_push(self, distance, force, velocity_factor, impact_factor, band_n, band_ms):
        command = dict()
        command["type"] = const.COMMAND_PRECISE_PUSH
        command["next_command_index"] = 15
        command["distance"] = distance
        command["force"] = force
        command["velocity_factor"] = velocity_factor
        command["impact_factor"] = impact_factor
        command["band_n"] = band_n
        command["band_ms"] = band_ms
        self.exec_command(command)

    def move_absolute(self, position, velocity, acceleration, deceleration, band):
        command = dict()
        command["type"] = const.COMMAND_MOVE_ABSOLUTE
        command["next_command_index"] = 15
        command["position"] = position
        command["velocity"] = velocity
        command["acceleration"] = acceleration
        command["deceleration"] = deceleration
        command["band"] = band
        self.exec_command(command)
        
    def push(self, distance, velocity, acceleration, force_limit, pos_band_mm,time_band_ms):
        command = dict()
        command["type"] = const.COMMAND_PUSH
        command["next_command_index"] = 15
        command["distance"] = distance
        command["velocity"] = velocity
        command["acceleration"] = acceleration
        command["force_limit"] = force_limit
        command["pos_band_mm"] = pos_band_mm
        command["time_band_ms"] = time_band_ms
        self.exec_command(command)
    
    def precise_push(self, distance, force, velocity_factor, impact_factor, band_n, band_ms):
        command = dict()
        command["type"] = const.COMMAND_PRECISE_PUSH
        command["next_command_index"] = 15
        command["distance"] = distance
        command["force"] = force
        command["velocity_factor"] = velocity_factor
        command["impact_factor"] = impact_factor
        command["band_n"] = band_n
        command["band_ms"] = band_ms
        self.exec_command(command)
    
    def go_home_z(self, distance, velocity, acceleration, force_limit, band_mm):
        command = dict()
        command["type"] = const.COMMAND_GO_HOME_Z
        command["next_command_index"] = 15
        command["distance"] = distance
        command["velocity"] = velocity
        command["acceleration"] = acceleration
        command["force_limit"] = force_limit
        command["band_mm"] = band_mm
        self.exec_command(command)

    def precise_touch(self, distance, velocity, acceleration, force_threshold, band_mm):
        command = dict()
        command["type"] = const.COMMAND_PRECISE_TOUCH
        command["next_command_index"] = 15
        command["distance"] = distance
        command["velocity"] = velocity
        command["acceleration"] = acceleration
        command["force_threshold"] = force_threshold
        command["band_mm"] = band_mm
        self.exec_command(command)

    def go_home(self):
        command = dict()
        command["type"] = const.COMMAND_NONE
        command["next_command_index"] = -1
        self.set_command(15, command)
        self.wait(self._io_gap_time)
        self.save_command()
        
        self.wait(self._io_gap_time)
        self.trig_coil(const.VIRTUAL_IO_GO_HOME)

    def is_finished(self,index):
        if self.read_discrete_inputs_with_retry(1000+index):
            return True
        else:
            return False

    def is_moving(self):#只能用于判断指令15是否完成,且速度达标 判断是否在moving
        if self.read_discrete_inputs(const.VIRTUAL_IO_COMMAND_FINISHED_15):
            return False
        input_float_2 = self.read_input_float(const.STATE_OBSERVER_VELOCITY)
        if  input_float_2 > 2 or input_float_2 < -2:
            return True
        else:
            return False

    
    def is_captured(self):#判断夹持（推压运动）
        if self.read_discrete_inputs(const.VIRTUAL_IO_COMMAND_FINISHED_15):
            return False
        if self.read_discrete_inputs_with_retry(const.VIRTUAL_IO_IN_POSITION):#位置到位，说明没夹持到
            return False
        else:
            return True

    def is_go_home_down(self):
        self.wait(self._io_gap_time)
        if self.read_input_int32(const.CMD_MANAGER_CURRENT_COMMAND_INDEX) == -1:
            return True
        else:
            return False

    def is_reached(self):#只能判断 绝对运动，精密推压,相對運動
        command = self.get_command(32)
        if self.read_discrete_inputs(const.VIRTUAL_IO_COMMAND_FINISHED_15):
            if command["type"] == const.COMMAND_MOVE_RELATIVE:#判断是否和设置位置匹配
                now_pos = self.position()
                self.wait(self._io_gap_time)
                read_pos = self.read_holding_float(const.F9)
                temp = command["distance"]-abs(now_pos - read_pos)
                if (temp<= command["band"]):
                    return True
                else:
                    return False
            if command["type"] == const.COMMAND_MOVE_ABSOLUTE:#判断是否和设置位置匹配
                temp = self.position() - command["position"]
                if temp < 0:
                    temp = -temp
                if (temp <= command["band"]):
                    return True
                else:
                    return False
            if command["type"] == const.COMMAND_PRECISE_PUSH:#判断力是否达到指定大小
                temp =self.position() - command["distance"]
                if temp < 0:
                    temp = -temp
                if (temp > 0):#没有到达指定的位置就停下了 
                    self.wait(self._io_gap_time)
                    return True
                else:#到达 
                    temp = self.force_sensor() - command["force"]
                    if temp < 0:                    
                        temp = -temp
                    if temp <= command["band_n"]:#夹到
                        return True
                    else:
                        return False
                
    def get_command_status(self):
        #状态0 pending, 1完成   2停止   3位置到达   4力到达
        return self.read_input_float(const.CMD_MANAGER_CURRENT_COMMAND_STATUS)

    def is_push_empty(self):
        if self.read_input_float(const.CMD_MANAGER_CURRENT_COMMAND_STATUS) == 3:
            return True #空推
        else:
            return False
        
    def load_commands(self):
        self.trig_coil(const.VIRTUAL_IO_LOAD_COMMAN)

    def error_code(self):
        errors = []
        if self.read_discrete_inputs(const.ERR_MANAGER_ENABLE_POSITION_DEVIATION_OVERFLOW):
            errors.append("Position_deviation_overflow")
        if self.read_discrete_inputs(const.ERR_MANAGER_ENABLE_VELOCITY_DEVIATION_OVERFL):
            errors.append("Velocity_deviation_overflow")
        if self.read_discrete_inputs(const.VIRTUAL_IO_MOTOR_STUCK):
            errors.append("Motor_stuck")
        if self.read_discrete_inputs(const.VIRTUAL_IO_FORCE_OVERLOAD):
            errors.append("Force_overload")
        return errors
    
    def reset_error(self):
        self.trig_coil(const.VIRTUAL_IO_RESET_ERROR)

    def reset_force(self):
        self.trig_coil(const.VIRTUAL_IO_RESET_FORC)

    def set_servo_on_off(self, on_off):
        self.write_coil(const.VIRTUAL_IO_SERVO_ON_OFF, on_off,self._client.write_coil)

    def stop(self):
        self.trig_coil(const.VIRTUAL_IO_COMMAND_STOP)

    def position(self):
        return self.read_input_float(const.STATE_OBSERVER_POSITION)

    def velocity(self):
        return self.read_input_float(const.STATE_OBSERVER_VELOCITY)

    def torque(self):
        return self.read_input_float(const.STATE_OBSERVER_TORQUE)

    def force_sensor(self):
        return self.read_input_float(const.FORCE_SENSOR_READING)

    def pending_index(self):
        return self.read_holding_float(const.CMD_MANAGER_PENDING_COMMAND_INDEX)

    def enable_error_position_deviation_overflow(self,on_off):
        self.write_coil(const.VIRTUAL_IO_POSITION_DEVIATION_OVERFLO,on_off,self._client.write_coil)
    
    def enable_error_velocity_deviation_overflow(self,on_off):
        self.write_coil(const.VIRTUAL_IO_VELOCITY_DEVIATION_OVERFLO,on_off,self._client.write_coil)
       
    def enable_motor_stuck(self,on_off):
        self.write_coil(const.VIRTUAL_IO_MOTOR_STUCK,on_off,self._client.write_coil)
       
    
    def is_ready(self):
        servo_on_off = self.read_coil(const.VIRTUAL_IO_SERVO_ON_OFF)
        ret = self.error_code()
        if (servo_on_off and ret == 0):
            return True
        else:
            return False
        
    # 精密推压 传入点位序号 和 力的大小
    def set_command_force(self, index, force):
        if (index < 0 or index>15):
            return False
        pre_command = self.get_command(index)
        if(pre_command["type"] != const.COMMAND_PRECISE_PUSH):
            return False
        pre_command["force"] =force
        self.set_command(index,pre_command)
        self.wait(self._io_gap_time)
        self.save_command()
        return True

    def set_command_pos(self, index, pos):
        if (index < 0 or index>15):
            return False
        pre_command = self.get_command(index)
        if(pre_command["type"] != const.COMMAND_MOVE_ABSOLUTE):
            return False
        pre_command["position"] = pos
        self.set_command(index,pre_command)
        self.wait(self._io_gap_time)
        self.save_command()
        return True


    def close(self):
        self._client.close()

    #读取外部力传感器 单独连接后使用
    def read_external_force(self):
        reg = self._client.read_holding_registers(80, count=2,unit=self._slave_id)
        if not reg.isError():
            reg_values = reg.registers
            force_bytes = struct.pack('>HH', reg_values[0], reg_values[1])
            force = struct.unpack('>i', force_bytes)[0] / 100.0

            return force
        return 0
    

    def set_b0_state(self,on_off):
        self.write_holding_int32(const.B0, ~on_off)
        self.wait(self._io_gap_time)
        self.write_holding_int32(const.B0, on_off)
    
    def set_b1_state(self,on_off):
        self.write_holding_int32(const.B1, ~on_off)
        self.wait(self._io_gap_time)
        self.write_holding_int32(const.B1, on_off)

    def set_b3_state(self,on_off):
        self.write_holding_int32(const.B3, ~on_off)
        self.wait(self._io_gap_time)
        self.write_holding_int32(const.B3, on_off)

    def set_f1(self,pos):
        self.write_holding_float(const.F1, pos)

    def set_f2(self,pos):
        self.write_holding_float(const.F2, pos)

    def set_f3(self,force_limit):
        self.write_holding_float(const.F3, force_limit)

    #对应原来的d0
    def set_f4(self,coefficient):
        self.write_holding_float(const.F4, coefficient)
    #对应原来的d1
    def set_f5(self,coefficient):
        self.write_holding_float(const.F5, coefficient)
    #对应原来的d2    
    def set_f6(self,coefficient):
        self.write_holding_float(const.F6, coefficient)

