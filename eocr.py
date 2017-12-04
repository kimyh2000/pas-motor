
from pyModbusTCP.client import ModbusClient


# EOCR 장치의 클래스를 만든다.
class CEOCR:
    def __init__(self):
        print("create EOCR object")
    
    def initModbusTCP(self, hostName, portNo):
        self.comm = ModbusClient()
        self.comm.host(hostName)
        self.comm.port(portNo)


        
    