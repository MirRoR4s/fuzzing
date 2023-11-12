"""
cotp 协议规范实现
"""
import struct
from scapy.compat import Type
from scapy.packet import Packet
from scapy.fields import (
    ByteField,
    ByteEnumField,
    ConditionalField,
    ShortField,
    StrLenField,
    FieldListField,
    PacketField,
    StrFixedLenField,
    FieldLenField,
    XShortField,
    XByteField,
    PacketListField
)


class COTPParameters(Packet):
    name = "COTPParameters"
    fields_desc = [
        XByteField("parameter_code", 0xc1),
        XByteField("parameter_length", 0x02),
        StrLenField("parameter_data", b'', length_from=lambda pkt: pkt.parameter_length),
    ]


class COTPConnect(Packet):
    """
    COTPConnect cotp 连接数据包
    """
    name = "COTPConnect"
    fields_desc = [
        # 目的引用
        XShortField("destination_reference", 0x0000),
        # 源引用
        XShortField("source_reference", 0x000F),
        # 选项
        XByteField("option", 0x00),
        # src tsap 参数
        PacketListField("parameter", [
            COTPParameters(parameter_data=0x0101.to_bytes(2, 'little')),
            COTPParameters(parameter_code=0xc2, parameter_length=0x02, parameter_data=0x0102.to_bytes(2, 'little')),
            COTPParameters(parameter_code=0xc0, parameter_length=0x01, parameter_data=0xa.to_bytes(1, 'little'))
        ],
            COTPParameters)
    ]

    def guess_payload_class(self, payload):  # type: (bytes) -> Type[Packet]
        print(f'payload = {payload}')
        return COTPParameters


class COTPFunction(Packet):
    name = "COTPFunction"
    fields_desc = [ByteField(name="option", default=0x80)]


class COTP(Packet):
    """
    COTP 协议规范
    """
    name = "COTP"
    fields_desc = [
        # 长度
        ByteField("length", None),
        # PDU 类型
        ByteEnumField("pdu_type", 0xF0, {0xe0: "CR Connect Request", 0xF0: "DT Data"}),
        # 连接数据包
        ConditionalField(PacketField("Connect", COTPConnect(), COTPConnect), lambda pkt: pkt.pdu_type == 0xe0),
        # 功能数据包
        ConditionalField(PacketField("Function", COTPFunction(), COTPFunction), lambda pkt: pkt.pdu_type == 0xF0),
    ]

    def post_build(self, pkt, pay):  # type: (bytes, bytes) -> bytes
        if self.length == None:
            pkt = struct.pack("!b", len(pkt[1:])) + pkt[1:]
        return pkt + pay

    def guess_payload_class(self, payload: bytes) -> Type[Packet]:
        print(f'payload = {payload}')
        return COTPConnect if self.pdu_type == 0xe0 else COTPFunction
