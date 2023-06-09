'''
    为了与SAMS 通讯,如下方式实施;
    1.确认SAMS的通讯可特征, 此特征为读取本地一个文件'nxl2500_connector_tag.txt',确认值是否为1 
                            -> SAMS 侧设定延时,如果3sec没有收到数据,则反馈通讯异常;
        2. 执行读取当前DMG设备的程序名,并生成'{程序名}'.txt 的文件.文件内容:'{当前时间}\n{程序名}'; 
                            -> SAMS 3sec内读取到此文件后,判断为通讯开始,并返回是否可以开始加工,如果可以加工,删除'{程序名}.txt'文件,则输出'startwork.txt'文件,内容为:产品代号
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

sams_connect = 0 
write_completed = 0 # 当为1时,不会再重复写入设备内部参数
get_toollife_completed = 0 # 当为1时不会再次读取刀具寿命

# 对接文件的主目录
root = '.'
works_dict = {'200231':'800121','200237':'800110','200238':'200116','220009':'810013','280010':'800111'}
work_id = {'200231':1,'200237':2,'200238':3,'220009':4,'280010':5}
path_prg = ''
path_result = path.join(root,'result.txt')
con_file = path.join(root,'nxl2500_connector_tag.txt')
start_file = path.join(root,'startwork.txt')
t_now = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
error_file = path.join(root,f'{t_now}_error.txt')

class DMGoperation():
    def __init__(self):
        self.host = '10.62.236.125:683'
        self._con_key = 0
        self.conn = object
        self._prg_no = ''
        self.para_no = 199 # 设备侧#199宏变量用于定义机种对应的ID
        self._work = 198
        self._sequence = 197
    
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
    def set_status_on(self,workID:float,work_type,sequence)->bool:
        '''设置程序启动的标识变量的值'''
        # sta = self.conn.get_run_status()
        # 如果设备在运行中
        global write_completed
        if not write_completed:
            if not self.machine_status():
                try:
                    print('准备写入参数')
                    self.conn.write_commv(self.para_no,workID)#写入机种ID
                    self.conn.write_commv(self._work,work_type)#写入QR中机种的型号部分
                    self.conn.write_commv(self._sequence,sequence)#写入QR中sequence部分
                except:
                    print('conncet with DMG error occurred!')
                    return False
                else:
                    print(f'{self.para_no} 写入值:{workID}')
                    print(f'{self._work} 写入值:{work_type}')
                    print(f'{self._sequence} 写入值:{sequence}')
                    return True
            else:
                print('the machine is running!...')
                return False
        else:
            return True
    
    # 得到刀具寿命
    def get_toollife(self):
        '''得到当前刀具寿命的清单'''
        global get_toollife_completed
        if not get_toollife_completed:
            lifes = []
            for i in range(1,13,1):
                tool_life = self.conn.get_tool_life(i,i)[2]
                lifes.append(tool_life)
            first_tool = []
            for i in range(len(lifes)):
                if lifes[i] == '1':
                    first_tool.append(i+1)
            if len(first_tool):
                return 1,first_tool
            else:return 0,[]
        else:
            return 0,[]
    

    # 设备的状态
    def machine_status(self)->bool:
        '''获得当前设备的运行状态，启动中返回1，停止中返回0'''
        sta = self.conn.get_run_status()
        if sta.value: 
            return 1
        else:
            return 0 

# 创建对接文件
def gen_file(filename,arg):
    '''一个创建文件的模板'''
    if not path.exists(filename):
        with open(filename,'w') as f:
            f.write(arg)

# 查看是否有QR 输入
def connect_file():
    ''' SAMS希望连接的标识，约定的文件路径及文件名是否存在'''
    global sams_connect
    sams_connect = 1
    return path.exists(con_file)

# 写入当前程序名
def write_current_prg_no(current_no):
    '''写入当前设备侧的程序名到文件中'''
    current_prg_file = current_no + '.txt'
    
    gen_file(current_prg_file,arg=f'{t_now}\n{current_prg_file}')

# 确认启动许可是否存在
def is_start():
    '''判断SAMS是否允许启动文件存在'''
    file = path.join(root,'startwork.txt')
    return path.exists(file)

# 如果可以启动，执行QR的确认动作
def confirm_qr()->tuple:
    '''确认启动文件中的产品类型，根据产品类型返回整数ID值
        QR实例:200238-1:2315779410:D:G601
        返回:产品ID,产品编号,产品的sequence
    '''
    '''根据传送过来的QR CODE, 返回对应的ID'''
    file = path.join(root,'startwork.txt')
    with open(file,'r') as f:
        try:
            context = f.read().strip().split(':')
            work_type = context[0][0:6]
            sequence = context[1]
        except:
            print('QR 错误')
            return 0,0,0
        else:
            if work_type in works_dict:
                return work_id[work_type],work_type,sequence
            else:
                return 0,0,0

# 删除本次对接的文件
def init():
    '''删除本次对话的文件'''
    global path_prg,path_result,write_completed,get_toollife_completed,sams_connect
    sams_connect = 0
    if path.exists(path_prg):
        remove(path_prg)
    if path.exists(path_result):
        remove(path_result)
    if path.exists(error_file):
        remove(error_file)
    write_completed = 0
    get_toollife_completed = 0


# 框架
def main():
    global write_completed,get_toollife_completed
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
                    id,work_type,sequence = confirm_qr()
                    if id:
                        if dmg.set_status_on(id,work_type,sequence):
                            write_completed = 1
                            print('the machine has been allowed to start!')
                            time.sleep(5)
                            if dmg.machine_status():
                                _is, new_tools = dmg.get_toollife()
                                if _is: # 有初品刀具
                                    arg = f'{sequence}:新刀具清单:{new_tools}'
                                else:
                                    arg = f'{sequence}:没有交换新刀'
                                gen_file(path_result,arg=arg)
                                remove(con_file)
                                remove(start_file)
                                dmg.close()
                        else:
                            print('the machine is not stop, it can not write parameter')
                    else:
                        # 抛出错误异常
                        gen_file(error_file,f'QR code 错误{id},{work_type},{sequence}')

            else:
                time.sleep(2)
                init()
        dmg.close()
    except KeyboardInterrupt:
        print('exit')

if __name__ == "__main__":
    main()