from enum import Enum


class ProtocolType(str, Enum):
    HYSTERIA2 = "hysteria2"
    NAIVEPROXY = "naiveproxy"
    VLESS_TCP_REALITY = "vless-tcp-reality"
    VLESS_XHTTP_REALITY = "vless-xhttp-reality"


class PortType(str, Enum):
    RANDOM = "random"
    FIXED = "fixed"
