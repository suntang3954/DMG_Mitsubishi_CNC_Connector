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
                            ->SAMS 读取后将result.txt,startwork.txt文件删除,
'''
from m7700 import M700
# host = '10.62.236.125:683'
from os import path,remove
import time
import asyncio

start_file_loop = 1 #默认不断的重复确认是否可以启动，当发现有启动文件'startwork.txt'后，重置为0，程序加工完成后重置为1
wait_QR_loop = 1 # 默认不断的重复确认是否有QR 文件,当发现有'nxl2500_connector_tag.txt'是重置为0,程序加工完成后重置为1

# 对接文件的主目录
root = '.'
works = ['200231','200237','200238','220009','280010']
qr = ''
path_prg = ''
path_result = path.join(root,'result.txt')
con_file = path.join(root,'nxl2500_connector_tag.txt')
start_file = path.join(root,'startwork.txt')

class DMGoperation():
    def __init__(self):
        self.host = '10.62.236.125:683'
        self._con_key = 0
        self.conn = object
        self._prg_no = ''
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
        if self._con_key == 1:
            self._con_key = 0
            self.conn.close()
        print(f'{self.host} has been closed..')

    # 输出设备当前的机种信息
    def current_program_No(self)->bool:
        '''当前的程序名,执行后程序名会存储在对象的_prg_no中'''
        if self._con_key == 1:
            try:
                self._prg_no = self.conn.get_program_number(M700.ProgramType.MAIN)
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
        '''设置程序启动的标识变量的值'''
        sta = self.conn.get_run_status()
        # 如果设备在运行中
        if sta:
            try:
                print('准备写入参数')
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
    
    # 得到刀具寿命
    def get_toollife(self):
        '''得到当前刀具寿命的清单'''
        lifes = []
        for i in range(1,13,1):
            tool_life = self.conn.get_tool_life(i,i)
            lifes.append(tool_life)
        first_tool = []
        for i in range(len(lifes)):
            if lifes[i] == '1':
                first_tool.append(i+1)
        if len(first_tool):
            return 1,first_tool
        else:return 0,[]
    
    # 设备的状态
    def machine_status(self)->bool:
        '''获得当前设备的运行状态，启动中返回0，停止中返回1'''
        sta = self.conn.get_run_status()
        if sta: 
            return 0
        else:
            return 1 

# 创建对接文件
def gen_file(filename,arg):
    '''一个创建文件的模板'''
    if not path.exists(filename):
        with open(filename,'w') as f:
            f.write(arg)

# 查看是否有QR 输入
def connect_file():
    ''' SAMS希望连接的标识，约定的文件路径及文件名是否存在'''
    return path.exists(con_file)

# 写入当前程序名
def write_current_prg_no(current_no):
    '''写入当前设备侧的程序名到文件中'''
    current_prg_file = current_no + '.txt'
    t_now = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
    gen_file(current_prg_file,arg=f'{t_now}\n{current_prg_file}')

# 确认启动许可是否存在
def is_start():
    '''判断SAMS是否允许启动文件存在'''
    file = path.join(root,'startwork.txt')
    return path.exists(file)

# 如果可以启动，执行QR的确认动作
def confirm_qr()->int:
    '''确认启动文件中的产品类型，根据产品类型返回整数ID值'''
    global qr
    '''根据传送过来的QR CODE, 返回对应的ID'''
    file = path.join(root,'startwork.txt')
    with open(file,'r') as f:
        qr = f.read().strip()
        if qr in works:
            return works.index(qr)
        else:
            return -1

# 删除本次对接的文件
def init():
    '''删除本次对话的文件'''
    global path_prg,path_result
    if path.exists(path_prg):
        remove(path_prg)
    if path.exists(path_result):
        remove(path_result)
    qr = ''
    start_file_loop = 1
    wait_QR_loop = 1

# 框架
def main():
    try:
        while 1:
            if connect_file():
                dmg = DMGoperation()
                dmg.connect()
                dmg.current_program_No()
                current_prg_no=dmg._prg_no
                write_current_prg_no(current_prg_no)
                # wait start single from SAMS
                time.sleep(1)
                if is_start():
                    id = confirm_qr()
                    if dmg.set_status_on(id):
                        print('the machine has been allowed to start!')
                    time.sleep(5)
                    if dmg.machine_status:
                        _is, new_tools = dmg.get_toollife()
                        if _is: # 有初品刀具
                            arg = f'{qr}:新刀具清单:{new_tools}'
                        else:
                            arg = f'{qr}:没有交换新刀'
                        gen_file(path_result,arg=arg)
                        remove(con_file)
                        remove(start_file)
                        dmg.close()
            else:
                time.sleep(2)
                init()
        dmg.close()
    except KeyboardInterrupt:
        print('exit')
    
main()