# coding=utf-8

from util.tool.dict_tool import ObjectDict

dict_service = ObjectDict(
    appid="A11003",
    interfaceid="A11003001",
    service_name="dict"
)

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
    appid="A11042",
    interfaceid="A11042001",
    service_name="employee"
)

application_service = ObjectDict(
    appid="A11017",
    interfaceid="A11017001",
    service_name="application"
)

sharechain_service = ObjectDict(
    appid="A11051",
    interfaceid="A11051001",
    service_name="sharechain"
)

company_service = ObjectDict(
    appid="A11007",
    interfaceid="A11007001",
    service_name="company"
)
