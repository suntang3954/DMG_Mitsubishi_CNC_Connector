import os, re
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import psutil
import pandas as pd

mask = ()
ipv4 = ()

def get_ip(): 
    with os.popen("ipconfig/all") as res:
        for line in res:
            line = line.strip()
            if line.startswith("IPv4 Address"):
                ipv4 = map(int, re.findall("(\d+)\.(\d+)\.(\d+)\.(\d+)", line)[0])
            elif line.startswith("Subnet Mask"):
                mask = map(int, re.findall("(\d+)\.(\d+)\.(\d+)\.(\d+)", line)[0])
                break
    net_segment = ".".join([str(i & j) for i, j in zip(ipv4, mask)]).strip(".0")
    print(f'result:  {net_segment}\n')
    return net_segment


# 清空映射表
def clear_arplist():
    os.system("arp -d *")
    print('映射表清空完毕....')

# ping 局域网内所有设备
def ping_all_device(net_segment):
    for i in range(1,255,1):
        os.system(f"ping -w 1 -n 1 {net_segment}.{i}")

# 加速ping 版本:
def ping_all_device_faster(net_segment):
    with ThreadPoolExecutor(max_workers=5) as executor:
        for i in range(1,255,1):
            executor.submit(os.system, f"ping -w 1 -n 1 {net_segment}.{i}")

def ping_all_device_best(net_segment):

    # 逻辑cpu个数
    count = psutil.cpu_count()
    with ProcessPoolExecutor(count) as executor:
        for i in range(1, 255):
            executor.submit(os.system, f"ping -w 1 -n 1 {net_segment}.{i}")

# 获取当前在线设备ip 和 Mac 地址
def get_online_mac_ip():
    header = None
    with os.popen("arp -a") as res:
        for line in res:
            line = line.strip()
            if not line or line.startswith("接口"):
                continue
            if header is None:
                header = re.split(" {2,}", line.strip())
                break
        df = pd.read_csv(res, sep=" {2,}", names=header, header=0, engine='python')

    print(df.shape)
    df.head()

if __name__ == "__main__":
    
    # res = get_ip()
    # clear_arplist()
    # ping_all_device_faster(res)
    get_online_mac_ip()