from boofuzz import *
from boofuzz.mutation import Mutation

def main():
    fuzzable_list = None
    if fuzzable_list is None:
        fuzzable_list = [False] * 8

        test = Block("parameter2", children=(
                Size("length part 2", "unknown_part", length=1, fuzzable=fuzzable_list[4]),
                Block("unknown_part", children=(
                    Byte("unknown char before load mem", 0x31, fuzzable=fuzzable_list[5]),
                    Bytes("length of load memory", 0x303030333332.to_bytes(6, 'big'), size=6, fuzzable=fuzzable_list[6]),
                    Bytes("Length of MC7 code", 0x303030323132.to_bytes(6, 'big'), size=6, fuzzable=fuzzable_list[7])))
        ))
    a = Request("request_download", children=(test))
    tmp = a.render()
    print(tmp)
    print(len(tmp))
    
    
    

if __name__ == "__main__":
    main()