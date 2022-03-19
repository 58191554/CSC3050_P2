"""
这个库是用来做.asm的.data阅读器的
他的extract 方法将把读入的data放进memory中
"""


class DataReader:

    def __init__(self, memory:list,  MIPS_code_file = "test.asm", machine_code_file = "test.txt"):
        self.MIPS_code_file = MIPS_code_file
        self.machine_code_file = machine_code_file
        self.memory = memory
        pass
    
    def read_machine_Code(self):
        with open(self.machine_code_file,"r") as mc:          #open the machine code file and read
            self.machine_code_lines = mc.readlines()         #初始化的时候就将机器码文件读入
            mc.close()
            self.text_scale = len(self.machine_code_lines)
        for i in range(len(self.machine_code_lines)):           #将机器码逐行转换成十进制整数
            self.memory[i] = int(self.machine_code_lines[i],2)

        return self.memory


    def get_data_seg(self):        
        print("get_data_seg")
        data_seg = []
        with open(self.MIPS_code_file) as mips:      #打开.asm文件
            txt = mips.readlines()
        
        data_begin_idx = -1
        test_begin_idx = -1
        for i in range(len(txt)):
            line = txt[i]
            if line.find(".data") != -1:        #找到.data标签
                data_begin_idx = i
            if line.find(".text") != -1:        #找到.text标签
                test_begin_idx = i


        if data_begin_idx != -1:                #如果存在.data segment
            if data_begin_idx < test_begin_idx:         #判断.data和.test的相对位置
                data_seg = txt[data_begin_idx:test_begin_idx]
            elif data_begin_idx > test_begin_idx:
                data_seg = txt[test_begin_idx: data_begin_idx]
        
            for i in range(len(data_seg)):
                data_seg:list
                if i < len(data_seg):
                    if data_seg[i] == "":
                        data_seg.pop(i)

        return data_seg

    def delete_comments(self):          #delete all the comment part from the line
        
        data_seg = self.get_data_seg()

        newDataLst = []
        for line in data_seg:

            cmtMark = line.find("#")
            if cmtMark != -1:
                if (cmtMark == 0):
                    continue
                else:
                    line = line[0:line.find("#")]
                    line = line.strip()         #delete redundant space
            newDataLst.append(line)
        # for line in newDataLst:
        #     print(line)
        return newDataLst

    def extract_data(self):     #extract the data in the data_seg and store in a list
        data_seg = self.delete_comments()
        data_list = []          #the target list storine the data 
        int_list = []          #store the bytes in a list每个元素都是2^8大小的
        for i in range(len(data_seg)):
            line = data_seg[i]          #进行每一行data: 指令 的 遍历
            line:str
            
            if line.find(".ascii")!=-1:    #如果这一行是.asciiz类数据或者.ascii

                print("ascii")
                data = line[line.find(" ", line.find(".ascii"))  :]
                data = data.strip()[1:-1]
                

                data_list.append(data)
                print(".asc ",data)
                deci_list = []          #用来存放所有的字符转int，最后加上一个\0
                j = 0
                for j in range(len(data)):
                    if j < len(data):
                        if data[j] == "\\":         #如果是换行符
                            if data[j+1] == "n":
                                char_int = 10
                                data = data[:j+1]+data[j+2:]
                        else:
                            char_int = ord(data[j])
                        deci_list.append(char_int)
                if line.find(".asciiz")!=-1:         
                    deci_list.append(0)             #因为是asciiz所有补上一个0
                if len(deci_list)%4 !=0:        #如果没满4的话就继续补上0
                    deci_list+=[0]*(4 - len(deci_list)%4)
                for group in range(len(deci_list)//4):      #从后往前，使用大端法
                    num = (2**24)*deci_list[4*group+3] + (2**16)*deci_list[4*group+2] +\
                            (2**8)*deci_list[4*group+1]  + deci_list[4*group]        #2^8一个byte也是一个字母
                    int_list.append(num)
                
                
            elif line.find(".word")!=-1:        #将n个32位的数据输入
                data = line[line.find(" ", line.find(".word")) +1 :]
                data_list.append(data)
                print(".word ",data)
                str_list = data.split(",")  #分割
                
                for i in range(len(str_list)):  #将字符串转变成数字
                    int_list.append(int(str_list[i].strip()))

            elif line.find(".byte")!=-1:
                data = line[line.find(" ", line.find(".byte")) +1 :]
                data_list.append(data)
                print(".byte ", data)
                str_list = data.split(",")  #分割
                deci_list = []
                for i in range(len(str_list)):  #将字符串转变成数字
                    deci_list.append(int(str_list[i].strip()))
                if len(deci_list)%4 !=0:        #如果没满4的话就继续补上0
                    deci_list += [0]*(4 - len(deci_list)%4)

                for group in range(len(deci_list)//4):
                    num = (2**24)*deci_list[4*group+3] + (2**16)*deci_list[4*group+2] +\
                            (2**8)*deci_list[4*group+1]  + deci_list[4*group]        #2^8一个byte
                    int_list.append(num)


            elif line.find(".half")!=-1:
                data = line[line.find(" ", line.find(".half")) +1 :]
                data_list.append(data)
                print(".half ", data)
                str_list = data.split(",")
                deci_list = []
                for i in range(len(str_list)):
                    deci_list.append(int(str_list[i].strip()))   #将字符串转变成数字
                if len(deci_list)%2 !=0:        #如果没满4的话就继续补上0
                    deci_list += [0]

                for group in range(len(deci_list)//2):
                    num = (2**16)*deci_list[2*group+1] + deci_list[2*group]        #2^16一个half
                    int_list.append(num)

        # print(int_list)
        for i in range(len(int_list)):              #将读入的data放进memory中
            self.memory[2**18+i] = int_list[i]
            
        # print(self.memory)
        return self.memory


if __name__ == "__main__":
    memoryLst = [0]*(6  *  (2**18))
    dt_reader = DataReader(memory= memoryLst)
    dt_reader.extract_data()
    