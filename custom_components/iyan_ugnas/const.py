"""Constants for the iYan-UGNas integration."""

DOMAIN = "iyan_ugnas"

# CONF KEY
CONF_HOST = "host"
CONF_PORT = "port"
CONF_USERNAME = "username"
CONF_PASSWD = "passwd"
CONF_PASSMD5 = "passwd"
CONF_PORT = "port"

CONF_TOKEN_EXPIRE_TIME = "token_expire_time"
COORDINATOR = "coordinator"
CONF_UPDATE_INTERVAL = "update_interval_seconds"

UNDO_UPDATE_LISTENER = "undo_update_listener"

# UGreen Url
LOGIN_URL = "/v1/user/offline/login"
SYS_INFO = "/setting/v1/sys/info"
CPU_INFO = "/v1/system/details/cpu/status"
DISK_INFO = "/v2/storage/disk/list"
STORAGES_INFO = "/v2/storage/list"
STATUS_INFO = "/v1/system/details/status"
STATUS_HARDDISK_INFO = "/v1/system/details/harddisk/status"
STATUS_HARDDISK_TEMP_INFO = "/v1/system/details/harddisk_temp/status"
STATUS_CPU_INFO = "/v1/system/details/cpu/status"
STATUS_NETWORK_INFO = "/v1/system/details/network/status"

UPDATE_WEB = "/v1/upgrade/webui/info"
UPDATE_ROM = "/v1/upgrade/rom/info"
UPDATE_BIOS = "/v1/upgrade/bios/info"

CHECK_OFFLINE = "/v1/user/checkOfflineName"
GET_OFFLINE = "/v1/user/getOfflineName"

# Sensor Configuration
SENSOR_TYPES = {
    "boot_time": {
        "icon": "mdi:clock-time-eight",
        "label": "UGNas启动时长",
        "name": "boot_time",
        "device_Id": "device",
    },
    "mac1": {
        "icon": "mdi:account-network",
        "label": "MAC地址",
        "name": "mac1",
        "device_Id": "device",
        "category": "diagnostic",
    },
    "mac2": {
        "icon": "mdi:account-network",
        "label": "MAC地址",
        "name": "mac2",
        "device_Id": "device",
        "category": "diagnostic",
    },
    "device_id": {
        "icon": "mdi:identifier",
        "label": "设备ID",
        "name": "device_id",
        "device_Id": "device",
        "category": "diagnostic",
    },
    "device_name": {
        "icon": "mdi:label",
        "label": "设备名称",
        "name": "device_name",
        "device_Id": "device",
    },
    "cpu_used": {
        "icon": "mdi:cpu-64-bit",
        "label": "CPU占用",
        "name": "cpu_used",
        "unit_of_measurement": "%",
        "device_Id": "device",
    },
    "build_date": {
        "icon": "mdi:clock-outline",
        "label": "建造日期",
        "name": "build_date",
        "device_Id": "device",
    },
    "build_utc": {
        "icon": "mdi:clock-outline",
        "label": "建造日期",
        "name": "build_utc",
        "device_Id": "device",
    },
    "cpu": {
        "icon": "mdi:cpu-64-bit",
        "label": "CPU占用",
        "name": "cpu",
        "device_Id": "device",
    },
    "memory": {
        "icon": "mdi:memory",
        "label": "内存大小",
        "name": "memory",
        "device_Id": "device",
    },
    "model": {
        "icon": "mdi:globe-model",
        "label": "型号",
        "name": "model",
        "device_Id": "device",
    },
    "nas_server_ver": {
        "icon": "mdi:overscan",
        "label": "服务器版本",
        "name": "nas_server_ver",
        "device_Id": "device",
        "category": "diagnostic",
    },
    "nas_server_ver_no": {
        "icon": "mdi:overscan",
        "label": "服务器版本",
        "name": "nas_server_ver_no",
        "device_Id": "device",
        "category": "diagnostic",
    },
    "sn": {
        "icon": "mdi:devices",
        "label": "序列号",
        "name": "sn",
        "device_Id": "device",
        "category": "diagnostic",
    },
    "timezone": {
        "icon": "mdi:map-clock",
        "label": "当前时区",
        "name": "timezone",
        "device_Id": "device",
        "category": "diagnostic",
    },
    "upload_speed": {
        "icon": "mdi:upload",
        "label": "上传速度",
        "name": "upload_speed",
        "device_Id": "device",
    },
    "download_speed": {
        "icon": "mdi:download",
        "label": "下载速度",
        "name": "download_speed",
        "device_Id": "device",
    },
    "cpu_temp": {
        "icon": "mdi:thermometer",
        "label": "CPU温度",
        "name": "cpu_temp",
        "device_Id": "device",
        "device_class": "temperature",
        "unit_of_measurement": "°C",
        "state_class": "measurement",
    },
    "memory_used": {
        "icon": "mdi:memory",
        "label": "内存占用率",
        "name": "memory_used",
        "device_Id": "device",
        "unit_of_measurement": "%",
    },
    "memory_used_size": {
        "icon": "mdi:memory",
        "label": "已用内存",
        "name": "memory_used_size",
        "device_Id": "device",
        "device_class": "data_size",
    },
    "memory_total": {
        "icon": "mdi:memory",
        "label": "内存大小",
        "name": "memory_total",
        "device_Id": "device",
        "device_class": "data_size",
    },
    "fan_speed": {
        "icon": "mdi:fan",
        "label": "风扇转速",
        "name": "fan_speed",
        "device_Id": "device",
        "unit_of_measurement": "r/min",
    },
    "cpu_fan_speed": {
        "icon": "mdi:fan",
        "label": "CPU风扇转速",
        "name": "cpu_fan_speed",
        "device_Id": "device",
        "unit_of_measurement": "r/min",
    },
    "board_fan_speed": {
        "icon": "mdi:fan",
        "label": "板载风扇转速",
        "name": "board_fan_speed",
        "device_Id": "device",
        "unit_of_measurement": "r/min",
    },
}

