from enum import Enum
import time

class M700():
    __ip = None
    __port = None
    __isopen = False
    __ezcom = None

    def __init__(self,host) -> None:
        print(f"new object {host}")

    @classmethod
    def get_connection(cls,host):
        time.sleep(2)
        cls.__isopen = 1
        print('准备与设备进行连接')

    class ProgramType(Enum):
        '''メインorサブプログラム（valueはM700の返される値に対応している）'''
        MAIN = 0
        SUB = 1

    def close(self):
        self.__isopen = 0
        print('closed')
    
    def __str__(self):
        return self.__ip + ":" + self.__port + " " + ("Open" if self.__isopen else "Close")

    def is_open(self):
        '''__open()処理後、接続が開いているか確認する。
        
        Return:
            bool: 接続が開いているならTrue
        '''
        with self.__lock:
            try:
                self.__open()
            except:
                pass
            return self.__isopen
        
    def get_program_number(self,progtype):
        return '200238'
    
    def write_commv(self,var:int,data:float):
        print(f'write {data} into the {var}')
        return 1
    
    def get_tool_life(self,tool_group,tool_no):
        print(f'try to obtain the life count of {tool_no} in {tool_group}.')
        return 1
    

    class RunStatus(Enum):
        '''運転状態（valueはM700の返される値に対応している）'''
        NOT_AUTO_RUN = 0
        AUTO_RUN = 1


    def get_run_status(self):
        return M700.RunStatus.NOT_AUTO_RUN