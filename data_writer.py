from instruction import twos_tansfer
class DataWriter:

    def __init__(self, memory_int_lst, out_mem_file = "default_test_out.bin"):
        self.int_lst = memory_int_lst
        self.out_mem_file = out_mem_file

    def write_bin_file(self):       #read the machine code and return a byte list used to write .bin file
        
        bytes_lst = []              #store bytes in a listS

        with open(self.out_mem_file,'wb') as mem_bin:
            print("\n"+"*"*40+"START WRITING..."+"*"*40)
            for num in self.int_lst:
                if num<0:   bin_info = twos_tansfer(bin(-num))
                else:       bin_info = bin(num)[2:]
                line = "0"*(32-len(bin_info)) + bin_info
                lineList = []           #every line list has 4 int
                for i in range(4):
                
                    num = int(line[8*i:8*i+8],2)
                    twoList = [num]
                    lineList = twoList + lineList

                a = bytes(lineList)
                bytes_lst.append(a)

                mem_bin.write(a)            #此处也可以不写入
            mem_bin.close()
        print("\n"+"*"*40+"WRITING FINISHD..."+"*"*40)
        return bytes_lst
    

    
if __name__ == "__main__":
    pass