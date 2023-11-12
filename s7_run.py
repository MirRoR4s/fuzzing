from model.test_case_gen.s7c.s7c_manager import S7CommunicationManager
from model.test_case_gen.s7c.s7_communication_socket_connection import S7CommunicationSocketConnection
from boofuzz.sessions import Session, Target
from pyfiglet import Figlet
import rich_click as click



@click.command()
@click.option(
    "--function",
    type=click.Choice(
        [
            "set up communication",
            "read var",
        ]
    ),
    show_default=True,
    help="请选择您要测试的功能",
)
def main(function):
    try:
        function = function.replace(' ', '_')

    except Exception as e:
        print(f'发生异常: {e}')
    else:
        print(f"您选择的功能为 {function}")
        ip, port = "192.168.101.172", 102
        session = Session(target=Target(connection=S7CommunicationSocketConnection(ip, port, "DT Data")),
                          # receive_data_after_each_request=True,
                          # receive_data_after_fuzz=True,
                          pre_send_callbacks=[cr_tpdu])

        manager = S7CommunicationManager()
        figlet = Figlet()
        # 字体列表可以参看 http://www.jave.de/figlet/fonts/overview.html
        figlet.setFont(font='slant')
        print(figlet.renderText("fuzzing S7C"))

        session.connect(manager.start_fuzz(function))
        session.fuzz()


def cr_tpdu(target: Target, fuzz_data_logger, session, sock):
    target._target_connection.pdu_type = "CR Connect Request"
    target.send(b'')
    target._target_connection.pdu_type = "DT Data"


if __name__ == "__main__":
    main()
