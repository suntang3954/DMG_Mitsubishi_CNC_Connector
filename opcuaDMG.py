import asyncio
from asyncua import Client, ua
import time

URL = 'opc.tcp://192.168.101.150:4840/'

async def reader_tag(tagaddress)->str:
    '''
    :return: tag value from DMG NLX2500-700 
    '''
    async with Client(url=URL) as client: # 连接DMG 的内置OPC UA服务器
        Client.session_timeout = 200
        nodeobj = client.get_node(tagaddress)
        value = await nodeobj.read_value()
        return value

def tagaddressfinder():
    #ns=2,s=Channel_1-CurrentNcProgram:OR:S
    try:
        tagno = input('''
            please input the number of tagName which you want to select>>>>> \n
            1: 'controllerMode'
            2: 'currentNcProgram'
            3: 'ExecutionState'
            4: 'alarmNumber'
            5: 'alarmMessage'
            6: 'alarmDate'
            7: 'EmergencyStop'
            8: 'PartCounter'
            9: 'FeedOverride'
            10: 'light1color'
            11: 'light1status'
            12: 'light2color'
            13: 'light2status'
            14: 'light3color'
            15: 'light3status'
            16: 'light4color'
            17: 'light4status'
        ''')
    except ValueError:
        print('>>the inputed number is wrong!>>')
    else:
        tagdi = {
            'controllerMode':'ns=2;s=Channel_1-ControllerMode',
            'currentNcProgram':'ns=2;s=Channel_1-CurrentNcProgram',
            'ExecutionState':'ns=2;s=Channel_1-ExecutionState',
            'alarmNumber':'ns=2;s=NumberOfActiveAlarms',
            'alarmMessage':'ns=2;s=Alarms."Alarmnumber"-Message',
            'alarmDate':'ns=2;s=Alarms."Alarmnumber"-Time',
            'EmergencyStop':'ns=2;s=EmergencyStop',
            'PartCounter':'ns=2;s=Channel_1-FeedOverride',
            'FeedOverride':'ns=2;s=PartCounter',
            'light1color':'ns=2;s=LightColor1',
            'light1status':'ns=2;s=LightStatus1',
            'light2color':'ns=2;s=LightColor2',
            'light2status':'ns=2;s=LightStatus2',
            'light3color':'ns=2;s=LightColor3',
            'light3status':'ns=2;s=LightStatus3',
            'light4color':'ns=2;s=LightColor4',
            'light4status':'ns=2;s=LightStatus4'
        }
        if int(tagno) > 17 or int(tagno) < 1:
            raise Exception('>>the inputed number is out of the list>>')
        else:
            values = list(tagdi.values())
            index = int(tagno)-1
            return values[index]

def main():
    tagaddress = tagaddressfinder()
    try:
        res = asyncio.run(reader_tag(tagaddress))
    except Exception as e:
        print(f'error:\n {e}')
    else:
        print(f'the result of {tagaddress} .\n')
        # decode result
        if tagaddress.find('ControllerMode')>0:
            res = {0:'other',1:'auto',2:'MDI',3:'JOG'}.get(res)
        elif tagaddress.find('ExecutionState')>0:
            res = {0:'other',1:'运行中',2:'中断中',3:'等待中'}.get(res)
        else:
            pass
        print(res)

if __name__ == '__main__':
    main()
    time.sleep(3)