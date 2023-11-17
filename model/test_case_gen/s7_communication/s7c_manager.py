"""
s7 协议原语创建指挥者
"""
from boofuzz.sessions import Session, Target
from boofuzz.blocks.request import Request
from model.test_case_gen.s7_communication.s7_gen import S7CommunicationGenerator
from model.test_case_gen.s7_communication.s7_communication_socket_connection import S7CommunicationSocketConnection


class S7CommunicationSession(Session):
    """
    S7CommunicationSession 针对于 S7 Communication 协议的模糊测试会话类，目前支持对7种功能进行模糊测试
    """

    def __init__(self, ip: str = "192.168.101.172", port: int = 102) -> None:

        super(S7CommunicationSession, self).__init__(
            target=Target(S7CommunicationSocketConnection(ip, port)),
            pre_send_callbacks=[S7CommunicationSession.cr_tpdu],
            post_test_case_callbacks=[S7CommunicationSession.s7c_post_callck],
            receive_data_after_fuzz=True,
        )
        self.s7_gen = S7CommunicationGenerator()

    @staticmethod
    def cr_tpdu(target: Target, fuzz_data_logger, session: Session, sock):
        """
        cr_tpdu 起始回调，用于发送 CR 数据包以及其它功能的前置数据包，比如请求下载等。
        """
        S7CommunicationSocketConnection.set_pdu_type("CR Connect Request")
        target.send(b"")
        S7CommunicationSocketConnection.set_pdu_type("DT Data")
        # 获取当前被 fuzz 的请求对象
        request: Request = session.fuzz_node
        req_name = request.name
        if req_name == "set_up_communication":
            pass
        elif req_name == "download":
            target.send(S7CommunicationGenerator.setup_communication().render())
            target.send(S7CommunicationGenerator.request_download().render())
        elif req_name == "upload":
            target.send(S7CommunicationGenerator.setup_communication().render())
            target.send(S7CommunicationGenerator.request_upload().render())

    @staticmethod
    def s7c_post_callck(target: Target, fuzz_data_logger, session: Session, sock):
        """
        s7c_post_callck fuzz 数据包后的回调，用于发送一些功能的后置数据包，比如结束下载等。
        """
        # 获取当前被 fuzz 的请求对象
        request: Request = session.fuzz_node
        req_name = request.name

        if req_name == "download":
            target.send(S7CommunicationGenerator.end_download().render())
        elif req_name == "upload":
            target.send(S7CommunicationGenerator.end_upload().render())

    def set_up_communication(self, fuzzable_list: list[bool] | None = None):
        """
        set_up_communication 传入一个布尔类型的列表，决定是否对以下字段进行模糊测试：
        
        1. Max AmQ (parallel jobs with ack) calling
        2. Max AmQ (parallel jobs with ack) called
        3. PDU length
        
        样例输入：0 0 1，这表示 [False, False, True]

        :param fuzzable_list: 确定变异规则的列表, 默认为 [False, False, True]
        :type fuzzable_list: list[bool] | None, optional
        """
        self.connect(S7CommunicationGenerator.setup_communication(fuzzable_list))
        self.fuzz()

    def read_var(self, fuzzable_list: list[int] | None = None):
        """
        read_var 传入一个布尔类型的列表，决定是否对以下字段进行模糊测试：
        
        1. Variable specification
        2. Length of following address specification
        3. Syntax ID
        4. Transport size
        5. Length
        6. DB number
        7. Area
        8. Address
        
        样例输入：0 0 0 0 0 0 0 1（表示仅对 Address 字段进行模糊测试）
        """
        self.connect(S7CommunicationGenerator.read_var(fuzzable_list))
        self.fuzz()

    def read_szl(self, fuzzable_list: list[bool] | None = None):
        """
        read_szl 传入一个布尔类型的列表，决定是否对以下字段进行模糊测试：
        
        1. SZL ID
        2. Index
        
        样例输入：0 1 （表示对 Index 字段进行模糊测试）
        """
        print(fuzzable_list)
        self.connect(S7CommunicationGenerator.read_szl(fuzzable_list))
        self.fuzz()

    def upload(self, fuzzable_list: list[bool] | None = None):
        """
        upload 传入一个布尔类型的列表，决定是否对以下字段进行模糊测试：
        1. function
        2. function status
        3. unknown bytes
        4. upload id
        
        样例输入： 0 1 0 0（表示仅对 Function status 字段进行模糊测试）
        注：对 Upload ID 字段进行模糊测试，通常会引起 PLC 发送错误信息。
        """
        upload_req = S7CommunicationGenerator.upload(fuzzable_list)
        self.connect(upload_req)
        self.fuzz()

    def download(self, fuzzable_list: list[bool] | None = None):
        """
        download 传入一个布尔类型的列表，决定是否对以下字段进行模糊测试：
        1. File identifier
        2. Block type
        3. Block number
        4. Destination filesystem
        5. Data
        
        样例输入： 0 0 0 0 1，表示仅对 Data 进行模糊测试
        不建议对除了 Data 之外的字段进行模糊测试，否则 PLC 会给出 Block 结构/语法异常。同时如果 Data 不满足 PLC 的要求，也会报出异常。
        
        :param fuzzable_list: _description_, defaults to None
        :type fuzzable_list: list[bool] | None, optional
        """
        download_req = S7CommunicationGenerator.download(fuzzable_list)
        # # 暂时假定仅有一个目标
        # target = self.targets[0]
        # target.open()
        # target.send(b'1')
        # # 发送建立通信数据包
        # target.send(S7CommunicationGenerator.setup_communication().render())
        # # 发送请求下载数据包
        # target.send(S7CommunicationGenerator.request_download().render())
        # # 模糊测试
        self.connect(download_req)
        self.fuzz()
        # 发送结束下载数据包
        # target.send(S7CommunicationGenerator.end_download().render())

    def run_plc(self, fuzzable_list: list[bool]):
        """
        run_plc 传入一个布尔类型的列表，决定是否对以下字段进行模糊测试：
        1. Unknown bytes
        
        样例输入：1（表示针对上述未知字节展开模糊测试）
        
        注：运行 PLC 数据包存在太多未知量，为了不破坏数据包的基本结构，暂时仅开放针对一个未知字段的模糊测试。
        在启动该功能的模糊测试后，一般来说 PLC 上的 Run 状态指示灯会亮起。
        """
        self.connect(S7CommunicationGenerator.run_plc(fuzzable_list))
        self.fuzz()

    def stop_plc(self, fuzzable_list: list[bool] | None = None):
        """
        stop_plc 传入一个布尔类型的列表，决定是否对以下字段进行模糊测试：
        1. Unknown bytes
        
        样例输入：1（表示针对上述未知字节展开模糊测试）
        
        注：运行 PLC 数据包存在太多未知量，为了不破坏数据包的基本结构，暂时仅开放针对一个未知字段的模糊测试。
        在启动该功能的模糊测试后，一般来说 PLC 上的 Stop 状态指示灯会亮起。
        """
        self.connect(S7CommunicationGenerator.stop_plc(fuzzable_list))
        self.fuzz()

    def start_fuzz(self, function: str):

        if function == 'set_up_communication':
            fuzzable_list = input_fuzzable(self.set_up_communication, 3)
            self.set_up_communication(fuzzable_list)

        elif function == 'read_var':
            fuzzable_list = input_fuzzable(self.read_var, 8)
            self.read_var(fuzzable_list)

        elif function == "read_szl":
            fuzzable_list = input_fuzzable(self.read_szl, 2)
            self.read_szl(fuzzable_list)

        elif function == "run_plc":
            fuzzable_list = input_fuzzable(self.run_plc, 1)
            self.run_plc(fuzzable_list)

        elif function == "stop_plc":
            fuzzable_list = input_fuzzable(self.stop_plc, 1)
            self.stop_plc(fuzzable_list)

        elif function == "upload":
            fuzzable_list = input_fuzzable(self.upload, 4)
            self.upload(fuzzable_list)

        elif function == "download":
            fuzzable_list = input_fuzzable(self.download, 5)
            self.download(fuzzable_list)


def input_fuzzable(function: callable, length) -> list:
    """
    input_fuzzable _summary_

    :param function: _description_
    :type function: object
    :param length: _description_
    :type length: _type_
    :return: _description_
    :rtype: list[int]
    """
    print(function.__doc__)
    while True:
        try:
            fuzzable_list = [int(i) for i in input("请您输入变异规则列表：").split()]
        except Exception:
            print("请您输入整数：")
        else:
            if len(fuzzable_list) != length:
                print("对不起，您输入的长度有误，请重新输入：")
                continue
            return [bool(i) for i in fuzzable_list]