SENSOR_TYPES_DISK = {
    "disk1_interface": {
        "icon": "mdi:globe-model",
        "label": "磁盘1类型",
        "name": "interface",
        "device_Id": "disk1",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk1_model": {
        "icon": "mdi:globe-model",
        "label": "磁盘1型号",
        "name": "model",
        "device_Id": "disk1",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk1_type": {
        "icon": "mdi:harddisk",
        "label": "磁盘1类型",
        "name": "type",
        "device_Id": "disk1",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk1_status": {
        "icon": "mdi:harddisk",
        "label": "磁盘1状态",
        "name": "status",
        "device_Id": "disk1",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk1_serial": {
        "icon": "mdi:devices",
        "label": "磁盘1序列号",
        "name": "serial",
        "device_Id": "disk1",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk1_temp": {
        "icon": "mdi:thermometer",
        "label": "磁盘1温度",
        "name": "temp",
        "device_Id": "disk1",
        "device_Name": "disk",
        "device_class": "temperature",
        "unit_of_measurement": "°C",
        "state_class": "measurement",
    },
    "disk1_size": {
        "icon": "mdi:chart-pie",
        "label": "磁盘1大小",
        "name": "size",
        "device_Id": "disk1",
        "device_Name": "disk",
        "device_class": "data_size",
    },
    "disk1_time": {
        "icon": "mdi:clock-time-eight",
        "label": "磁盘1使用时长",
        "name": "time",
        "device_Id": "disk1",
        "device_Name": "disk",
        "unit_of_measurement": "h",
    },
    "disk1_stpower": {
        "icon": "mdi:devices",
        "label": "硬盘1运行状态",
        "name": "stpower",
        "device_Id": "disk1",
        "device_Name": "disk",
    },
    "disk1_smartStatus": {
        "icon": "mdi:devices",
        "label": "硬盘1健康状态",
        "name": "smartStatus",
        "device_Id": "disk1",
        "device_Name": "disk",
    },

    "disk1_readspeed": {
        "icon": "mdi:devices",
        "label": "磁盘1读取速度",
        "name": "readspeed",
        "device_Id": "disk1",
        "device_Name": "disk",
    },
    "disk1_writespeed": {
        "icon": "mdi:devices",
        "label": "磁盘1写入速度",
        "name": "writespeed",
        "device_Id": "disk1",
        "device_Name": "disk",
    },
    "disk1_diskplace": {
        "icon": "mdi:devices",
        "label": "磁盘1位置",
        "name": "diskplace",
        "device_Id": "disk1",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk1_checkstatus": {
        "icon": "mdi:devices",
        "label": "磁盘1检查状态",
        "name": "checkstatus",
        "device_Id": "disk1",
        "device_Name": "disk",
    },

    "disk2_interface": {
        "icon": "mdi:globe-model",
        "label": "磁盘1类型",
        "name": "interface",
        "device_Id": "disk2",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk2_model": {
        "icon": "mdi:globe-model",
        "label": "磁盘1型号",
        "name": "model",
        "device_Id": "disk2",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk2_type": {
        "icon": "mdi:harddisk",
        "label": "磁盘1类型",
        "name": "type",
        "device_Id": "disk2",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk2_status": {
        "icon": "mdi:harddisk",
        "label": "磁盘1状态",
        "name": "status",
        "device_Id": "disk2",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk2_serial": {
        "icon": "mdi:devices",
        "label": "磁盘1序列号",
        "name": "serial",
        "device_Id": "disk2",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk2_temp": {
        "icon": "mdi:thermometer",
        "label": "磁盘1温度",
        "name": "temp",
        "device_Id": "disk2",
        "device_Name": "disk",
        "device_class": "temperature",
        "unit_of_measurement": "°C",
        "state_class": "measurement",
    },
    "disk2_size": {
        "icon": "mdi:chart-pie",
        "label": "磁盘1大小",
        "name": "size",
        "device_Id": "disk2",
        "device_Name": "disk",
        "device_class": "data_size",
    },
    "disk2_time": {
        "icon": "mdi:clock-time-eight",
        "label": "磁盘1使用时长",
        "name": "time",
        "device_Id": "disk2",
        "device_Name": "disk",
        "unit_of_measurement": "h",
    },
    "disk2_stpower": {
        "icon": "mdi:devices",
        "label": "硬盘1运行状态",
        "name": "stpower",
        "device_Id": "disk2",
        "device_Name": "disk",
    },
    "disk2_smartStatus": {
        "icon": "mdi:devices",
        "label": "硬盘1健康状态",
        "name": "smartStatus",
        "device_Id": "disk2",
        "device_Name": "disk",
    },

    "disk2_readspeed": {
        "icon": "mdi:devices",
        "label": "磁盘1读取速度",
        "name": "readspeed",
        "device_Id": "disk2",
        "device_Name": "disk",
    },
    "disk2_writespeed": {
        "icon": "mdi:devices",
        "label": "磁盘1写入速度",
        "name": "writespeed",
        "device_Id": "disk2",
        "device_Name": "disk",
    },
    "disk2_diskplace": {
        "icon": "mdi:devices",
        "label": "磁盘1位置",
        "name": "diskplace",
        "device_Id": "disk2",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk2_checkstatus": {
        "icon": "mdi:devices",
        "label": "磁盘1检查状态",
        "name": "checkstatus",
        "device_Id": "disk2",
        "device_Name": "disk",
    },


    "disk3_interface": {
        "icon": "mdi:globe-model",
        "label": "磁盘1类型",
        "name": "interface",
        "device_Id": "disk3",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk3_model": {
        "icon": "mdi:globe-model",
        "label": "磁盘1型号",
        "name": "model",
        "device_Id": "disk3",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk3_type": {
        "icon": "mdi:harddisk",
        "label": "磁盘1类型",
        "name": "type",
        "device_Id": "disk3",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk3_status": {
        "icon": "mdi:harddisk",
        "label": "磁盘1状态",
        "name": "status",
        "device_Id": "disk3",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk3_serial": {
        "icon": "mdi:devices",
        "label": "磁盘1序列号",
        "name": "serial",
        "device_Id": "disk3",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk3_temp": {
        "icon": "mdi:thermometer",
        "label": "磁盘1温度",
        "name": "temp",
        "device_Id": "disk3",
        "device_Name": "disk",
        "device_class": "temperature",
        "unit_of_measurement": "°C",
        "state_class": "measurement",
    },
    "disk3_size": {
        "icon": "mdi:chart-pie",
        "label": "磁盘1大小",
        "name": "size",
        "device_Id": "disk3",
        "device_Name": "disk",
        "device_class": "data_size",
    },
    "disk3_time": {
        "icon": "mdi:clock-time-eight",
        "label": "磁盘1使用时长",
        "name": "time",
        "device_Id": "disk3",
        "device_Name": "disk",
        "unit_of_measurement": "h",
    },
    "disk3_stpower": {
        "icon": "mdi:devices",
        "label": "硬盘1运行状态",
        "name": "stpower",
        "device_Id": "disk3",
        "device_Name": "disk",
    },
    "disk3_smartStatus": {
        "icon": "mdi:devices",
        "label": "硬盘1健康状态",
        "name": "smartStatus",
        "device_Id": "disk3",
        "device_Name": "disk",
    },

    "disk3_readspeed": {
        "icon": "mdi:devices",
        "label": "磁盘1读取速度",
        "name": "readspeed",
        "device_Id": "disk3",
        "device_Name": "disk",
    },
    "disk3_writespeed": {
        "icon": "mdi:devices",
        "label": "磁盘1写入速度",
        "name": "writespeed",
        "device_Id": "disk3",
        "device_Name": "disk",
    },
    "disk3_diskplace": {
        "icon": "mdi:devices",
        "label": "磁盘1位置",
        "name": "diskplace",
        "device_Id": "disk3",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk3_checkstatus": {
        "icon": "mdi:devices",
        "label": "磁盘1检查状态",
        "name": "checkstatus",
        "device_Id": "disk3",
        "device_Name": "disk",
    },

    "disk4_interface": {
        "icon": "mdi:globe-model",
        "label": "磁盘1类型",
        "name": "interface",
        "device_Id": "disk4",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk4_model": {
        "icon": "mdi:globe-model",
        "label": "磁盘1型号",
        "name": "model",
        "device_Id": "disk4",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk4_type": {
        "icon": "mdi:harddisk",
        "label": "磁盘1类型",
        "name": "type",
        "device_Id": "disk4",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk4_status": {
        "icon": "mdi:harddisk",
        "label": "磁盘1状态",
        "name": "status",
        "device_Id": "disk4",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk4_serial": {
        "icon": "mdi:devices",
        "label": "磁盘1序列号",
        "name": "serial",
        "device_Id": "disk4",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk4_temp": {
        "icon": "mdi:thermometer",
        "label": "磁盘1温度",
        "name": "temp",
        "device_Id": "disk4",
        "device_Name": "disk",
        "device_class": "temperature",
        "unit_of_measurement": "°C",
        "state_class": "measurement",
    },
    "disk4_size": {
        "icon": "mdi:chart-pie",
        "label": "磁盘1大小",
        "name": "size",
        "device_Id": "disk4",
        "device_Name": "disk",
        "device_class": "data_size",
    },
    "disk4_time": {
        "icon": "mdi:clock-time-eight",
        "label": "磁盘1使用时长",
        "name": "time",
        "device_Id": "disk4",
        "device_Name": "disk",
        "unit_of_measurement": "h",
    },
    "disk4_stpower": {
        "icon": "mdi:devices",
        "label": "硬盘1运行状态",
        "name": "stpower",
        "device_Id": "disk4",
        "device_Name": "disk",
    },
    "disk4_smartStatus": {
        "icon": "mdi:devices",
        "label": "硬盘1健康状态",
        "name": "smartStatus",
        "device_Id": "disk4",
        "device_Name": "disk",
    },

    "disk4_readspeed": {
        "icon": "mdi:devices",
        "label": "磁盘1读取速度",
        "name": "readspeed",
        "device_Id": "disk4",
        "device_Name": "disk",
    },
    "disk4_writespeed": {
        "icon": "mdi:devices",
        "label": "磁盘1写入速度",
        "name": "writespeed",
        "device_Id": "disk4",
        "device_Name": "disk",
    },
    "disk4_diskplace": {
        "icon": "mdi:devices",
        "label": "磁盘1位置",
        "name": "diskplace",
        "device_Id": "disk4",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk4_checkstatus": {
        "icon": "mdi:devices",
        "label": "磁盘1检查状态",
        "name": "checkstatus",
        "device_Id": "disk4",
        "device_Name": "disk",
    },

    "disk5_interface": {
        "icon": "mdi:globe-model",
        "label": "磁盘1类型",
        "name": "interface",
        "device_Id": "disk5",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk5_model": {
        "icon": "mdi:globe-model",
        "label": "磁盘1型号",
        "name": "model",
        "device_Id": "disk5",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk5_type": {
        "icon": "mdi:harddisk",
        "label": "磁盘1类型",
        "name": "type",
        "device_Id": "disk5",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk5_status": {
        "icon": "mdi:harddisk",
        "label": "磁盘1状态",
        "name": "status",
        "device_Id": "disk5",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk5_serial": {
        "icon": "mdi:devices",
        "label": "磁盘1序列号",
        "name": "serial",
        "device_Id": "disk5",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk5_temp": {
        "icon": "mdi:thermometer",
        "label": "磁盘1温度",
        "name": "temp",
        "device_Id": "disk5",
        "device_Name": "disk",
        "device_class": "temperature",
        "unit_of_measurement": "°C",
        "state_class": "measurement",
    },
    "disk5_size": {
        "icon": "mdi:chart-pie",
        "label": "磁盘1大小",
        "name": "size",
        "device_Id": "disk5",
        "device_Name": "disk",
        "device_class": "data_size",
    },
    "disk5_time": {
        "icon": "mdi:clock-time-eight",
        "label": "磁盘1使用时长",
        "name": "time",
        "device_Id": "disk5",
        "device_Name": "disk",
        "unit_of_measurement": "h",
    },
    "disk5_stpower": {
        "icon": "mdi:devices",
        "label": "硬盘1运行状态",
        "name": "stpower",
        "device_Id": "disk5",
        "device_Name": "disk",
    },
    "disk5_smartStatus": {
        "icon": "mdi:devices",
        "label": "硬盘1健康状态",
        "name": "smartStatus",
        "device_Id": "disk5",
        "device_Name": "disk",
    },

    "disk5_readspeed": {
        "icon": "mdi:devices",
        "label": "磁盘1读取速度",
        "name": "readspeed",
        "device_Id": "disk5",
        "device_Name": "disk",
    },
    "disk5_writespeed": {
        "icon": "mdi:devices",
        "label": "磁盘1写入速度",
        "name": "writespeed",
        "device_Id": "disk5",
        "device_Name": "disk",
    },
    "disk5_diskplace": {
        "icon": "mdi:devices",
        "label": "磁盘1位置",
        "name": "diskplace",
        "device_Id": "disk5",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk5_checkstatus": {
        "icon": "mdi:devices",
        "label": "磁盘1检查状态",
        "name": "checkstatus",
        "device_Id": "disk5",
        "device_Name": "disk",
    },

    "disk6_interface": {
        "icon": "mdi:globe-model",
        "label": "磁盘1类型",
        "name": "interface",
        "device_Id": "disk6",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk6_model": {
        "icon": "mdi:globe-model",
        "label": "磁盘1型号",
        "name": "model",
        "device_Id": "disk6",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk6_type": {
        "icon": "mdi:harddisk",
        "label": "磁盘1类型",
        "name": "type",
        "device_Id": "disk6",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk6_status": {
        "icon": "mdi:harddisk",
        "label": "磁盘1状态",
        "name": "status",
        "device_Id": "disk6",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk6_serial": {
        "icon": "mdi:devices",
        "label": "磁盘1序列号",
        "name": "serial",
        "device_Id": "disk6",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk6_temp": {
        "icon": "mdi:thermometer",
        "label": "磁盘1温度",
        "name": "temp",
        "device_Id": "disk6",
        "device_Name": "disk",
        "device_class": "temperature",
        "unit_of_measurement": "°C",
        "state_class": "measurement",
    },
    "disk6_size": {
        "icon": "mdi:chart-pie",
        "label": "磁盘1大小",
        "name": "size",
        "device_Id": "disk6",
        "device_Name": "disk",
        "device_class": "data_size",
    },
    "disk6_time": {
        "icon": "mdi:clock-time-eight",
        "label": "磁盘1使用时长",
        "name": "time",
        "device_Id": "disk6",
        "device_Name": "disk",
        "unit_of_measurement": "h",
    },
    "disk6_stpower": {
        "icon": "mdi:devices",
        "label": "硬盘1运行状态",
        "name": "stpower",
        "device_Id": "disk6",
        "device_Name": "disk",
    },
    "disk6_smartStatus": {
        "icon": "mdi:devices",
        "label": "硬盘1健康状态",
        "name": "smartStatus",
        "device_Id": "disk6",
        "device_Name": "disk",
    },

    "disk6_readspeed": {
        "icon": "mdi:devices",
        "label": "磁盘1读取速度",
        "name": "readspeed",
        "device_Id": "disk6",
        "device_Name": "disk",
    },
    "disk6_writespeed": {
        "icon": "mdi:devices",
        "label": "磁盘1写入速度",
        "name": "writespeed",
        "device_Id": "disk6",
        "device_Name": "disk",
    },
    "disk6_diskplace": {
        "icon": "mdi:devices",
        "label": "磁盘1位置",
        "name": "diskplace",
        "device_Id": "disk6",
        "device_Name": "disk",
        "category": "diagnostic",
    },
    "disk6_checkstatus": {
        "icon": "mdi:devices",
        "label": "磁盘1检查状态",
        "name": "checkstatus",
        "device_Id": "disk6",
        "device_Name": "disk",
    },
}

