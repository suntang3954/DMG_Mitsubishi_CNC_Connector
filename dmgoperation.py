'''
    为了与SAMS 通讯,如下方式实施;
    1.确认SAMS的通讯可特征, 此特征为读取本地一个文件'nxl2500_connector_tag.txt',确认值是否为1 
                            -> SAMS 侧设定延时,如果3sec没有收到数据,则反馈通讯异常;
        2. 执行读取当前DMG设备的程序名,并生成'{程序名}'.txt 的文件.文件内容:'{当前时间}\n{程序名}'; 
                            -> SAMS 3sec内读取到此文件后,判断为通讯开始,并返回是否可以开始加工,如果可以加工,则输出'startwork.txt'文件,内容为:产品代号
                            '200237','200231'...
            3.  while true: 如果发现startwork.txt 文件, 读取文件中产品代号;既可以将设备中#199 赋值,程序启动有效. 否认则一直等待;
                #100 赋值对照表:200231:1,200237:2;200238:3,220009:4,280010:5

            4. 设备加工完毕后,NC中自动将#199=0,程序创建'result.txt'文件,返回当前刀具的寿命等参数.
'''
from m700 import M700
# host = '10.62.236.125:683'

class DMGoperation():
    def __init__(self):
        self.host = '10.62.236.125:683'
        self._con_key = 0
        self.conn = object
        self.current_prg_no = ''
        self.para_no = 199 # 设备侧#199宏变量用于定义机种对应的ID
    def connect(self):
        mc = M700(self.host)
        try:
            mc.get_connection(self.host)
        except Exception as e:
            print('Connection Error with DMG CNC..')
            return False
        else:
            self._con_key = 1
            self.conn = mc
            return True
    
    def close(self):
        self._con_key = 0
        self.conn.close()
        print(f'{self.host} has been closed..')

    # 输出设备当前的机种信息
    def current_program_No(self)->bool:
        if self._con_key == 1:
            try:
                self.current_prg_no = self.conn.get_program_number(M700.ProgramType.MAIN)
            except Exception as e:
                print('读取当前程序号异常')
                return 0
            else:
                return 1
        else:
            print('当前没有连接到设备')
            return 0
    
    # 执行写入和读取设备信息
    def set_status_on(self,workID:float)->bool:
        sta = self.conn.get_run_status()
        # 如果设备在运行中
        if sta == "NOT_AUTO_RUN":
            try:
                self.conn.write_commv(self.para_no,workID)
            except:
                print('conncet with DMG error occurred!')
                return False
            else:
                print(f'{self.para_no} 写入值:{workID}')
                return True
        else:
            print('the machine is running!...')
            return False
        