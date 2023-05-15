from tkinter import *
from tkinter import scrolledtext, messagebox
from testObject import TestObject
import time

class DMGoperator():
    def __init__(self,name):
        self._name = name
        self.product_ids = ['200231','200237','200238','220009','280010']
        # the status about connecting with machine, 0:disconnecting;1:connecting
        self._key = 0
        self._key_exe = 0
        self.nc_sn = ''
        self._mc = TestObject()
        self.root = Tk()

        self.root.geometry('640x640')
        self.root.title(self._name)

        self.sta = StringVar(name='连接状态') # connecting or disconnected
        self.exe_sta = StringVar(name='执行状态')#success or failure
        self.prg = StringVar(name='currentPrg')
        self.prg_no = StringVar(name='PrgNo',value='200237')
        self.prgsequence = StringVar(name='PrgSequence',value='n100')
        
        self.la_abs_x,self.la_abs_y,self.la_abs_z = StringVar(),StringVar(),StringVar()
        self.la_ori_x,self.la_ori_y,self.la_ori_z = StringVar(),StringVar(),StringVar()
        self.la_res_x,self.la_res_y,self.la_res_z = StringVar(),StringVar(),StringVar()
        # 容器汇总
        self.top_frame = Frame(self.root,width=640,height=440)
        self.bot_frame = Frame(self.root,width=640,height=200)
        self.top_frame_left = Frame(self.top_frame,width=440)
        self.info_frame = LabelFrame(self.top_frame_left,background='gray',fg='black',font='黑体',text='Machine Connection Information')
        self.info_frame_left = Frame(self.info_frame)
        
        self.prg_frame = LabelFrame(self.top_frame,background='gray',fg='black',font='黑体',text='current Programe Status',width=200)
        self.prg_frame_con = LabelFrame(self.prg_frame,text='current program context')
        self.prg_frame_bot = Frame(self.prg_frame)

        self.pos_frame = LabelFrame(self.top_frame_left,background='gray',fg='black',font='黑体',text='Position realtime')
        self.pos_frame_abs = LabelFrame(self.pos_frame,background='gray',fg='black',font='黑体',text='ABS Position')
        self.pos_frame_ori = LabelFrame(self.pos_frame,background='gray',fg='black',font='黑体',text='G53 Pos')
        self.pos_frame_res = LabelFrame(self.pos_frame,background='gray',fg='black',font='黑体',text='Residual')

        self.frame_log = LabelFrame(self.bot_frame,background='gray',fg='black',font='黑体',text='Run Log',width=320)
        self.frame_err = LabelFrame(self.bot_frame,background='gray',fg='black',font='黑体',text='Error Code',width=320)
        self.status_frame = LabelFrame(self.info_frame,text='Status')
        # button
        self.con_btn = Button(self.info_frame_left,text='Connect',activebackground='green',activeforeground='blue',command=self._connect)
        self.exe_btn = Button(self.info_frame_left,text='Execute',activebackground='yellow',activeforeground='red',height=2,command=self.execute)

        #标签汇总
        Label(self.info_frame_left,text='Machine Host/IP',font=5).grid(column=0,row=0,padx=2,sticky=W)
        Label(self.info_frame_left,text='NC TYPE',font=5).grid(column=0,row=1,padx=2,sticky=W)
        Label(self.info_frame_left,text='Time Out Value',font=5).grid(column=0,row=2,padx=2,sticky=W)
        Label(self.info_frame_left,text='Sys Series/ Name',font=5).grid(column=0,row=3,padx=2,sticky=W)
        Label(self.info_frame_left,text='Prodcut QRcode', font=5).grid(column=0,row=4,padx=2,sticky=W)
        self.la_status_run = Label(self.status_frame,text='待连接')
        self.la_status_exe = Label(self.status_frame,text='待执行')
        # Position
        Label(self.pos_frame_abs,text='X',font=('黑体',30,'bold')).grid(row=0,column=0,sticky=W)
        Label(self.pos_frame_abs,text='Y',font=('黑体',30,'bold')).grid(row=1,column=0,sticky=W)
        Label(self.pos_frame_abs,text='Z',font=('黑体',30,'bold')).grid(row=2,column=0,sticky=W)
        
        Label(self.pos_frame_ori,text='X',font=20).grid(column=0,row=0,sticky=W)
        Label(self.pos_frame_ori,text='Y',font=20).grid(column=0,row=1,sticky=W)
        Label(self.pos_frame_ori,text='Z',font=20).grid(column=0,row=2,sticky=W)

        Label(self.pos_frame_res,text='X',font=15).grid(column=0,row=0,sticky=W)
        Label(self.pos_frame_res,text='Y',font=15).grid(column=0,row=1,sticky=W)
        Label(self.pos_frame_res,text='Z',font=15).grid(column=0,row=2,sticky=W)
        # Programe
        Label(self.prg_frame_bot,text='Programe No',bg='#e4c8b1',justify='left').grid(column=0,row=0,padx=5,pady=2)
        Label(self.prg_frame_bot,text='Sequence',bg='#e4c8b1',justify='left').grid(column=0,row=1,padx=5,pady=2)
        Label(self.prg_frame_bot,text=self.prg_no.get(),bg='#e4c8b1',width=20).grid(column=1,row=0,padx=5,pady=2)
        Label(self.prg_frame_bot,text=self.prgsequence.get(),bg='#e4c8b1',width=20).grid(column=1,row=1,padx=5,pady=2)

        self.cur_prg_con = Text(self.prg_frame_con,bg='#e4c8b1')
        Label(self.info_frame_left,text='M730UM',width=17).grid(column=1,row=1,padx=2)#type input
        self.ent_timeout = Entry(self.info_frame_left,bg='#e4c8b1')
        Label(self.info_frame_left,text='',width=17).grid(column=1,row=3,padx=2)#series input
        self.qr_ent=Entry(self.info_frame_left,bg='#e4c8b1')
        self.qr_ent.bind('<Return>',func=self._write)
        self.ip_ent = Entry(self.info_frame_left,bg='#e4c8b1') # ip input
        
        self.pos_frame_abs.rowconfigure(1,weight=1)
        Entry(self.pos_frame_abs,textvariable=self.la_abs_x,bg='#e4c8b1',font=('黑体',30,'bold'),width=10).grid(row=0,column=1,sticky=E,padx=2)
        Entry(self.pos_frame_abs,textvariable=self.la_abs_y,bg='#e4c8b1',font=('黑体',30,'bold'),width=10).grid(row=1,column=1,sticky=E,padx=2)
        Entry(self.pos_frame_abs,textvariable=self.la_abs_z,bg='#e4c8b1',font=('黑体',30,'bold'),width=10).grid(row=2,column=1,sticky=E,padx=2)
        Entry(self.pos_frame_ori,textvariable=self.la_ori_x,bg='#e4c8b1',font=('黑体',20,'bold'),width=10).grid(row=0,column=1,sticky=E,padx=2)
        Entry(self.pos_frame_ori,textvariable=self.la_ori_y,bg='#e4c8b1',font=('黑体',20,'bold'),width=10).grid(row=1,column=1,sticky=E,padx=2)
        Entry(self.pos_frame_ori,textvariable=self.la_ori_z,bg='#e4c8b1',font=('黑体',20,'bold'),width=10).grid(row=2,column=1,sticky=E,padx=2)
        Entry(self.pos_frame_res,textvariable=self.la_res_x,bg='#e4c8b1',font=('黑体',20,'bold'),width=10).grid(row=0,column=1,sticky=E,padx=2)
        Entry(self.pos_frame_res,textvariable=self.la_res_y,bg='#e4c8b1',font=('黑体',20,'bold'),width=10).grid(row=1,column=1,sticky=E,padx=2)
        Entry(self.pos_frame_res,textvariable=self.la_res_z,bg='#e4c8b1',font=('黑体',20,'bold'),width=10).grid(row=2,column=1,sticky=E,padx=2)

        self.log_data_Text = Text(self.frame_log,bg='#e4c8b1')
        self.erro_data_Text = Text(self.frame_err,bg='#e4c8b1')
        # self.log_data_Text = Text(self.bot_frame,bg='#e4c8b1')
        # self.erro_data_Text = Text(self.bot_frame,bg='#e4c8b1')

        # 位置定义
        self.ip_ent.grid(column=1,row=0,padx=3)
        self.con_btn.grid(column=4,row=0,padx=3)
        self.exe_btn.grid(column=4,row=2,padx=3)

        self.top_frame.pack(side=TOP,fill='x')
        self.bot_frame.pack(side=TOP,fill='x')
        self.top_frame.pack_propagate(0)
        self.bot_frame.pack_propagate(0)
        self.top_frame_left.pack(side='left',fill='y')
        self.top_frame_left.pack_propagate(0)
        self.prg_frame.pack(side='left',fill='y')
        self.prg_frame.pack_propagate(0)
        # program
        self.prg_frame_con.pack(side='top',pady=1)
        self.prg_frame_bot.pack(side='bottom',fill='both')
        self.cur_prg_con.pack(fill='both')
        # top_frame_left
        self.info_frame.pack(side='top',padx=1,pady=1,fill='x')
        self.info_frame_left.pack(side='left',padx=2)
        self.ent_timeout.grid(column=1,row=2,padx=2)#timeout input
        self.qr_ent.grid(column=1,row=4,padx=2)# QRcode
        self.status_frame.pack(side='right',padx=3,fill='y')
        self.la_status_run.grid(column=0,row=0,padx=1,pady=1)
        self.la_status_exe.grid(column=0,row=1,padx=1,pady=1)
       
        self.pos_frame.pack(side='top',padx=2,pady=2,fill='x')
        
        self.pos_frame_abs.pack(side='left',fill='y')
        self.pos_frame_ori.pack(side='top',fill='x')
        self.pos_frame_res.pack(side='top',fill='x')
        self.pos_frame_abs.pack_propagate(0)
        self.pos_frame_ori.pack_propagate(0)
        self.pos_frame_res.pack_propagate(0)

        self.frame_log.pack(side='left',fill='y')
        self.frame_err.pack(side='left',fill='y')
        
        self.frame_log.pack_propagate(0)
        self.frame_err.pack_propagate(0)
        
        self.log_data_Text.pack()
        self.erro_data_Text.pack()

        # self.log_data_Text.grid(column=0,row=0,sticky=W)
        # self.erro_data_Text.grid(column=1,row=0,sticky=E)

        self.root.mainloop()
    #获取当前时间
    def get_current_time(self):
        current_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        return current_time
        
    def _connect(self):
        if self.con_btn['text'] == 'Connect'or self.con_btn['text'] == '':
            try:
                self._mc.connect()
            except Exception as e:
                self.erro_data_Text.insert(END,f'{str(self.get_current_time())} 无法连接到设备.\n') 
            else:
                self._key = 1
                self.con_btn.config(text='Disconnect',bg='gray')
                self.la_status_run.config(bg='green',text='连接中')
                self.log_data_Text.insert(END,f'{str(self.get_current_time())} 设备连接成功.\n')
        else:
            self._mc.close()
            self._key = 0
            self.la_status_run.config(text='断开',bg='red')
            self.la_status_exe.config(text='停止',bg='yellow')
            self.log_data_Text.insert(END,f'{str(self.get_current_time())} 设备断开成功.\n')
    # 判断输入的QR code 的产品信息
    def _getqr(self):
        res = ''
        for id in self.product_ids:
            if id in self.qr_ent.get():
                res = id
        return res
        
    # 读取设备的状态，位置等信息              
    def _read(self):
        # series number:
        # x,y,z abs position
        # xyz G53 position
        # xyz residual distance
        # current programe number
        # current programe block number
        # current programe 
        # machine error
        print('read data from mc.')
    # 写入产品ID至宏变量
    def _write(self,keyinfo):
        if self._key == 1 and self._key_exe == 1:
            if self._getqr() == '':
                messagebox.showerror(title='读取QR 异常',message='扫描的信息不在本站产品库中!')
            else:
                print(self._getqr())
                self.log_data_Text.insert(END,f'{str(self.get_current_time())} write data to machine.\n')  
        else:
            messagebox.showerror(title='写入变量异常',message='连接状态异常,无法写入产品型号。')
    # 按钮执行的对应功能
    def execute(self):
        if self.exe_btn['text'] == 'Execute'or self.exe_btn['text'] == '':
            self._key_exe = 1
            self.update()
            self.exe_btn.config(text='Stop',bg='gray')
            self.con_btn.config(state='disabled')
            self.la_status_exe.config(bg='green',text='读写中')
            self.log_data_Text.insert(END,f'{str(self.get_current_time())} 读/写执行中.\n')
        else:
            self._key_exe = 0
            self.con_btn.config(state='active')
            self.exe_btn.config(text='Execute')
            self.la_status_exe.config(bg='yellow')
            self.la_status_exe.config(text='停止')
            self.log_data_Text.insert(END,f'{str(self.get_current_time())} 停止读写.\n')
    # 实现后台刷新
    def update(self):
        if self._key and self._key_exe:
            try:
                self._read()
            except Exception as e:
                print(e)
            self.root.after(1000,self.update)
        else:
            self.erro_data_Text.insert(END,f'{str(self.get_current_time())} 连接设备停止.\n') 

if __name__ == "__main__":
    dmg = DMGoperator('Danfoss Radial Bearing Machining Process')

    
