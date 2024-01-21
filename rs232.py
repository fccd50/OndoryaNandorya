import serial.tools.list_ports
import serial

class RS232C:
    def __init__(self) :
        pass

    def getCOMPorts(self):
        return [ports.device + " " + ports.description for ports in serial.tools.list_ports.comports()]
        '''
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            yield p.device
        '''
    def connect(self, comport):
        try:
            # self.seri.setDTR(False)
            self.seri = serial.Serial(comport,9600) #, dsrdtr=True)
            self.seri.timeout=30
            self.seri.set_buffer_size = 25
            return True
        except:
            return False
    
    def disconnect(self):
        try:
            if (self.seri.isOpen) :
                self.seri.close()
        except:
            pass 

    def send_command(self, command):
        self.seri.write(command)

    def send_command_with_return(self, command):
        self.seri.write(command)
        re = ""
        try:
            if self.seri.open :
                re = self.seri.read_until(b"\n").decode('utf8')
        except:
            return re
        return re

    def read_line(self):
        if self.seri.open :
            re = self.seri.read_until(b"\n")
        else:
            re = ""
        return re
    # def read_line_(self):
    #     if self.seri.open :
    #         # re = self.seri.read_until("\n")
    #         re = self.seri.readline()
    #     else:
    #         re = ""
    #     return re
