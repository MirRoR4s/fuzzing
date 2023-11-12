"""
s7 协议原语创建指挥者
"""
from model.test_case_gen.s7c.s7_gen import S7CommunicationGenerator
# from model.test_case_gen.s7c.s7_communication_socket_connection import S7CommunicationSocketConnection
# from model.test_case_gen.s7c.cotp import COTP
# from model.test_case_gen.s7c.tpkt import TPKT
# from boofuzz.sessions import Session, Target


class S7CommunicationManager:
    
    def __init__(self) -> None:
        self.s7_gen = S7CommunicationGenerator()
        
    def set_up_communication(self, fuzzable_list: list[bool] | None = None):
        return self.s7_gen.setup_communication(fuzzable_list)
        
    def read_var(self, fuzzable_list: list[bool] | None = None):
        return self.s7_gen.read_var(fuzzable_list)

    def start_fuzz(self, function: str, fuzzable_list: list[bool] | None = None):
        if function == 'set_up_communication':
            return self.s7_gen.setup_communication(fuzzable_list)
        elif function == 'read_var':
            return self.s7_gen.read_var(fuzzable_list)
