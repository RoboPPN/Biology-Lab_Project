## can 模块使能

```bash
cd  agx_driver_api/gripper_sdk

bash can_activate.sh can0 1000000
```

## API 说明

模块导入：

```python
from gripper_sdk import *  # 导入gripper_sdk中的所有功能
```

创建驱动API的控制器实例：

```python
controller = DriverApi()
```

连接到设备端口：

```python
controller.ConnectPort()
```

检测设备状态是否正常：

```python
if controller.isOk():
    print("Device is connected")
else:
    print("Device connection failed")
```

电机使能：

```python
controller.Enable()
```

电机失能：

```python
controller.Disable()
```

循环检测设备状态是否正常：

```python
while controller.isOk():
    if controller.GetEnableStatus():
        print("Enable successfully")
        break
```


控制电机张开 1.5 rad：

```python
controller.GripperCtrl(1.5)
```

零点设置：

```python
controller.SetZero()
```

获取夹爪当前开合弧度：

```python
rad = controller.GetPos()
```


获取电机当前转速（rad/s）:

```python
vel = controller.GetVel()
```


获取电机温度（°C）：

```python
temp = controller.GetTemp()
```


