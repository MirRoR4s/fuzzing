from model.fuzzing_case_gen.s7_communication.s7c_manager import S7CommunicationSession
from pyfiglet import Figlet
import rich_click as click


@click.command()
@click.argument('ip')
@click.argument('port', type=int)
# @click.option("--ip", default="192.168.101.172", help="模糊测试目标ip", type=str)
# @click.option("--port", type=int, default=102, help="模糊测试目标端口")
@click.option(
    "--function",
    type=click.Choice(
        [
            "set up communication",
            "read var",
            "read szl",
            "run plc",
            "stop plc",
            "data read",
            "upload",
            "download",
        ]
    ),
    show_default=True,
    help="模糊测试功能",
)
def start_fuzz(ip: str = "192.168.101.172", port: int = 102, function: str = "set up communication"):
    """
    start_fuzz 选择功能码进行模糊测试

    :param ip: _description_, defaults to "192.168.101.172"
    :type ip: str, optional
    :param port: _description_, defaults to 102
    :type port: int, optional
    :param function: _description_, defaults to "set up communication"
    :type function: str, optional
    """
    try:
        function = function.replace(" ", "_")
    except Exception:
        print("发生异常，使用 -- help 选项查看用法")
    else:
        print(f"您选择的功能为 {function}")
        manager = S7CommunicationSession(ip, port)
        figlet = Figlet()
        # 字体列表可以参看 http://www.jave.de/figlet/fonts/overview.html
        figlet.setFont(font="slant")
        print(figlet.renderText("fuzzing S7C"))
        manager.start_fuzz(function)


def main():
    start_fuzz()


if __name__ == "__main__":
    main()
