    
    
global R_dict, I_dict, J_dict

R_dict = {
0 : "sll"  , 11 : "movn"   ,  25 :  "multu"   , 38  :  "xor" ,          #10: "movz"  not important
2 : "srl"  , 12 : "syscall",  26 :  "div"     , 39  :  "nor" ,          #11 : "movn" not important
3 : "sra"  , 13 : "break"  ,  27 :  "divu"    , 42  :  "slt" ,
4 : "sllv" , 15 : "sync"   ,  32 :  "add"     , 43  :  "sltu",
6 : "srlv" , 16 : "mfhi"   ,  33 :  "addu"    , 48  :  "tge" ,
7 : "srav" , 17 : "mthi"   ,  34 :  "sub"     , 49  :  "tgeu",
8 : "jr"   , 18 : "mflo"   ,  35 :  "subu"    , 50  :  "tlt" ,
9 : "jalr" , 19 : "mtlo"   ,  36 :  "and"     , 51  :  "tltu",
10: "movz" , 24 : "mult"   ,  37 :  "or"      , 52  :  "teq" ,
54: "tne"  }

I_dict = {
1  :  "bgez" , 1   :  "bltz" , 
4  :  "beq"  , 20  :  "beql" , 40  : "sb"   , 56   :   "sc"  ,
5  :  "bne"  , 21  :  "bnel" , 41  : "sh"   , 57   :   "swc1",
6  :  "blez" , 22  :  "blezl", 42  : "swl"  , 58   :   "swc2",
7  :  "bgtz" , 23  :  "bgtzl", 43  : "sw"   , 61   :   "sdc1",
8  :  "addi" ,                 46  : "swr"  , 62   :   "sdc2",
9  :  "addiu", 32  :  "lb"   , 47  : "cache", 
10 :  "slti" , 33  :  "lh"   , 48  : "ll"   , 
11 :  "sltiu", 34  :  "lwl"  , 49  : "lwc1" , 
12 :  "andi" , 35  :  "lw"   , 50  : "lwc2" , 
13 :  "ori"  , 36  :  "lbu"  , 51  : "pref" , 
14 :  "xori" , 37  :  "lhu"  , 53  : "idc1" , 
15 :  "lui"  , 38  :  "lwr"  , 54  : "idc2" , 

}   

J_dict = {2:"j",3:"jal"}

global reg_dict

reg_dict = {
0  :  "$zero"    , 10    :  "$t2", 20   :   "$s4", 30  : "$fp",
1  :  "$at"      , 11    :  "$t3", 21   :   "$s5", 31  : "$ra",
2  :  "$v0"      , 12    :  "$t4", 22   :   "$s6",  0  :   "00000",
3  :  "$v1"      , 13    :  "$t5", 23   :   "$s7",
4  :  "$a0"      , 14    :  "$t6", 24   :   "$t8",
5  :  "$a1"      , 15    :  "$t7", 25   :   "$t9",
6  :  "$a2"      , 16    :  "$s0", 26   :   "$k0",
7  :  "$a3"      , 17    :  "$s1", 27   :   "$k1",
8  :  "$t0"      , 18    :  "$s2", 28   :   "$gp",
9  :  "$t1"      , 19    :  "$s3", 29   :   "$sp",}       


class Instruction:

    def __init__(self, machine_code):
        self.machine_code = machine_code
        self.operation = ''
    
    def define_operation(self):

        op_code = self.machine_code[0:6]
        if op_code == "0"*6 :    #如果op code是000000那么是R-type的
            funct = self.machine_code[-6:]
            if int(funct,2) in R_dict:
                
                self.operation = R_dict[int(funct,2)]
            elif funct == "100101":
                print("#############OOOOOOOOOOOOOOOOOOOOORRRRRRRRRRRRRRRRRRRRR###############")
            
        elif int(op_code, 2) in I_dict:
            self.operation = I_dict[int(op_code, 2)]

        elif int(op_code,2) in J_dict:
            self.operation = J_dict[int(op_code,2)]
        else:
            self.operation = "or"
        print(self.operation)

def twos_tansfer(binary ):      #transfer a binary number into a two's complement
    ones = []
    for i in binary:            #process for one's complement
        if i == "0":
            ones.append("1")
        else:
            ones.append("0")
    binary = ''.join(ones)
    twos = []
    k = "1"
    for i in range(len(binary)):
        j = len(binary)-1-i

        if k == "1" and binary[j] == "1":       #1+1 = 10
            twos = ["0"]+twos
            k = "1"

        elif k=="0" and binary[j] == "0":
            twos = ["0"]+twos
            k = "0"

        else:
            twos = ["1"]+twos
            k = "0"  

    result = ''.join(twos)
    return result

def sign_bin_to_int(binary:str):
    if binary[0] == "1":                       #如果binary是补码负数
        twos  = twos_tansfer(binary)
        return -int(twos,2)
    else:                                   #有符号的2^15 binary
        return  int(binary,2)
