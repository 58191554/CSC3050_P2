global R_dict, I_dict, J_dict, reg_dict
from instruction import R_dict, I_dict, J_dict, reg_dict, twos_tansfer
from data_reader import DataReader
from data_writer import DataWriter
from executor import Executor

import time

class Simulator:

    def __init__(self, machin_code_file = "test.txt", MIPS_path = "test.asm", out_mem_file_path= "tz_mem.bin",
     out_register_file = "tz_register.bin", input_file = "test.in", terminal_out_file = "tz_terminal.out"):

        self.mem_size = 6*  (16**5)  //  4

        self.registerLst = [0]*35     #除了$zero寄存器初始化为0以外，其他寄存器都初始化为   ""
        self.registerLst[29] = self.mem_size*4 + 4*(16**5)      #栈指针初始
        self.registerLst[28] = 5275648
        self.Lo = 0                            #特别的两个寄存器
        self.Hi = 0                            #特别的两个寄存器
        self.PC = 0         #The PC will change each time when the instruction done
        self.memory = [0]*self.mem_size                   #6MB内存

        self.machin_code_file = machin_code_file
        self.MIPS_code_file = MIPS_path                         #输入的MIPS的文件路径    
        self.input_file = input_file                            #输入的.in文件                    
        self.out_mem_file = out_mem_file_path                   #输出的mem.bin文件路径
        self.out_register_file = out_register_file              #输出的register.bin文件路径
        self.out_terminal_string = ""                           #输出的字符
        self.terminal_out_file = terminal_out_file              #模拟系统调用的输出文件.out文件
        self.prog_scale = range(6*(2**20))                      #PC是按照byte来计算的所有是以2^8为一个单位的


    def read_into_memory(self):
        dataReader = DataReader(self.memory, self.MIPS_code_file, self.machin_code_file)
        dataReader.read_machine_Code()      #将机器码读入内存
        dataReader.extract_data()           #将MIPS .data读入内存
        self.memory = dataReader.memory

    
    def execute_prog(self):

        with open(self.input_file, "r") as infile:      #将.in文件读入
            in_lines = infile.readlines()

        print("\n"+"*"*40+"START EXECUTING..."+"*"*40)

        in_line_index = 0

        while self.PC in self.prog_scale:

            # time.sleep(0.8)
            print("\n"+"*"*40+"..."+"*"*40+"\n", "PC = ", self.PC)
            load_int = self.memory[self.PC//4]                      #从内存中获取指令 的 int 格式
            if load_int == 0: break                                 #若为空指令，那么停止运行
            bin_load_line = bin(load_int)[2:]                       #将 int 格式转化成 32位 二进制 机器码
            load_line = "0"*(32-len(bin_load_line)) + bin_load_line
            line_exe = Executor(self.registerLst, self.memory, load_line, in_lines,\
                 in_line_index, self.PC)                            #建立当前的 指令执行器
            line_exe.execute_instruction()                          #调用指令执行器的方法进行指令执行
            self.registerLst = line_exe.registerLst                 #得到指令执行器加工后的输出
            self.memory = line_exe.memoryLst                        #得到指令执行器加工后的输出
            in_line_index = line_exe.in_line_index                  #读取输入的行数+1
            self.out_terminal_string += line_exe.out_terminal_string#拼接输出字符串
            self.PC = line_exe.PC                                   #PC同步
            print("输出字符串>>",self.out_terminal_string)           #调试期间用于模拟终端输出

            #terminal输出把新的字符串合并进去
            self.show_registers()                                   #展示当前寄存器占用情况
            self.PC+=4                                              #PC 进入下一行
            if line_exe.exit == True: break                         #判断程序是否需要syscall提前终结
            
        pass

    def show_memory(self):
        null_count = 0
        flage = False
        for i in range(len(self.memory)):
            info = self.memory[i]   #设置规则认为如果有连续10个null那么就是内存空挡
                            
            if info == 0:        null_count += 1
            else:                null_count = 0

            if null_count>10:         continue
            elif null_count == 10 and flage == False:print("\n\n.test end... TO BE CONTINUE...\n"); flage = True
            else:                     print(str(i)+" " + str(info),end = " ")
        target_idx = int((80*(2**16)-4*(16**5))/4)

        print("目标位置>>", target_idx,"目标字符串>>", self.memory[target_idx])
    
    def show_registers(self):
        print("=="*15,"寄存器表", "=="*15)
        for i in range(32):
            if i % 8 == 0:print()       #显示8个一行
            print(reg_dict[i], " = " , self.registerLst[i], end = " ")
        
    def output_as_bin(self):
        mem_writer = DataWriter(self.memory, self.out_mem_file)
        mem_writer.write_bin_file()

        self.registerLst[32] = self.PC
        self.registerLst[33] = self.Lo
        self.registerLst[34] = self.Hi
        register_writer = DataWriter(self.registerLst,self.out_register_file)
        register_writer.write_bin_file()

    def output_as_out(self):
        with open(self.terminal_out_file,"w") as out_f:
            out_f.write(self.out_terminal_string)
        return


if __name__ == "__main__":

    smt = Simulator("test.txt", "test.asm")
    smt.read_into_memory()
    smt.show_memory()

    smt.execute_prog()
    smt.output_as_out()
    smt.output_as_bin()