SENSOR_TYPES_STORAGES = {
    "storage1_label": {
        "icon": "mdi:devices",
        "label": "存储空间1名称",
        "name": "label",
        "device_Id": "storage1",
        "device_Name": "storage",
    },
    "storage1_host": {
        "icon": "mdi:devices",
        "label": "存储空间1主机",
        "name": "host",
        "device_Id": "storage1",
        "device_Name": "storage",
        "category": "diagnostic",
    },
    "storage1_mode": {
        "icon": "mdi:devices",
        "label": "存储空间1模式",
        "name": "mode",
        "device_Id": "storage1",
        "device_Name": "storage",
        "category": "diagnostic",
    },
    "storage1_name": {
        "icon": "mdi:devices",
        "label": "存储空间1名字",
        "name": "name",
        "device_Id": "storage1",
        "device_Name": "storage",
        "category": "diagnostic",
    },
    "storage1_size": {
        "icon": "mdi:chart-pie",
        "label": "存储空间1大小",
        "name": "size",
        "device_Id": "storage1",
        "device_Name": "storage",
        "device_class": "data_size",
    },
    "storage1_used": {
        "icon": "mdi:chart-pie",
        "label": "存储空间1已用",
        "name": "used",
        "device_Id": "storage1",
        "device_Name": "storage",
        "device_class": "data_size",
    },
    "storage1_used_gb": {
        "icon": "mdi:chart-pie",
        "label": "存储空间1已用",
        "name": "used_gb",
        "device_Id": "storage1",
        "device_Name": "storage",
        "device_class": "data_size",
    },
    "storage1_used_tb": {
        "icon": "mdi:chart-pie",
        "label": "存储空间1已用",
        "name": "used_tb",
        "device_Id": "storage1",
        "device_Name": "storage",
        "device_class": "data_size",
    },
    "storage1_type": {
        "icon": "mdi:devices",
        "label": "存储空间1类型",
        "name": "type",
        "device_Id": "storage1",
        "device_Name": "storage",
    },

    "storage2_label": {
        "icon": "mdi:devices",
        "label": "存储空间2名称",
        "name": "label",
        "device_Id": "storage2",
        "device_Name": "storage",
    },
    "storage2_host": {
        "icon": "mdi:devices",
        "label": "存储空间2主机",
        "name": "host",
        "device_Id": "storage2",
        "device_Name": "storage",
        "category": "diagnostic",
    },
    "storage2_mode": {
        "icon": "mdi:devices",
        "label": "存储空间2模式",
        "name": "mode",
        "device_Id": "storage2",
        "device_Name": "storage",
        "category": "diagnostic",
    },
    "storage2_name": {
        "icon": "mdi:devices",
        "label": "存储空间2名字",
        "name": "name",
        "device_Id": "storage2",
        "device_Name": "storage",
        "category": "diagnostic",
    },
    "storage2_size": {
        "icon": "mdi:chart-pie",
        "label": "存储空间2大小",
        "name": "size",
        "device_Id": "storage2",
        "device_Name": "storage",
        "device_class": "data_size",
    },
    "storage2_used": {
        "icon": "mdi:chart-pie",
        "label": "存储空间2已用",
        "name": "used",
        "device_Id": "storage2",
        "device_Name": "storage",
        "device_class": "data_size",
    },
    "storage2_used_gb": {
        "icon": "mdi:chart-pie",
        "label": "存储空间2已用",
        "name": "used_gb",
        "device_Id": "storage2",
        "device_Name": "storage",
        "device_class": "data_size",
    },
    "storage2_used_tb": {
        "icon": "mdi:chart-pie",
        "label": "存储空间2已用",
        "name": "used_tb",
        "device_Id": "storage2",
        "device_Name": "storage",
        "device_class": "data_size",
    },
    "storage2_type": {
        "icon": "mdi:devices",
        "label": "存储空间2类型",
        "name": "type",
        "device_Id": "storage2",
        "device_Name": "storage",
    },

    "storage3_label": {
        "icon": "mdi:devices",
        "label": "存储空间3名称",
        "name": "label",
        "device_Id": "storage3",
        "device_Name": "storage",
    },
    "storage3_host": {
        "icon": "mdi:devices",
        "label": "存储空间3主机",
        "name": "host",
        "device_Id": "storage3",
        "device_Name": "storage",
        "category": "diagnostic",
    },
    "storage3_mode": {
        "icon": "mdi:devices",
        "label": "存储空间3模式",
        "name": "mode",
        "device_Id": "storage3",
        "device_Name": "storage",
        "category": "diagnostic",
    },
    "storage3_name": {
        "icon": "mdi:devices",
        "label": "存储空间3名字",
        "name": "name",
        "device_Id": "storage3",
        "device_Name": "storage",
        "category": "diagnostic",
    },
    "storage3_size": {
        "icon": "mdi:chart-pie",
        "label": "存储空间3大小",
        "name": "size",
        "device_Id": "storage3",
        "device_Name": "storage",
        "device_class": "data_size",
    },
    "storage3_used": {
        "icon": "mdi:chart-pie",
        "label": "存储空间3已用",
        "name": "used",
        "device_Id": "storage3",
        "device_Name": "storage",
        "device_class": "data_size",
    },
    "storage3_used_gb": {
        "icon": "mdi:chart-pie",
        "label": "存储空间3已用",
        "name": "used_gb",
        "device_Id": "storage3",
        "device_Name": "storage",
        "device_class": "data_size",
    },
    "storage3_used_tb": {
        "icon": "mdi:chart-pie",
        "label": "存储空间3已用",
        "name": "used_tb",
        "device_Id": "storage3",
        "device_Name": "storage",
        "device_class": "data_size",
    },
    "storage3_type": {
        "icon": "mdi:devices",
        "label": "存储空间3类型",
        "name": "type",
        "device_Id": "storage3",
        "device_Name": "storage",
    },

    "storage4_label": {
        "icon": "mdi:devices",
        "label": "存储空间4名称",
        "name": "label",
        "device_Id": "storage4",
        "device_Name": "storage",
    },
    "storage4_host": {
        "icon": "mdi:devices",
        "label": "存储空间4主机",
        "name": "host",
        "device_Id": "storage4",
        "device_Name": "storage",
        "category": "diagnostic",
    },
    "storage4_mode": {
        "icon": "mdi:devices",
        "label": "存储空间4模式",
        "name": "mode",
        "device_Id": "storage4",
        "device_Name": "storage",
        "category": "diagnostic",
    },
    "storage4_name": {
        "icon": "mdi:devices",
        "label": "存储空间4名字",
        "name": "name",
        "device_Id": "storage4",
        "device_Name": "storage",
        "category": "diagnostic",
    },
    "storage4_size": {
        "icon": "mdi:chart-pie",
        "label": "存储空间4大小",
        "name": "size",
        "device_Id": "storage4",
        "device_Name": "storage",
        "device_class": "data_size",
    },
    "storage4_used": {
        "icon": "mdi:chart-pie",
        "label": "存储空间4已用",
        "name": "used",
        "device_Id": "storage4",
        "device_Name": "storage",
        "device_class": "data_size",
    },
    "storage4_used_gb": {
        "icon": "mdi:chart-pie",
        "label": "存储空间4已用",
        "name": "used_gb",
        "device_Id": "storage4",
        "device_Name": "storage",
        "device_class": "data_size",
    },
    "storage4_used_tb": {
        "icon": "mdi:chart-pie",
        "label": "存储空间4已用",
        "name": "used_tb",
        "device_Id": "storage4",
        "device_Name": "storage",
        "device_class": "data_size",
    },
    "storage4_type": {
        "icon": "mdi:devices",
        "label": "存储空间4类型",
        "name": "type",
        "device_Id": "storage4",
        "device_Name": "storage",
    },
}

