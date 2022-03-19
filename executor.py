import os
from instruction import R_dict, I_dict, J_dict, reg_dict, twos_tansfer

class Executor:

    def __init__(self, registerLst, memoryLst, load_line:str ,  in_lines:list, \
        in_line_index:int, PC_num:int, IO_file = 0):
        self.registerLst = registerLst
        self.memoryLst = memoryLst
        self.PC = PC_num                            #记录读入的PC数字
        self.line = load_line                       #读入的机器码01010101001 32bits
        self.in_lines = in_lines                    #读入的数据列表:list(str)
        self.in_line_index = in_line_index          #记录读入文件读到了哪一行
        self.out_terminal_string = ""               #往这个string写一行输出字符串
        self.exit = False                           #退出程序初始为假
        self.buffer = 16**5//4                      #用于syscal 的 sbrk
        self.IO_file = IO_file
        pass

    def string_concatenate(self, word_index,length = 10000):           #阅读memory中连续的字符串，直到遇到\0停止，字符串结尾
        real_address = word_index
    
        store_num = self.memoryLst[real_address]   #内存中存在的数            #这个地方//20的得到所存的地址
        n1 = store_num//(2**24);                            ch4 = chr(n1)
        n2 = (store_num-n1*(2**24))//(2**16);               ch3 = chr(n2)
        n3 = (store_num-n1*(2**24)-n2*(2**16))//(2**8);     ch2 = chr(n3)
        n4 = (store_num-n1*(2**24)-n2*(2**16)-n3*(2**8));   ch1 = chr(n4)
        # input("递归")
        # print("|"+ch1 + ch2 + ch3 + ch4+"|")
        if length >0:
            if n4 == 0:     return ""
            elif n3 == 0:   return ch1
            elif n2 == 0:   return ch1 + ch2
            elif n1 == 0:   return ch1 + ch2 + ch3
            else:           return ch1 + ch2 + ch3 + ch4 + self.string_concatenate(word_index+1, length-4)
        else:               return ""

    def show_last_10_mem(self):
        print("栈内存为：",end=" ")
        print(self.memoryLst[-30:])

    def execute_instruction(self):        #将一个instruction分配到一个MIPS函数并执行
        inst_oprt = int(self.line[0:6],2)
        print("执行阶段报告:", end = " ")
        if inst_oprt == 0:
            print("R类指令>>", end=" ")
            rs = self.line[6:11]; rt = self.line[11:16]; rd = self.line[16:21] 
            sa = self.line[21:26] ; funct = self.line[26:]
            funct_num = int(funct,2)
            print("rs = ",reg_dict[int(rs,2)], ",rt = ",reg_dict[int(rt,2)], ",rd = ", reg_dict[int(rd,2)])
            #rs,rt 序号化
            int_rs = self.registerLst[int(rs,2)]
            int_rt = self.registerLst[int(rt,2)]
            int_sa = int(sa,2)
            #将 rs, rt转化成32位 binary
            bin_rs = bin(int_rs)[2:];  bin_rs = "0"*(32 - len(bin_rs)) + bin_rs
            bin_rt = bin(int_rt)[2:];  bin_rt = "0"*(32 - len(bin_rt)) + bin_rt

        #R-type instruction 
            if funct_num == 0:      self.MIPS_sll    (bin_rt, rd, int_sa)
            elif funct_num == 2:    self.MIPS_srl    (bin_rt, rd, int_sa)
            elif funct_num == 3:    self.MIPS_sra    (bin_rt, rd, int_sa)
            elif funct_num == 4:    self.MIPS_sllv   (bin_rt, rd, int_rs)
            elif funct_num == 6:    self.MIPS_srlv   (bin_rt, rd, int_rs)
            elif funct_num == 7:    self.MIPS_srav   (bin_rt, rd, int_rs)
            elif funct_num == 8:    self.MIPS_jr     (int_rs)
            elif funct_num == 9:    self.MIPS_jalr   (int_rs, rd)
            elif funct_num == 12:   self.MIPS_syscall()
            elif funct_num == 17:   self.MIPS_mthi   (int_rs)
            elif funct_num == 18:   self.MIPS_mflo   (rd)
            elif funct_num == 19:   self.MIPS_mtlo   (int_rs)
            elif funct_num == 24:   self.MIPS_mult   (int_rs, int_rt)
            elif funct_num == 25:   self.MIPS_multu  (int_rs, int_rt)
            elif funct_num == 26:   self.MIPS_div    (int_rs, int_rt)
            elif funct_num == 27:   self.MIPS_divu   (int_rs, int_rt)
            elif funct_num == 32:   self.MIPS_add    (int_rs, int_rt, rd)
            elif funct_num == 33:   self.MIPS_addu   (int_rs, int_rt, rd)
            elif funct_num == 34:   self.MIPS_sub    (int_rs, int_rt, rd)
            elif funct_num == 35:   self.MIPS_subu   (int_rs, int_rt, rd)
            elif funct_num == 36:   self.MIPS_and    (bin_rs, bin_rt, rd)                
            elif funct_num == 37:   self.MIPS_or     (bin_rs, bin_rt, rd)
            elif funct_num == 38:   self.MIPS_xor    (bin_rt, bin_rs, rd)
            elif funct_num == 39:   self.MIPS_nor    (bin_rs, bin_rt, rd)
            elif funct_num == 42:   self.MIPS_slt    (int_rs, int_rt, rd)
            elif funct_num == 43:   self.MIPS_sltu   (int_rs, int_rt, rd)

        #指令属于 I 型
        elif inst_oprt in I_dict.keys():
            print("I类指令>>", end=" ")
            op = self.line[0:6];  rs = self.line[6:11]; rt = self.line[11:16]; imm = self.line[16:]

            #rs,rt 序号化
            int_rs = self.registerLst[int(rs,2)]
            int_rt = self.registerLst[int(rt,2)]
            unsign_int_imm = int(imm,2)             #无符号转换的imm

            if imm[0] == "1":                       #如果imm是补码负数
                twos_imm  = twos_tansfer(imm)
                int_imm = -int(twos_imm,2)
            else:                                   #有符号的2^15imm整数
                int_imm = int(imm,2)
            print("rs = ",reg_dict[int(rs,2)], ",rt = ",reg_dict[int(rt,2)], ",imm = ", int_imm)


            #将 rs, rt转化成32位 binary
            bin_rs = bin(int_rs)[2:];  bin_rs = "0"*(32 - len(bin_rs)) + bin_rs
            bin_rt = bin(int_rt)[2:];  bin_rt = "0"*(32 - len(bin_rt)) + bin_rt
            bin_imm = bin(int_imm)[2:];  bin_imm = "0"*(32 - len(bin_imm)) + bin_imm

            if op == "001000"  : self.MIPS_addi (int_rs, rt, int_imm)
            elif op == "001001": self.MIPS_addiu(int_rs, rt, int_imm)
            elif op == "001100": self.MIPS_andi (rt, bin_rs, bin_imm)
            elif op == "000100": self.MIPS_beq  (rs,rt,int_imm)
            elif op == "000001": self.MIPS_bgez (int_rs, int_imm)
            elif op == "000111": self.MIPS_bgtz (int_rs, int_imm)
            elif op == "000110": self.MIPS_blez (int_rs, int_imm)
            elif op == "000001": self.MIPS_bltz (int_rs, int_imm)
            elif op == "000101": self.MIPS_bne  (int_rs, int_rt, int_imm)
            elif op == "100000": self.MIPS_lb   (int_rs, int_imm, rt)
            elif op == "100100": self.MIPS_lbu  (int_rs, unsign_int_imm, rt)
            elif op == "100001": self.MIPS_lh   (int_rs, int_imm, rt)
            elif op == "100101": self.MIPS_lhu  (int_rs, unsign_int_imm, rt)
            elif op == "001111": self.MIPS_lui  (rt,int_imm)
            elif op == "100011": self.MIPS_lw   (rt,int_rs,int_imm)
            elif op == "001101": self.MIPS_ori  (rt, int_rs, int_imm)
            elif op == "101000": self.MIPS_sb   (int_rs, rt, int_imm)
            elif op == "001010": self.MIPS_slti (rt, int_rs, int_imm)
            elif op == "001011": self.MIPS_sltiu(rt, int_rs, unsign_int_imm)
            elif op == "101001": self.MIPS_sh   (int_rs, rt, int_imm)
            elif op == "101011": self.MIPS_sw   (int_rs, rt, int_imm)
            elif op == "001110": self.MIPS_xori (rt, bin_rs, bin_imm)
            elif op == "100010": self.MIPS_lwl  (int_rs, int_imm, rt)
            elif op == "100110": self.MIPS_lwr  (int_rs, int_imm, rt)
            elif op == "101010": self.MIPS_swl  (int_rs, int_imm, rt)
            elif op == "101110": self.MIPS_swr  (int_rs, int_imm, rt)

        elif inst_oprt in J_dict.keys():
            print("J类指令>>", end=" ")
            op = self.line[0:6];  bin_target = self.line[6:]
            unsign_int_target = int(bin_target, 2)

            if bin_target[0] == "1":                       #如果imm是补码负数
                twos_target  = twos_tansfer(bin_target)
                int_target = -int(twos_target,2)
            else:                                   #有符号的2^15imm整数
                int_target = int(bin_target,2)
            print("bin_target = ",bin_target, ",unsign_int_target = ",unsign_int_target, ",int_target = ", int_target)

            if op   == "000010" : self.MIPS_j   (bin_target)
            elif op == "000011" : self.MIPS_jal (bin_target)

    #R-type begain...
    def MIPS_j(self, bin_target):
        complete_bin = bin_target+"00"
        address_num  = int(complete_bin,2)
        self.PC = (address_num-4*(16**5))-4
        print("下一步PC = ", self.PC)
        print("jump")

    def MIPS_jal(self, bin_target):
        complete_bin = bin_target+"00"
        address_num  = int(complete_bin,2)
        self.registerLst[31] = self.PC
        self.PC = (address_num-4*(16**5))-4
        print("下一步PC = ", self.PC)

        print("jal")

    #I-type begains...
    def MIPS_addi(self, int_rs, rt, int_imm):       #常数加法
        print("MIPS_addi")
        ans = int_rs + int_imm
        self.registerLst[int(rt,2)] = ans
        # if int(rt,2) == 29: input("addi $sp 操作执行")
    
    def MIPS_addiu(self, int_rs, rt, unsign_int_imm):      #常数加法unsigned 暂时同上
        print("MIPS_addi")
        self.MIPS_addi(int_rs, rt, unsign_int_imm)

    def MIPS_andi(self,rt, bin_rs, bin_imm):
        bin_ans = ""
        for i in range(32):
            if bin_rs[i] == "1" and bin_imm[i] == "1":
                bin_ans += "1"
            else:
                bin_ans += "0"
        int_ans = int(bin_ans,2)
        self.registerLst[int(rt,2)] = int_ans    

    def MIPS_beq(self, int_rs, int_rt, int_imm):        #如果寄存器rs和rt相等，条件转移指令数移动int_imm
        if int_rs == int_rt:
            self.PC += int_imm

    def MIPS_bne(self, int_rs, int_rt, int_imm):
        # input("PRESS TO NEXT...")
    
        if int_rs != int_rt:
            
            self.PC += (int_imm+1)*4-4

        print("MIPS_bne()")
        print("当前pc = ", self.PC)
        # input("PRESS TO NEXT...")

    def MIPS_lb(self, int_rs, int_imm, rt):     
        real_address = (int_rs-4*(16**5))//4        #读入memory list 中 rs对应的地址
        target_address = real_address + int_imm     #加上偏移量的目标地址
        load_num = self.memoryLst[target_address]   #将目标寄存器赋予得到地址的值
        byte_num = load_num % (2**8)
        # self.registerLst[int(rt,2)] == self.PC+int_imm   
        self.registerLst[int(rt,2)] = byte_num

        print("MIPS_lb()")
    def MIPS_lbu(self, int_rs, unsign_int_imm, rt): 
           
        print("MIPS_lbu()")
        real_address = (int_rs-4*(16**5))//4        #读入memory list 中 rs对应的地址
        target_address = real_address + unsign_int_imm     #加上偏移量的目标地址
        load_num = self.memoryLst[target_address]   #将目标寄存器赋予得到地址的值
        byte_num = load_num % (2**8)
        # self.registerLst[int(rt,2)] == self.PC+int_imm   
        self.registerLst[int(rt,2)] = byte_num

    def MIPS_lh(self, int_rs, int_imm, rt):     
        print("MIPS_lh()")
        real_address = (int_rs-4*(16**5))//4        #读入memory list 中 rs对应的地址
        target_address = real_address + int_imm     #加上偏移量的目标地址
        load_num = self.memoryLst[target_address]   #将目标寄存器赋予得到地址的值
        byte_num = load_num % (2**16)
        # self.registerLst[int(rt,2)] == self.PC+int_imm   
        self.registerLst[int(rt,2)] = byte_num
        
    def MIPS_lhu(self, int_rs, unsign_int_imm, rt):    
        print("lhu load half unsign")
        real_address = (int_rs-4*(16**5))//4        #读入memory list 中 rs对应的地址
        target_address = real_address + unsign_int_imm     #加上偏移量的目标地址
        load_num = self.memoryLst[target_address]   #将目标寄存器赋予得到地址的值
        byte_num = load_num % (2**16)
        # self.registerLst[int(rt,2)] == self.PC+int_imm   
        self.registerLst[int(rt,2)] = byte_num


    def MIPS_lui(self,rt,int_imm ):     #load upper immediate载入高位
        print("lui : load upper immediate")
        self.registerLst[int(rt,2)] = int_imm*(2**16)
    def MIPS_lw(self,rt,int_rs,int_imm):            #将地址address中32为数字存入寄存器rt中
        # input("PRESS TO NEXT...")

        real_address = int_rs-4*(16**5)                 #读入memory list 中 rs对应的地址
        print("real_address:", real_address)
        target_address = real_address//4 + int_imm//4         #加上偏移量的目标地址

        load_num = self.memoryLst[target_address]   #将目标寄存器赋予得到地址的值
        # self.registerLst[int(rt,2)] == self.PC+int_imm   
        self.registerLst[int(rt,2)] = load_num
        print("lw操作获取的数字是:", load_num)
        print("MIPS_lw()")
        self.show_last_10_mem()
        # input("Press to next...")

    def MIPS_ori(self,rt, int_rs, int_imm):  #载入低位
        print("MIPS_ori()")
        self.registerLst[int(rt,2)] = int_rs + int_imm
    def MIPS_sb(self, int_rs, rt, int_imm):         #将寄存器rt的 byte 保存到地址address中
        print("int_rs", int_rs )
        real_address = int_rs-4*(16**5)                 #读入memory list 中 rs对应的地址
        print("real_address:", real_address)
        target_address = real_address//4 + int_imm//4         #加上偏移量的目标地址
        print("列表位置为：",target_address )

        word_num = self.registerLst[int(rt,2)] 
        print("要存的数字是：", word_num)
        print("内存的大小是 = ", len(self.memoryLst))
        self.memoryLst[target_address] = word_num

        byte_num = self.registerLst[int(rt,2)] % (2**8)
        self.memoryLst[target_address] = byte_num
        print("sb操作获取的target_address是:", target_address)
        print("MIPS_sb()")

        input("press to next...")

    def MIPS_slti(self, rt, int_rs, int_imm):                            #Set Less Than Immidiate
    #Set register rt to 1 if register rs is less than the sign-extended immediate, and to 0 otherwise.
        if int_rs<int_imm: self.registerLst[int(rt,2)] = 1; print("{} 比 {} {}".format(int_rs, int_imm,"小"))
        else:              self.registerLst[int(rt,2)] = 0; print("{} 比 {} {}".format(int_rs, int_imm,"大"))
        print("MIPS_slti()")
    def MIPS_sltiu(self, rt, int_rs, unsign_int_imm):                   #参考上面的函数
        print("MIPS_sltiu()")
        if int_rs<unsign_int_imm: self.registerLst[int(rt,2)] = 1; print("{} 比 {} {}".format(int_rs, unsign_int_imm,"小"))
        else:              self.registerLst[int(rt,2)] = 0; print("{} 比 {} {}".format(int_rs, unsign_int_imm,"大"))

    def MIPS_sh(self, int_rs, rt, int_imm):             #将寄存器的低16位半字存入地址中
        real_address = (int_rs-4*(16**5))//4        #读入memory list 中 rs对应的地址
        target_address = real_address + int_imm     #加上偏移量的目标地址
        half_num = self.registerLst[int(rt,2)] % (2**16)
        self.memoryLst[target_address] = half_num
        print("sh操作获取的target_address是:", target_address)
        print("MIPS_sh()")                              #############功能实现障碍##############
    def MIPS_sw(self, int_rs, rt, int_imm):             #############功能实现障碍##############
        print("int_rs", int_rs )
        real_address = int_rs-4*(16**5)                 #读入memory list 中 rs对应的地址
        print("real_address:", real_address)
        target_address = real_address//4 + int_imm//4         #加上偏移量的目标地址
        print("列表位置为：",target_address )

        word_num = self.registerLst[int(rt,2)] 
        print("要存的数字是：", word_num)
        print("内存的大小是 = ", len(self.memoryLst))
        self.memoryLst[target_address] = word_num
        print("MIPS_sw()")                              #############功能实现障碍##############
        self.show_last_10_mem()
        # input("Press to next...")

    def MIPS_xori(self, rt, bin_rs, bin_imm):    
        ans = ""
        for i in range(32):
            if(bin_rs[i] == bin_imm[i]):                #若两数的这个位数上的数相同
                ans+="0"
            else:
                ans+="1"
        if ans[0] == "1":
            int_ans = -int(twos_tansfer(ans),2)
        else:
            int_ans = int(ans,2)
        self.registerLst[int(rt,2)]  = int_ans
        print("MIPS_xori()")
    def MIPS_lwl(self, int_rs, int_imm, rt):                           #程序的实现暂时照抄 lw 操作
        real_address = (int_rs-4*(16**5))//4        #读入memory list 中 rs对应的地址
        target_address = real_address + int_imm     #加上偏移量的目标地址
        load_num = self.memoryLst[target_address]   #将目标寄存器赋予得到地址的值
        left_load_num = load_num // (2**16)
        self.registerLst[int(rt,2)] = left_load_num
        print("lwl left操作获取的半字数字是:", left_load_num)
        print("MIPS_lwl()")


    def MIPS_lwr(self, int_rs, int_imm, rt):    
        real_address = (int_rs-4*(16**5))//4        #读入memory list 中 rs对应的地址
        target_address = real_address + int_imm     #加上偏移量的目标地址
        load_num = self.memoryLst[target_address]   #将目标寄存器赋予得到地址的值
        right_load_num = load_num % (2**16)
        self.registerLst[int(rt,2)] = right_load_num
        print("lwl left操作获取的半字数字是:", right_load_num)

        print("MIPS_lwr()")
    def MIPS_swl(self, int_rs, int_imm, rt):            #存入左半字
        real_address = (int_rs-4*(16**5))//4            #读入memory list 中 rs对应的地址
        target_address = real_address + int_imm         #加上偏移量的目标地址
        word_num = self.registerLst[int(rt,2)] 
        left_word_num = word_num//(2**16)
        self.memoryLst[target_address] = left_word_num
        print("MIPS_swl()")
    def MIPS_swr(self,int_rs, int_imm, rt):    
        real_address = (int_rs-4*(16**5))//4            #读入memory list 中 rs对应的地址
        target_address = real_address + int_imm         #加上偏移量的目标地址
        word_num = self.registerLst[int(rt,2)] 
        right_word_num = word_num//(2**16)
        self.memoryLst[target_address] = right_word_num
        print("MIPS_swr()")

    def MIPS_bgez(self, int_rs, int_imm):               #如果int_rs大于等于0，则偏移
        print("bgez")
        if int_rs>=0:   self.PC+=int_imm
    def MIPS_bgtz(self, int_rs, int_imm):               #如果int_rs大于0，则偏移                
        print("bgtz")
        if int_rs>0:   self.PC+=int_imm
    def MIPS_blez(self, int_rs, int_imm):               #如果int_rs小于等于0，则偏移
        print("blez")
        if int_rs<=0:   self.PC+=int_imm
    def MIPS_bltz(self, int_rs, int_imm):               #如果int_rs小于0，则偏移
        print("bltz")
        if int_rs<0:   self.PC+=int_imm




    #R-type begains...
    def MIPS_add(self, int_rs, int_rt, rd):     #rd = rs + rt
        print("MIPS_add ", "rs值 = ",int_rs, "rt值 = ",int_rt)
        # int_sum = int(bin_rs,2) + int(bin_rt,2)
        int_sum = int_rs + int_rt       #暂时存储为一个十进制数
        # self.registerLst[int(rd,2)] = "0"*(32-len(bin_sum)) + bin_sum
        self.registerLst[int(rd,2)] = int_sum

        pass
    def MIPS_addu(self, rs, rt, rd):        #听说addu和add暂时没啥差别，就先按add运行了
        print("MIPS_addu")
        self.MIPS_add(rs, rt, rd)
    def MIPS_and(self, bin_rs, bin_rt, rd):     #诸位比较是否是都是1 and 操作
        print("MIPS_and")
        and_val = ""
        for i in range(32):
            if bin_rs[i] == "1" and bin_rt[i]== "1":
                and_val += "1"
            else:
                and_val += "0"
        and_int = int(and_val,2)
        self.registerLst[int(rd,2)] = and_int
    def MIPS_div(self, int_rs, int_rt):                 #除法
        print("MIPS_div")
        remaind = int_rs % int_rt
        quotient = int_rs // int_rt
        self.Lo = quotient
        self.Hi = remaind
        print(self.Lo)
        print(self.Hi)
    def MIPS_divu(self, int_rs, int_rt):     #听说divu和div 暂时没啥差别，就先按add运行
        print("MIPS_divu")
        self.MIPS_div( int_rs, int_rt)
    def MIPS_jalr(self, int_rs, rd):                    #***还没实现***
        print("MIPS_jalr")
        self.registerLst[int(rd,2)] = self.PC + 4          #将rd的值赋为PC+4的值（地址）
        self.PC = int_rs                                    #将PC无条件赋值为int_rs
        # print("self.PC", self.PC)
    def MIPS_jr(self, int_rs):                          #jr jump register将PC赋值为rs存储的地址

        print("MIPS_jr")
        self.PC = int_rs
        # print("self.PC", self.PC)
        # input("PRESS TO NEXT...")

    def MIPS_mflo(self, rd):                            #把LO输入寄存器
        print("MIPS_mflo")
        self.registerLst[int(rd,2)] = self.Lo
        # print("int_rd", rd)
    def MIPS_mthi(self, int_rs):                        #存储HI
        print("MIPS_mthi")
        self.Hi = int_rs
    def MIPS_mtlo(self, int_rs):                        #存储LO
        print("MIPS_mtlo")
        self.Lo = int_rs
    def MIPS_mult(self, int_rs, int_rt):                #乘法
        print("MIPS_mult")
        anwser = int_rs * int_rt
        bin_ans= bin(anwser)[2:]
        bin_ans= "0"*(64-len(bin_ans)) + bin_ans
        self.Hi = int(bin_ans[0:32],2)
        self.Lo = int(bin_ans[32:],2)
        print("self.Lo", self.Lo, "self.Hi", self.Hi)
    def MIPS_multu(self, int_rs, int_rt):               #乘法
        print("MIPS_multu")
        self.MIPS_mult(int_rs, int_rt)
    def MIPS_nor(self,bin_rs, bin_rt, rd):              #each bit nor
        print("MIPS_nor")
        or_ans = ""
        for i in range(32):
            if bin_rs[i] == 0 and bin_rt[i] == 0:   or_ans+="1"
            else:                                   or_ans+="0"
        int_ans = int(or_ans,2)
        self.registerLst[int(rd,2)] = int_ans

    def MIPS_or(self, bin_rs, bin_rt, rd):              #each bit or
        print("MIPS_or")
        or_ans = ""
        for i in range(32):
            if bin_rs[i] == 0 and bin_rt[i] == 0:   or_ans+="0"
            else:                                   or_ans+="1"
        int_ans = int(or_ans,2)
        self.registerLst[int(rd,2)] = int_ans

    def MIPS_sll(self, bin_rt, rd, int_sa):             #左移通过检测
        print("MIPS_sll")
        print("bin_rt",bin_rt)
        bin_moved = bin_rt[int_sa:] + "0"*int_sa
        print("bin_moved", bin_moved)
        int_moved = int(bin_moved,2)
        print("int_moved", int_moved)
        self.registerLst[int(rd,2)] = int_moved

    def MIPS_sllv(self, bin_rt, rd, int_rs):            #左移通过检测
        print("MIPS_sllv")
        self.MIPS_sll(bin_rt, rd, int_rs)

    def MIPS_slt(self, int_rs, int_rt,rd):              #比小Set less than
        print("MIPS_slt")
        if int_rs < int_rt:
            self.registerLst[int(rd,2)] = 1
        else:
            self.registerLst[int(rd,2)] = 0

    def MIPS_sltu(self, int_rs, int_rt,rd):             #暂时同上
        print("MIPS_sltu")
        self.MIPS_slt(int_rs, int_rt,rd)

    def MIPS_sra(self, bin_rt, rd, int_sa):             #Shift right arithmetic   还没检测
        print("MIPS_sra")
        if len(bin_rt) == 32 and bin_rt[0] == "1":
            bin_moved = "1"*int_sa + bin_rt[:-int_sa]
            int_moved = -int(twos_tansfer(bin_moved), 2)
        else:
            bin_moved = "0"*int_sa + bin_rt[:-int_sa]
            int_moved = int(bin_moved,2)
        self.registerLst[int(rd,2)] = int_moved

    def MIPS_srav(self, bin_rt, rd, int_rs):            #算数右移Shift right arithmetic variable
        print("MIPS_srav")
        self.MIPS_sra(bin_rt, rd, int_rs)               #有变量的sra
        
    def MIPS_srl(self, bin_rt, rd, int_sa):             #逻辑右移
        print("MIPS_srl")
        bin_moved = "0"*int_sa + bin_rt[:-int_sa]
        int_moved = int(bin_moved,2)
        self.registerLst[int(rd,2)] = int_moved

    def MIPS_srlv(self, bin_rt, rd, int_rs):            #寄存器变量逻辑右移
        print("MIPS_srlv")
        self.MIPS_srl(bin_rt, rd, int_rs)

    def MIPS_sub(self, int_rs,int_rt, rd):          #减法
        print("MIPS_sub")
        ans = int_rs - int_rt
        self.registerLst[int(rd,2)] = ans

    def MIPS_subu(self, int_rs,int_rt, rd):         #暂时和简单减法一样
        print("MIPS_subu")
        self.MIPS_sub(int_rs,int_rt, rd)

    def MIPS_xor(self, bin_rt, bin_rs,rd):          #逐位异或
        print("MIPS_xor")
        ans = ""
        for i in range(32):
            if(bin_rt[i] == bin_rs[i]):     #若两数的这个位数上的数相同
                ans+="0"
            else:
                ans+="1"
        if ans[0] == "1":
            int_ans = -int(twos_tansfer(ans),2)
        else:
            int_ans = int(ans,2)
        self.registerLst[int(rd,2)]  = int_ans
        
    def MIPS_syscall(self):
        
        print("MIPS_syscall")
        #检查$v0的值之后决定进入哪一个system call
    
        if self.registerLst[2] == 1:                self.MIPS_sys_print_int()
        elif self.registerLst[2] == 4:              self.MIPS_sys_print_string()
        elif self.registerLst[2] == 5:              self.MIPS_sys_read_int()
        elif self.registerLst[2] == 8:              self.MIPS_sys_read_string()
        elif self.registerLst[2] == 9:              self.MIPS_sys_sbrk()
        elif self.registerLst[2] == 10:             self.MIPS_sys_exit()
        elif self.registerLst[2] == 11:             self.MIPS_sys_print_char()
        elif self.registerLst[2] == 12:             self.MIPS_sys_read_char()
        elif self.registerLst[2] == 13:             self.MIPS_sys_open()
        elif self.registerLst[2] == 14:             self.MIPS_sys_read()
        elif self.registerLst[2] == 15:             self.MIPS_sys_write()
        elif self.registerLst[2] == 16:             self.MIPS_sys_close()
        elif self.registerLst[2] == 17:             self.MIPS_sys_exit2()


    def MIPS_sys_print_int(self):       #调用寄存器$a0, 一个数字  
        print("系统调用输出 print_int $a0 = ", self.registerLst[4])
        str_num = str(self.registerLst[4])
        self.out_terminal_string += str_num
        pass
    def MIPS_sys_print_string(self):    #调用寄存器$a0， 一段地址
        a0 = self.registerLst[4]        #$a0存放的整数
        real_address = int((a0-4*(16**5))/4) + int((a0-4*(16**5))%4)   
        #减去0x400 000的初始内存 得到memory list 中的位置
        store_num = self.memoryLst[real_address]   #内存中存在的数            
        str_line = self.string_concatenate(real_address)

        if self.out_terminal_string.find("\n") != -1: print("@@@换行@@@")

        print("系统调用输出 print_string $a0 = ", a0)
        print("$a0指向的地址 所存的数 = ",store_num)
        print("字符串", str_line)
        self.out_terminal_string += str_line
        pass
    def MIPS_sys_read_int(self):       
        print("系统调用， read_int")
        readin_data = self.in_lines[self.in_line_index]
        readin_data:str
        try:
            num = int(readin_data.strip())
            print("读取的数字是 = ", num)
        except:
            print("sys_read_int读取整数出错")
            num = 0
        self.registerLst[2] = num   #将$v0赋值
        self.in_line_index += 1     #读取后读取行数+=1
        pass
    def MIPS_sys_read_char(self):     #现在能够读到这个char但是不知道要存在哪里
        print("MIPS_sys_read_char")   
        char = self.in_lines[self.in_line_index]
        char:str
        print("输入的char是:", char)
        self.registerLst[2] = ord(char.strip())
        self.in_line_index += 1     #读取后读取行数+=1
        pass
    def MIPS_sys_read_string(self):        
        print("MIPS_sys_read_string")
        a0 = self.registerLst[4]; a1 = self.registerLst[5]
        buffer = a0             ;length = a1
        real_address = int((a0-4*(16**5))/4) + int((a0-4*(16**5))%4)

        str_line = self.string_concatenate(real_address, length)
        self.out_terminal_string += str_line
        self.in_line_index += 1
        pass
    def MIPS_sys_sbrk(self):        #具体实现过程不清楚
        while self.memoryLst[self.buffer] != 0:
            print("buffer增长", self.buffer)
            self.buffer += 1
            input("press to next...")
        print("MIPS_sys_sbrk")
        input("press to contiue...")
        pass
    def MIPS_sys_exit(self):        #将程序退出判断标记改为真      
        self.exit = True
        print("sys_exit 程序结束")
        pass
    def MIPS_sys_print_char(self):     
        num = self.registerLst[4]
        str_char= chr(num)
        self.out_terminal_string += str_char
        print("MIPS_sys_print_char")
        pass
    def MIPS_sys_open(self):        
        a0 = self.registerLst[4]        #获取a0整数
        a1 = self.registerLst[5]; Flag = a1
        a2 = self.registerLst[6]; Mode = a2
        real_address = int((a0-4*(16**5))/4) + int((a0-4*(16**5))%4)
        file_name_str = self.string_concatenate(real_address)
        print("文件名称是:",file_name_str)
        print("sys_open")
        os.open(file_name_str,Flag,Mode)
        input("press to contiue...")
        pass    
    def MIPS_sys_read(self):    
        self.buffer = 16 ** 6    
        print("sys_read")
        input("press to contiue...")
        pass
    def MIPS_sys_write(slef):        
        print("sys_write")
        input("press to contiue...")
        pass
    def MIPS_sys_close(self):        
        print("sys_close")
        input("press to contiue...")
        pass
    def MIPS_sys_exit2(self):        
        print("sys_exit2")
        input("press to contiue...")
        pass
