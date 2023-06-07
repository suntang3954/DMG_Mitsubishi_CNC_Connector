# DMG MORI SYSTEM: BND-1023W010-E1	MITSUBISHI CNC 730UM-L	I81868C07
from m700 import M700

HOST = '192.168.101.90'
PORT = '683'
ADDR = '10.62.236.125:683'


def workDict():
    return {'200231':1,'200237':2,'200238':3,'280010':4,'220009':5}

def writeProductId(qrcode:str)->int:
    '''
        extract the work type code from QRCODE
        return the Product ID
    '''
    # qrcode = '200238-1:2311379270:D:G601'
    wdict = workDict()
    id = 0
    qrwork = qrcode[:6]
    if qrwork in wdict.keys():
        id = wdict[qrwork]
        return id
    raise Exception('错误的QR信息')
    return id

def communicat():
    mc = M700.get_connection(ADDR)
    status = mc.get_run_status()
    qrcode = ''
    if status != 'RunStatus.AUTO_RUN':
        var = 100
        id = writeProductId(qrcode)
        mc.write_commv(var,0) # product ID
        # val = mc.read_commv(var)
        # print(val)

    # rpm = mc.get_rpm()
    # print(f'转速:{rpm}')
    # 
    mc.close()

def get_info():
    mc = M700(ADDR)
    mc.get_connection(ADDR)
    # pos_x = mc.get_distance(M700.Position.X)
    # pos_y = mc.get_distance(M700.Position.Y)
    # pos_z = mc.get_distance(M700.Position.Z)
    # print(pos_x,pos_y,pos_z)
    # a,b = mc.get_current_prg_block()
    # print(a,b)
    
    p1="M01:\\PRG"
    res=mc.find_dir(p1)
    print(res)
    mc.close()

if __name__ == "__main__":
    get_info()