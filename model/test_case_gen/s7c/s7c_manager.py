"""
s7 协议原语创建指挥者
"""
from model.test_case_gen.s7c.s7_gen import S7CommunicationGenerator


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
        elif function == "read_szl":
            return self.s7_gen.read_szl(fuzzable_list)
        elif function == "run_plc":
            return self.s7_gen.run_plc(fuzzable_list)
        elif function == "stop_plc":
            return self.s7_gen.stop_plc(fuzzable_list)
        
