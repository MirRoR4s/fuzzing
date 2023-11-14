from boofuzz import *


def main():
    a1 = Request("mirror")
    print(a1)
    a = Block("test",children=(
        
    ))
    a1.push(a)
    print(a1)
    b = Byte("test", 0)
    
    print(a.stack)
    a.push(b)
    print(a.stack)

if __name__ == "__main__":
    main()