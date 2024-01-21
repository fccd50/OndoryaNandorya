import time
from threading import Thread 
from threading import Semaphore 
import sys
import os
#from urllib.parse import ParseResult
import PySimpleGUI as sg
import rs232
import frontgui

class Main:
  serial = rs232.RS232C()
  gui = frontgui.Guidget()
  sg.theme("Gray Gray Gray")
  ports_list = serial.getCOMPorts()
  connected = False
  data_pv = []
  data_sv = []
  sema = Semaphore(1)
  in_weighing_tab = True
  not_data_taking = True
  # ウィンドウオブジェクトの作成
  window = gui.get_window(ports_list)
  def start(self):
    while True:
        # イベントの読み込み
        event, values = self.window.read(timeout=3000, timeout_key="-timeout-")
        # ウィンドウの×ボタンが押されれば終了
        if event == sg.WIN_CLOSED or event == '-QUIT-':
          if self.connected:
            self.serial.disconnect()
          self.window.close()
          sys.exit()
        elif event == "-tab-":
            selected_tab = values["-tab-"]
            # print(selected_tab)
            if selected_tab == "-adjust_tab-":
              self.in_weighing_tab = True
            else:
              self.in_weighing_tab = False
        elif event == '-connect-':
          com_num = values['-ports-'].split()[0]
          if self.serial.connect(com_num):
            self.connected = True
            self.window["-status-"].update("接続OK") 
        elif event == '-temp-' and values["-temp-"] and values["-temp-"][-1] not in ('0123456789.-'):
          self.window["-temp-"].update(values['-temp-'][:-1])
        elif event == '-hum-' and values["-hum-"] and values["-hum-"][-1] not in ('0123456789.-'):
          self.window["-hum-"].update(values['-hum-'][:-1])
        elif event == '-pres-' and values["-pres-"] and values["-pres-"][-1] not in ('0123456789.-'):
          self.window["-pres-"].update(values['-pres-'][:-1])
        elif event == '-k-' and values["-k-"] and values["-k-"][-1] not in ('0123456789.-'):
          self.window["-k-"].update(values['-k-'][:-1])
        elif event == "-timeout-":
          if self.connected and self.in_weighing_tab and self.not_data_taking:
            Thread(target=self.get_THPK, args=(self.sema,),daemon=True).start()
          self.window["-time-"].update(time.strftime('%Y-%m-%d %H:%M:%S'))
        elif event == "-adjust-":
          if self.connected:
            t = values["-temp-"]
            h = values["-hum-"]
            p = values["-pres-"]
            k = values["-k-"]
            Thread(target=self.adjust, args=(t,h,p,k,self.sema), daemon=True).start()
        elif event == "-set-":
          if self.connected:
            Thread(target=self.setrom, args=(self.sema,), daemon=True).start()
        elif event == "-timeset-":
          if self.connected:
            Thread(target=self.timeset, args=(self.sema,), daemon=True).start()
        elif event == "-getData-":
          if self.connected:
            self.not_data_taking = False
            Thread(target=self.showdata, args=(self.sema,), daemon=True).start()
        elif event == "-ssidOK-":
          if self.connected:
            Thread(target=self.setssid, args=(self.sema,values["-ssid-"], values["-paswd-"]), daemon=True).start()
        elif event == "-savedata-":
          if self.connected and len(values["-datafield-"]) != 0:
            filename = time.strftime('%Y%m%d_%H%M%S') + "ONDORYA.csv"
            f = open(os.path.join(os.getcwd(),filename),"w")
            # print(os.path.join(os.getcwd(),filename))
            f.write(values["-datafield-"])
            f.close()     
        elif event == "-deldata-" :
          if self.connected:
            v = sg.popup_ok_cancel("SDカード内データ消していい？",keep_on_top=True, modal=True)
            if v=="OK":
              Thread(target=self.deldata, args=(self.sema,), daemon=True).start()
        elif event == "-reset-":
          if self.connected:
            self.reset()

  def reset(self):
    self.serial.send_command(bytes("reset" + "\r\n", encoding='utf-8', errors='replace'))

  def setssid(self, sema, ssid, pawd):
    with sema:
      self.serial.send_command_with_return(bytes("setSSID " + ssid + "\r\n", encoding='utf-8', errors='replace'))
      self.serial.send_command_with_return(bytes("setPSWD " + pawd + "\r\n", encoding='utf-8', errors='replace'))
      temp = self.serial.send_command_with_return(b"updateOffSetALL\r\n")
      self.window["-ssidres-"].update(temp)

  def deldata(self, sema):
    with sema:
      self.serial.send_command_with_return(b"clearData\r\n")

  def showdata(self, sema):
    with sema:
      self.serial.send_command(b"getData\r\n")
      while True:
        s = self.serial.read_line_().decode('utf8')
        if s == "":
          self.not_data_taking = True
          break
        self.window["-datafield-"].print(s.rstrip())

  def timeset(self, sema):
    pass
    # with sema:
    #   y = time.strftime("%Y")
    #   m = time.strftime("%m")
    #   d = time.strftime("%d")
    #   h = time.strftime("%H")
    #   M = time.strftime("%M")
    #   s = time.strftime("%S")
    #   self.serial.send_command_with_return(bytes("setDateTime "+y+","+m+","+d+","+h+","+M+","+s+"\r\n", encoding='utf-8', errors='replace'))
    # self.setrom(sema)

  def setrom(self,sema):
    with sema:
      self.serial.send_command_with_return(b"updateOffSetALL\r\n")
      self.serial.send_command_with_return(b"getOffSets\r\n")

  def adjust(self,t,h,p,k, sema):
    with sema:
      self.data_sv = [float(t),float(h),float(p),float(k)]
      read = self.serial.send_command_with_return(b"getOffSets\r\n")
      print ("getOffsets")
      print(read)
      offsetdata = [float (a) for a in read.split()]
      newoffset = [self.data_sv[i] - self.data_pv[i] + offsetdata[i] for i in range(4) if self.data_pv[i] != 0.0]
      # print(self.window["check_T"].get())
      if(self.window["check_T"].get()):
        self.serial.send_command_with_return(bytes("offSetT " + f'{newoffset[0]:.1f}' + "\r\n", encoding='utf-8', errors='replace'))
      if(self.window["check_H"].get()):
        self.serial.send_command_with_return(bytes("offSetH " + f'{newoffset[1]:.1f}' + "\r\n", encoding='utf-8', errors='replace'))
      if(self.window["check_P"].get()):
        self.serial.send_command_with_return(bytes("offSetP " + f'{newoffset[2]:.1f}' + "\r\n", encoding='utf-8', errors='replace'))
      if(self.window["check_K"].get()):
        self.serial.send_command_with_return(bytes("offSetK " + f'{newoffset[3]:.1f}' + "\r\n", encoding='utf-8', errors='replace'))

  def get_THPK(self, sema):
    with sema:
      read = self.serial.send_command_with_return(b"getTHPK\r\n")
      print ("get_THPK")
      print (read)
      try:
        self.data_pv = [float(a) for a in read.split()]
        self.window["-temppv-"].update(self.data_pv[0])
        self.window["-humpv-"].update(self.data_pv[1])
        self.window["-prespv-"].update(self.data_pv[2])
        self.window["-kpv-"].update(self.data_pv[3])
        if ( self.data_pv[0]==0.0 or self.data_pv[1]==0.0 or self.data_pv[3]==0.0):
          self.window['-adjust-'].update( disabled = True )
        else:
          self.window['-adjust-'].update( disabled = False )
      except:
        self.window["-temppv-"].update("0.0")
        self.window["-humpv-"].update("0.0")
        self.window["-prespv-"].update("0.0")
        self.window["-kpv-"].update("0.0")
        self.window['-adjust-'].update( disabled = True )

if __name__ == '__main__':
  main = Main()
  main.start()
