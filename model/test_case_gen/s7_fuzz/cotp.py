"""
cotp 协议规范实现
"""
from scapy.packet import Packet
from scapy.fields import ByteField, ByteEnumField, ConditionalField, ShortField, StrLenField


def cond(pkt: Packet):
    """
    cond 条件函数，当 COTP 数据包的 pdu type 字段值为 0xe0 时返回 True。

    :param pkt: _description_
    :type pkt: _type_
    :return: 如果 pdu_type == 0xe0，那么返回 True，否则返回 False。
    :rtype: _type_
    """
    return pkt.pdu_type == 0xe0

class COTP(Packet):
    """
    COTP 协议规范

    :param Packet: _description_
    :type Packet: _type_
    :return: _description_
    :rtype: _type_
    """
    name = "COTP"
    fields_desc = [
        ByteField(name="length", default=None),
        ByteEnumField(name="pdu_type", default=0xf0, enum={0xe0: "CR Connect Request", 0xf0: "DT Data"}),
        
        # 依据 pdu type 的不同，可将 cotp 分为连接数据包和功能数据包两种。
        ConditionalField(ShortField(name="destination_reference", default=0x0000), cond=cond),
        ConditionalField(ShortField(name="source_reference", default=0x0000), cond=cond),
        
        ByteField(name="option", default=0x00),
        
        # 连接数据包还有一个名为 parameters 的变长字段
        ConditionalField(ByteField(name="parameter_code", default=0xc1), cond=cond),
        ConditionalField(ByteField(name="parameter_length", default=0x00), cond=cond),
        ConditionalField(StrLenField(name="parameter_data", default=None,length_from = lambda pkt: pkt.parameter_length), cond=cond)
    ]

    return pkt.pdu_type == 0xe0