BUTTON_TYPES = {
    "sleep": {
        "label": "休眠",
        "name": "sleep",
        "device_class": "restart",
        "device_Id": "device",
    },
    "reboot": {
        "label": "重启",
        "name": "reboot",
        "device_class": "restart",
        "device_Id": "device",
    },
    "shutdown": {
        "label": "关机",
        "name": "shutdown",
        "device_class": "restart",
        "device_Id": "device",
    },
}

UPDATE_TYPES = {
    "bios": {
        "label": "BIOS",
        "name": "bios",
        "friendly_name": "BISO版本",
        "device_Id": "device",
    },
    "firmware": {
        "label": "firmware",
        "name": "firmware",
        "friendly_name": "Firmware版本",
        "device_Id": "device",
    },
    "webui": {
        "label": "webui",
        "name": "webui",
        "friendly_name": "WebUI版本",
        "device_Id": "device",
    },

}

SWITCH_TYPES = {
    "indicator_light": {
        "icon": "mdi:account-lock",
        "label": "指示灯开关",
        "name": "indicator_light",
        "device_Id": "device",
        "turn_on_url": "/setting/v1/sys/indicator_light/set?indicator_light=1&api_token={api_token}",
        "turn_off_url": "/setting/v1/sys/indicator_light/set?indicator_light=0&api_token={api_token}",
        "turn_on_body": "1",
        "turn_off_body": "0",
        "show_url": "/setting/v1/sys/info?api_token={api_token}",
        "show_body": "data.indicator_light",

    },
    "poweronautomatically": {
        "icon": "mdi:power",
        "label": "通电自动开机",
        "name": "poweronautomatically",
        "device_Id": "device",
        "turn_on_url": "/setting/v1/sys/power_on_automatically/set?power_on_automatically=1&api_token={api_token}",
        "turn_off_url": "/setting/v1/sys/power_on_automatically/set?power_on_automatically=0&api_token={api_token}",
        "turn_on_body": "1",
        "turn_off_body": "0",
        "show_url": "/setting/v1/sys/info?api_token={api_token}",
        "show_body": "data.power_on_automatically",
    },
    "samba": {
        "icon": "mdi:monitor-share",
        "label": "Samba",
        "name": "samba",
        "device_Id": "device",
        "turn_on_url": '/v1/user/offline/account/switch?api_token={api_token}|{"open_samba":1}',
        "turn_off_url": '/v1/user/offline/account/switch?api_token={api_token}|{"open_samba":0}',
        "turn_on_body": "1",
        "turn_off_body": "0",
        "show_url": "/v1/user/getOfflineName?ver=2&api_token={api_token}",
        "show_body": "data.open_samba",
    },
    "samba_external": {
        "icon": "mdi:monitor-share",
        "label": "Samba外置存储检测",
        "name": "sambaexternal",
        "device_Id": "device",
        "turn_on_url": '/v1/user/offline/account/switch?api_token={api_token}|{"external_samba":1}',
        "turn_off_url": '/v1/user/offline/account/switch?api_token={api_token}|{"external_samba":0}',
        "turn_on_body": "1",
        "turn_off_body": "0",
        "show_url": "/v1/user/getOfflineName?ver=2&api_token={api_token}",
        "show_body": "data.external_samba",
    },
    "afp": {
        "icon": "mdi:monitor-share",
        "label": "AFP",
        "name": "afp",
        "device_Id": "device",
        "turn_on_url": '/v1/user/offline/account/switch?api_token={api_token}|{"open_afp":1}',
        "turn_off_url": '/v1/user/offline/account/switch?api_token={api_token}|{"open_afp":0}',
        "turn_on_body": "1",
        "turn_off_body": "0",
        "show_url": "/v1/user/getOfflineName?ver=2&api_token={api_token}",
        "show_body": "data.open_afp",
    },
    "ftp": {
        "icon": "mdi:monitor-share",
        "label": "FTP",
        "name": "ftp",
        "device_Id": "device",
        "turn_on_url": '/v1/ftp/server/open?api_token={api_token}|{"open_ftp":1}',
        "turn_off_url": '/v1/ftp/server/open?api_token={api_token}|{"open_ftp":0}',
        "turn_on_body": "1",
        "turn_off_body": "0",
        "show_url": "/v1/user/getOfflineName?ver=2&api_token={api_token}",
        "show_body": "data.open_ftp",
    },
    "webdav": {
        "icon": "mdi:monitor-share",
        "label": "WebDAV",
        "name": "webdav",
        "device_Id": "device",
        "turn_on_url": "/v1/webdav/set?on=1&api_token={api_token}",
        "turn_off_url": "/v1/webdav/set?on=0&api_token={api_token}",
        "turn_on_body": "1",
        "turn_off_body": "0",
        "show_url": "/v1/user/getOfflineName?ver=2&api_token={api_token}",
        "show_body": "data.open_webdav",
    },

}