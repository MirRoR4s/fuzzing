from scapy.packet import Packet
from scapy.fields import ByteField, ShortField
import struct


class TPKT(Packet):
    name = "TPKT"
    fields_desc = [
        ByteField(name="version", default=3),
        ByteField(name="reserved", default=0),
        ShortField(name="length", default=None)
    ]

    def post_build(self, pkt, pay):
        if self.length is None:
            tmp_len = 2 + len(pay)
            print(pkt)
            pkt = pkt[:2] + struct.pack("!H", tmp_len) + pkt[4:]
        return pkt + pay