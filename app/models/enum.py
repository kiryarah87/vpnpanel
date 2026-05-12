from enum import Enum


class ProtocolType(str, Enum):
    HYSTERIA2_UDP = "hysteria2-udp"
    NAIVEPROXY = "naiveproxy"
    VLESS_TCP_REALITY = "vless-tcp-reality"
    VLESS_XHTTP_REALITY = "vless-xhttp-reality"
    VLESS_TCP_TLS = "vless-tcp-tls"


class PortType(str, Enum):
    RANDOM = "random"
    FIXED = "fixed"
