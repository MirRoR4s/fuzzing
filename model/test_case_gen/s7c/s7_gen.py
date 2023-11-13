from boofuzz.primitives import Byte, Word, Bytes, DWord
from boofuzz.blocks import Block, Request, Size


class S7CommunicationGenerator:
    """
    S7协议模糊测试原语生成类
    """

    @staticmethod
    def define_header(
        block_name_for_parameter_length: str,
        block_name_for_data_length: str | None = None,
        protocol_id: int = 0x32,
        rosctr: int = 0x01,
        reserved: int = 0x0000,
        pdu_reference: int = 0x0000,
    ) -> Block:
        """
        define_header 定义协议首部，首部的话不允许进行变异，否则整个数据包应该都会很混乱。

        :return: 首部
        :rtype: Block
        """
        data_length = Word("data_length", 0, endian=">", fuzzable=False)

        if block_name_for_data_length is not None:
            data_length = Size(
                "data_length",
                block_name_for_data_length,
                length=2,
                endian=">",
                fuzzable=False,
            )

        # 注意字节顺序应是大端
        header = Block(
            "header",
            children=(
                Byte("protocol_id", protocol_id, fuzzable=False),
                Byte("rosctr", rosctr, fuzzable=False),
                Word("reserved", reserved, fuzzable=True),  # see here!
                Word("pdu_reference", pdu_reference, fuzzable=False),
                Size(
                    "parameter_length",
                    block_name_for_parameter_length,
                    length=2,
                    endian=">",
                    fuzzable=False,
                ),
                data_length,
            ),
        )
        return header

    @staticmethod
    def define_item(
        var_specification: int,
        len_of_following_add_specification: int,
        syntax_id: int,
        transport_size: int,
        length: int,
        db_number: int,
        area: int,
        address: int,
        fuzzable_list: list[bool] | None = None,
    ) -> Block:
        """
        item 传入各项参数定义 item

        :param var_specification: _description_
        :type var_specification: int
        :param len_of_following_add_specification: _description_
        :type len_of_following_add_specification: int
        :param syntax_id: _description_
        :type syntax_id: int
        :param transport_size: _description_
        :type transport_size: int
        :param length: _description_
        :type length: int
        :param db_number: _description_
        :type db_number: int
        :param area: _description_
        :type area: int
        :param address: _description_
        :type address: int
        :param fuzzable_list: _description_, defaults to None
        :type fuzzable_list: list[bool] | None, optional
        :return: _description_
        :rtype: Block
        """
        item = Block(
            # "item",
            children=(
                Byte(
                    "variable_specification",
                    var_specification,
                    fuzzable=fuzzable_list[0],
                ),
                Byte(
                    "length_of_following_address_specification",
                    len_of_following_add_specification,
                    fuzzable=fuzzable_list[1],
                ),
                Byte("syntax_id", syntax_id, fuzzable=fuzzable_list[2]),
                Byte("transport_size", transport_size, fuzzable=fuzzable_list[3]),
                Word("length", length, endian=">", fuzzable=fuzzable_list[4]),
                Word("db_number", db_number, endian=">", fuzzable=fuzzable_list[5]),
                Byte("area", area, fuzzable=fuzzable_list[6]),
                Bytes("address", address.to_bytes(3, "big"), size=3, fuzzable=False),
            ),
        )
        return item

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
                Word(
                    "max_amq_calling",
                    0x0001,
                    endian=">",
                    full_range=True,
                    fuzzable=fuzzable_list[2],
                ),
                Word(
                    "max_amq_called",
                    0x0001,
                    endian=">",
                    full_range=True,
                    fuzzable=fuzzable_list[3],
                ),
                Word(
                    "pdu_length",
                    960,
                    endian=">",
                    full_range=True,
                    fuzzable=fuzzable_list[4],
                ),
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
        fuzzable_list = (
            [False] * 15 + [True] if fuzzable_list is None else fuzzable_list
        )
        header = self.define_header("parameter")
        parameter = Block(
            "parameter",
            children=(
                Byte("function", 0x04, fuzzable=False),
                Byte("item_count", 0x02, fuzzable=False),
                self.define_item(
                    0x12,
                    0x0A,
                    0x10,
                    0x02,
                    0x0010,
                    0x0000,
                    0x03,
                    0x000000,
                    fuzzable_list[:8],
                ),
                self.define_item(
                    0x12,
                    0x0A,
                    0x10,
                    0x02,
                    0x0006,
                    0x0000,
                    0x05,
                    0x002080,
                    fuzzable_list[8:],
                ),
            ),
        )
        return Request("read_var", children=(header, parameter))

    def read_szl(self, fuzzable_list: list[bool] | None = None):
        """
        read_szl 读取系统状态列表

        :param fuzzable_list: _description_, defaults to None
        :type fuzzable_list: list[bool] | None, optional
        :return: _description_
        :rtype: _type_
        """
        fuzzable_list = [False] * 8 + [True] if fuzzable_list is None else fuzzable_list
        header = self.define_header("parameter", "data", rosctr=0x07)
        parameter = Block(
            "parameter",
            children=(
                Bytes(
                    "parameter_head",
                    0x000112.to_bytes(3, "big"),
                    size=3,
                    fuzzable=fuzzable_list[0],
                ),
                Byte("parameter_length", 0x04, fuzzable=fuzzable_list[1]),
                Byte("method", 0x11, fuzzable=fuzzable_list[2]),
                Byte("method_body", 0x44, fuzzable=fuzzable_list[3]),
                Byte("subfunction", 0x01, fuzzable=fuzzable_list[4]),
                Byte("sequence_number", 0x00, fuzzable=fuzzable_list[5]),
            ),
        )
        data = Block(
            "data",
            children=(
                DWord("data_header", 0xFF090004, endian=">", fuzzable=fuzzable_list[6]),
                Word("szl_id", 0x0000, fuzzable=fuzzable_list[7]),
                Word("index", 0x0000, fuzzable=fuzzable_list[8]),
            ),
        )
        return Request("read_szl", children=(header, parameter, data))

    def run_plc(self, fuzzable_list: list[bool] | None = None):
        """
        run_plc 运行plc，发送该数据包后plc的run指示灯应亮起。

        :param fuzzable_list: _description_, defaults to None
        :type fuzzable_list: list[bool] | None, optional
        """
        fuzzable_list = (
            [False, True, False, False, False, False]
            if fuzzable_list is None
            else fuzzable_list
        )
        header = self.define_header("parameter")
        parameter = Block(
            "parameter",
            children=(
                Byte("function", 0x28, fuzzable=fuzzable_list[0]),
                Bytes(
                    "unknown_bytes",
                    0x000000000000FD.to_bytes(7, "big"),
                    size=7,
                    fuzzable=fuzzable_list[1],
                ),
                Size(
                    "parameter_block_length",
                    "parameter_block",
                    endian="<",
                    length=2,
                    fuzzable=fuzzable_list[2],
                ),
                Block(
                    "parameter_block",
                    children=(Bytes("unknown", size=0, fuzzable=fuzzable_list[3])),
                ),
                Size(
                    "string_length",
                    "pi_service",
                    endian=">",
                    length=1,
                    fuzzable=fuzzable_list[4],
                ),
                Block(
                    "pi_service",
                    children=(
                        Bytes(
                            "plc_start",
                            0x505F50524F4752414D.to_bytes(9, "big"),
                            size=9,
                            fuzzable=fuzzable_list[5],
                        )
                    ),
                ),
            ),
        )
        return Request("read_szl", children=(header, parameter))

    def stop_plc(self, fuzzable_list: list[bool] | None = None):
        """
        stop_plc 停止PLC运行

        :param fuzzable_list: _description_, defaults to None
        :type fuzzable_list: list[bool] | None, optional
        """
        fuzzable_list = (
            [False, True, False, False]
            if fuzzable_list is None
            else fuzzable_list
        )
        header = self.define_header("parameter")
        parameter = Block(
            "parameter",
            children=(
                Byte("function", 0x29, fuzzable=fuzzable_list[0]),
                Bytes(
                    "unknown_bytes",
                    0x0000000000.to_bytes(5, "big"),
                    size=7,
                    fuzzable=fuzzable_list[1],
                ),
                Size(
                    "string_length",
                    "pi_service",
                    endian=">",
                    length=1,
                    fuzzable=fuzzable_list[2],
                ),
                Block(
                    "pi_service",
                    children=(
                        Bytes(
                            "plc_start",
                            0x505f50524f4752414d.to_bytes(9, "big"),
                            size=9,
                            fuzzable=fuzzable_list[3],
                        )
                    ),
                ),
            ),
        )
        return Request("read_szl", children=(header, parameter))
        
        
        pass

    def control(self):
        pass

    def security(self):
        pass

    def system_info(self):
        pass
