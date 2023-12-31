"""
重写连接类，将 s7 数据包封装在 cotp、tpkt 中
"""
from scapy.compat import raw
from boofuzz.connections.tcp_socket_connection import TCPSocketConnection
from .tpkt import TPKT
from .cotp import COTP


class S7CommunicationSocketConnection(TCPSocketConnection):
    """
    重写 TCPSocketConnection 的 send 方法发送 COTP、TPKT 协议层的数据，以便专心于 S7 协议的原语定义
    """
    pdu_type = "CR Connect Request"
    def __init__(self, host, port, send_timeout=5.0, recv_timeout=5.0, server=False):
        super(TCPSocketConnection, self).__init__(send_timeout, recv_timeout)
        self.host = host
        self.port = port
        self.server = server
        self._serverSock = None

    def send(self, data):
        """
        send _summary_

        :param pdu_type: _description_
        :type pdu_type: str
        :param data: _description_
        :type data: _type_
        """
        tpkt = TPKT()
        cotp = COTP(pdu_type=S7CommunicationSocketConnection.pdu_type)
        data = raw(tpkt/cotp/data)
        super().send(data)
    
    @staticmethod
    def set_pdu_type(pdu_type: str) -> None:
        """
        set_pdu_type 设置 pdu 类型

        :param pdu_type: _description_
        :type pdu_type: str
        """
        S7CommunicationSocketConnection.pdu_type = pdu_type