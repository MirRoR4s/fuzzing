from boofuzz.primitives import Byte, Word, Bytes
from boofuzz.blocks import Block, Request


class S7CommunicationGenerator:
    """
    S7协议模糊测试原语生成类
    """
    @staticmethod
    def define_header() -> Block:
        """
        define_header 定义协议首部

        :return: 首部
        :rtype: Block
        """
        # 注意字节顺序应是大端
        header = Block("header", children=(
                Byte("Protocol_id", 0x32, fuzzable=False),
                Byte("rosctr", 0x01, fuzzable=False),
                Word("reserved", 0x0000, fuzzable=False),
                Word("pdu_reference", 0x0000, fuzzable=False),
                Word("parameter_length", 0x0008, endian='>', fuzzable=False),
                Word("data_length", 0x0000, fuzzable=False),
            ),
        )
        return header
    
    def setup_communication(self, fuzzable_list: list[bool] | None = None):
        """
        setup_communication _summary_

        :param fuzzable_list: _description_, defaults to None
        :type fuzzable_list: list[bool], optional
        :return: _description_
        :rtype: _type_
        """
        fuzzable_list = [False] * 4 + [True] if fuzzable_list is None else fuzzable_list
        # 注意字节顺序应是大端
        header = self.define_header()
        parameter = Block(
            name="parameter",
            children=(
                Byte("function", 0xF0, full_range=True, fuzzable=fuzzable_list[0]),
                Byte("reserved", 0x00, full_range=True, fuzzable=fuzzable_list[1]),
                Word("max_amq_calling", 0x0001, endian=">", full_range=True, fuzzable=fuzzable_list[2]),
                Word("max_amq_called", 0x0001, endian='>', full_range=True, fuzzable=fuzzable_list[3]),
                Word("pdu_length", 960, endian='>', full_range=True, fuzzable=fuzzable_list[4]),
            ),
        )
        return Request(name="set_up_communication", children=(header, parameter))

    def read_var(self, fuzzable_list: list[bool] | None = None):
        """
        read_var _summary_

        :param fuzzable_list: 变异规则列表, defaults to None
        :type fuzzable_list: list[bool], optional
        :return: _description_
        :rtype: _type_
        """
        fuzzable_list = [False] * 7 + [True] if fuzzable_list is None else fuzzable_list
        header = self.define_header()
        parameter = Block("parameter", children=(
            Byte("function", 0x04, fuzzable=False),
            Byte("item_count", 0x01, fuzzable=False),
        ))
        item = Block("item", children=(
            Byte("variable_specification", 0x12, fuzzable=fuzzable_list[0]),
            Byte("length_of_following_address_specification", 0x0a, fuzzable=fuzzable_list[1]),
            Byte("syntax_id", 0x10, fuzzable=fuzzable_list[2]),
            Byte("transport_size", 0x02, fuzzable=fuzzable_list[3]),
            Word("length", 0x0010, endian='>', fuzzable=fuzzable_list[4]),
            Word("db_number", 0x0000, endian='>', fuzzable=fuzzable_list[5]),
            Byte("area", 0x03, fuzzable=fuzzable_list[6]),
            Bytes("address", 0x000000.to_bytes(3, 'big'), max_len=5, fuzzable=fuzzable_list[7])
        ))
        return Request("read_var", children=(header, parameter, item))

    def date_and_time(self):
        pass

    def control(self):
        pass

    def security(self):
        pass

    def system_info(self):
        pass


