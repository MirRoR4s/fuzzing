from boofuzz import *


def main():
    a = Block("block_test",children=(
        Byte("byte_test", 1)
    ))
    b = Byte("test1", 2)

    c = Byte("c_test", 3)
    
    a1 = Request("mirror")
    
    a1.stack.append(a)
    a1.stack.append(b)
    a1.stack.append(c)
    
    print(a1.stack)
    
    a2 = Request("mirror_test", children=(a, b, c ))
    print(a2.stack)
    
    

if __name__ == "__main__":
    main()