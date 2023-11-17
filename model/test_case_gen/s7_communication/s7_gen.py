"""
S7 Communication 协议模糊测试脚本，暂时提供 7 种不同功能的模糊测试。
"""
from boofuzz.primitives import Byte, Word, Bytes, DWord
from boofuzz.blocks import Block, Request, Size


# from boofuzz.protocol_session_reference import ProtocolSessionReference


class S7CommunicationGenerator:
    """
    S7协议模糊测试原语生成类
    """

    @staticmethod
    def define_header(
            block_name_for_parameter_length: str | None = None,
            block_name_for_data_length: str | None = None,
            protocol_id: int = 0x32,
            rosctr: int = 0x01,
            reserved: int = 0x0000,
            pdu_reference: int = 0x0000,
    ) -> Block:
        """
        define_header 定义协议首部，首部不进行变异，否则整个数据包会很混乱。

        :param block_name_for_parameter_length: 要计算参数长度的 block 名称
        :type block_name_for_parameter_length: str | None, optional
        :param block_name_for_data_length: 要计算数据长度的 block 名称
        :type block_name_for_data_length: str | None, optional
        :param protocol_id: _description_, defaults to 0x32
        :type protocol_id: int, optional
        :param rosctr: _description_, defaults to 0x01
        :type rosctr: int, optional
        :param reserved: _description_, defaults to 0x0000
        :type reserved: int, optional
        :param pdu_reference: _description_, defaults to 0x0000
        :type pdu_reference: int, optional
        :return: _description_
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
                Word("reserved", reserved, fuzzable=False),  # see here!
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
                Bytes("address", address.to_bytes(3, "big"), size=3, fuzzable=fuzzable_list[7]),
            ),
        )
        return item

    @staticmethod
    def define_download_and_upload_parameter(
            fuzzable_list: list[bool] | None = None,
            function: int | None = 0xfa,
            function_status: int | None = 0x00,
            unknown_bytes: int | None = 0x0100,
            upload_id: int | None = 0x00_00_00_00,
            file_identifier: int | None = 0x5f,
            block_type: int | None = 0x3042,
            block_number: int | None = 0x3030303030,
            destination_filesystem: int | None = 0x50,
    ) -> Block:
        """
        定义请求上传/下载、上传/下载、上传/下载结束三个数据包的公共参数部分。
        :param fuzzable_list:
        :param function:
        :param function_status:
        :param unknown_bytes:
        :param upload_id:
        :param file_identifier:
        :param block_type:
        :param block_number:
        :param destination_filesystem:
        :return:
        """
        if fuzzable_list is None:
            fuzzable_list = [False] * 4
        parameter = Block("parameter", children=(
            Byte("function", function, fuzzable=False),
            Byte("function_status", function_status, fuzzable=False),
            Word("unknown_bytes", unknown_bytes, endian='>', fuzzable=False),
            DWord("upload_id", upload_id, fuzzable=False),
            Size("filename_length", "filename", length=1, fuzzable=False),
            Block("filename", children=(
                Byte("file identifier", file_identifier, fuzzable=fuzzable_list[0]),
                Word("block type", block_type, endian='>', fuzzable=fuzzable_list[1]),
                # 如果 block number 不存在，plc 会返回错误！
                Bytes("block number", block_number.to_bytes(5, 'big'), fuzzable=fuzzable_list[2]),
                Byte("destination filesystem", destination_filesystem, fuzzable=fuzzable_list[3])
            )),
        ))
        return parameter

    @staticmethod
    def setup_communication(fuzzable_list: list[bool] | None = None):
        """
        setup_communication _summary_

        :param fuzzable_list: _description_, defaults to None
        :type fuzzable_list: list[bool], optional
        :return: _description_
        :rtype: _type_
        """
        fuzzable_list = [False] * 4 + [True] if fuzzable_list is None else fuzzable_list
        # 注意字节顺序应是大端
        header = S7CommunicationGenerator.define_header("parameter")
        parameter = Block(
            name="parameter",
            children=(
                Byte("function", 0xF0, full_range=True, fuzzable=False),
                Byte("reserved", 0x00, full_range=True, fuzzable=False),
                Word(
                    "max_amq_calling",
                    0x0001,
                    endian=">",
                    full_range=True,
                    fuzzable=fuzzable_list[0],
                ),
                Word(
                    "max_amq_called",
                    0x0001,
                    endian=">",
                    full_range=True,
                    fuzzable=fuzzable_list[1],
                ),
                Word(
                    "pdu_length",
                    960,
                    endian=">",
                    full_range=True,
                    fuzzable=fuzzable_list[2],
                ),
            ),
        )
        return Request(name="set_up_communication", children=(header, parameter))

    @staticmethod
    def read_var(fuzzable_list: list[bool] | None = None):
        """
        read_var _summary_

        :param fuzzable_list: 变异规则列表, defaults to None
        :type fuzzable_list: list[bool], optional
        :return: _description_
        :rtype: _type_
        """
        fuzzable_list = (
            [False] * 7 + [True] if fuzzable_list is None else fuzzable_list
        )
        header = S7CommunicationGenerator.define_header("parameter")
        parameter = Block(
            "parameter",
            children=(
                Byte("function", 0x04, fuzzable=False),
                Byte("item_count", 0x01, fuzzable=False),
                S7CommunicationGenerator.define_item(0x12, 0x0A, 0x10, 0x02, 0x0010, 0x0000, 0x03, 0x000000,
                                                     fuzzable_list[:8]),
                # S7CommunicationGenerator.define_item( 0x12, 0x0A, 0x10, 0x02, 0x0006, 0x0000, 0x05, 0x002080,
                # fuzzable_list[8:]),
            ),
        )
        return Request("read_var", children=(header, parameter))

    @staticmethod
    def read_szl(fuzzable_list: list[bool] | None = None):
        """
        read_szl 读取系统状态列表

        :param fuzzable_list: _description_, defaults to None
        :type fuzzable_list: list[bool] | None, optional
        :return: _description_
        :rtype: _type_
        """
        if fuzzable_list is None:
            fuzzable_list = [False] * 11 + [True]
        else:
            fuzzable_list = [False] * 10 + fuzzable_list

        header = S7CommunicationGenerator.define_header("parameter", "data", rosctr=0x07)
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
                Byte("return codee", 0xff, fuzzable=fuzzable_list[6]),
                Byte("Transport size", 0x09, fuzzable=fuzzable_list[7]),
                Size("Length", "SZL data", length=2, endian='>', fuzzable=fuzzable_list[8]),
                Block("SZL data", children=(
                    Word("szl_id", 0x0000, fuzzable=fuzzable_list[10]),
                    Word("index", 0x0000, fuzzable=fuzzable_list[11]),
                ))

            ),
        )
        return Request("read_szl", children=(header, parameter, data))

    @staticmethod
    def run_plc(fuzzable_list: list[bool] | None = None):
        """
        run_plc 运行plc，发送该数据包后plc的run指示灯应亮起。

        :param fuzzable_list: _description_, defaults to None
        :type fuzzable_list: list[bool] | None, optional
        """
        print(fuzzable_list)
        if fuzzable_list is None:
            fuzzable_list = [False, True, False, False, False, False]
        else:
            fuzzable_list = [False] + fuzzable_list + [False] * 4
        header = S7CommunicationGenerator.define_header("parameter")
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

    @staticmethod
    def stop_plc(fuzzable_list: list[bool] | None = None):
        """
        stop_plc 停止PLC运行

        :param fuzzable_list: _description_, defaults to None
        :type fuzzable_list: list[bool] | None, optional
        """
        if fuzzable_list is None:
            fuzzable_list = [False, True, False, False]
        else:
            fuzzable_list = [False] + fuzzable_list + [False] * 2
        header = S7CommunicationGenerator.define_header("parameter")
        parameter = Block(
            "parameter",
            children=(
                Byte("function", 0x29, fuzzable=fuzzable_list[0]),
                Bytes(
                    "unknown_bytes",
                    0x0000000000.to_bytes(5, "big"),
                    size=5,
                    fuzzable=fuzzable_list[1],
                ),
                Size(
                    "Length part 2",
                    "PI Service",
                    length=1,
                    fuzzable=fuzzable_list[2],
                ),
                Block(
                    "PI Service",
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

    @staticmethod
    def request_upload(fuzzable_list: list[bool] | None = None) -> Request:
        """
        request_upload 请求上传
        """
        if fuzzable_list is None:
            fuzzable_list = [False, False, False, False]
        header = S7CommunicationGenerator.define_header("parameter")
        parameter: Block = S7CommunicationGenerator.define_download_and_upload_parameter(fuzzable_list[:4], 0x1d, 0x00,
                                                                                         0x0000, 0x00000000, 0x5f,
                                                                                         0x3038, 0x3030303031, 0x41)
        return Request("start_upload", children=(header, parameter))

    @staticmethod
    def upload(fuzzable_list: list[bool] | None = None) -> Request:
        """
        upload 上传数据包，允许模糊测试的字段有：
        1. function
        2. function status
        3. unknown bytes
        4. upload id
        
        请传入一个布尔类型的列表控制上述变量的变异规则，默认情况下仅对 Unknown bytes 进行变异。
        """
        if fuzzable_list is None:
            fuzzable_list = [False, False, True, False]
        header = S7CommunicationGenerator.define_header("parameter")
        parameter = Block("parameter", children=(
            Byte("function", 0x1e, fuzzable=fuzzable_list[0]),
            Byte("function_status", 0x00, fuzzable=fuzzable_list[1]),
            Word("unknown_bytes", 0x00_00, fuzzable=fuzzable_list[2]),
            DWord("upload_id", 0x00_00_00_01, endian='>', fuzzable=fuzzable_list[3]),
        ))
        return Request("upload", children=(header, parameter))

    @staticmethod
    def end_upload(fuzzable_list: list[bool] | None = None) -> Request:
        """
        end_upload 结束上传
        """
        if fuzzable_list is None:
            fuzzable_list = [False] * 4
        header = S7CommunicationGenerator.define_header("parameter")
        parameter = Block("parameter", children=(
            Byte("function", 0x1f, fuzzable=fuzzable_list[0]),
            Byte("function_status", 0x00, fuzzable=fuzzable_list[1]),
            Word("error_code", 0x00_00, fuzzable=fuzzable_list[2]),
            DWord("upload_id", 0x00_00_00_01, endian='>', fuzzable=fuzzable_list[3]),
        ))
        return Request("upload", children=(header, parameter))

    @staticmethod
    def request_download(fuzzable_list: list[bool] | None = None) -> Request:
        """
        request_download 开始下载

        :param fuzzable_list: 未来如果有需要对请求下载进行变异的话，可以传入该参数，默认情况下为空。
        :type fuzzable_list: list[bool] | None, optional
        :return: _description_
        :rtype: Request
        """
        if fuzzable_list is None:
            fuzzable_list = [False] * 8
        header: Block = S7CommunicationGenerator.define_header("parameter")
        parameter: Block = S7CommunicationGenerator.define_download_and_upload_parameter(fuzzable_list[:4], 0xfa)
        parameter.push(
            Block("parameter2", children=(
                Size("length part 2", "unknown_part", length=1, fuzzable=fuzzable_list[4]),
                Block("unknown_part", children=(
                    Byte("unknown char before load mem", 0x31, fuzzable=fuzzable_list[5]),
                    Bytes("length of load memory", 0x303030333332.to_bytes(6, 'big'), size=6,
                          fuzzable=fuzzable_list[6]),
                    Bytes("Length of MC7 code", 0x303030323132.to_bytes(6, 'big'), size=6, fuzzable=fuzzable_list[7])))
            )))
        return Request("request_download", children=(header, parameter))

    @staticmethod
    def download(fuzzable_list: list[bool] | None = None) -> Request:
        """
        download 下载

        :param fuzzable_list: _description_, defaults to None
        :type fuzzable_list: list[bool] | None, optional
        :return: _description_
        :rtype: Request
        """
        # 寻找一个不会导致异常的 Data 起始值
        test_data = 0x001c00fb04a8000004c0000004c1000004b0000004b1000004b2000004b30000
        if fuzzable_list is None:
            fuzzable_list = [False] * 5
        header = S7CommunicationGenerator.define_header("parameter", "data")
        parameter: Block = S7CommunicationGenerator.define_download_and_upload_parameter(fuzzable_list[:4], 0xfb, 0x01)
        data = Block("data", children=(
            Bytes("unknown", test_data.to_bytes(32, 'big'), max_len=100, fuzzable=fuzzable_list[4])
        ))
        return Request("download", children=(header, parameter, data))

    @staticmethod
    def end_download(fuzzable_list: list[bool] | None = None) -> Request:
        """
        end_download _summary_

        :param fuzzable_list: _description_, defaults to None
        :type fuzzable_list: list[bool] | None, optional
        :return: _description_
        :rtype: Request
        """
        if fuzzable_list is None:
            fuzzable_list = [False] * 4
        header = S7CommunicationGenerator.define_header("parameter")
        parameter: Block = S7CommunicationGenerator.define_download_and_upload_parameter(fuzzable_list, 0xfc)
        return Request("end_download", children=(header, parameter))

    def system_info(self):
        pass
