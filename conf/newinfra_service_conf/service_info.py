# coding=utf-8

from util.tool.dict_tool import ObjectDict


redpacket_service = ObjectDict(
    appid="A11039",
    interfaceid="A11039001",  # 必传，但是又没有什么用，也没有拓展使用的打算，这里都用默认值写死
    service_name="redpacket"
)

user_service = ObjectDict(
    appid="A11005",
    interfaceid="A11005001",
    service_name="user"
)

position_service = ObjectDict(
    appid="A11009",
    interfaceid="A11009001",
    service_name="position"
)

employee_service = ObjectDict(
    appid="A11043",
    interfaceid="A11043001",
    service_name="employee"
)
