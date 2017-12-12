import logger as log
import threading
import serial
import time
import modbusCRC
from inverter import slaveDevice
from inverter import FunctionCode
from inverter import exceptionCode
from inverter import inverParamList


"""
slaveDevice = {
    'inverterLS'    : 0x01,
    'breaker'       : 0x02
}

# LS iG5A Serise Inverter Modbus-RTU Function Code
FunctionCode = {
    'readHoldReg'       : 0x03,
    'readInputReg'      : 0x04,
    'presetSingleReg'   : 0x06,
    'presetMultiReg'    : 0x10
}

# LS iG5A Serise Inverter Modbus-RTU Exception Code
exceptionCode = {
    'illegalFun'        : 0x01,
    'illegalDataAdd'    : 0x02,
    'illegalDataVal'    : 0x03,
    'slaveDevBusy'      : 0x06
}

# LS iG5A Serise Inverter Common Parameter List
inverParamList = {
    'Model'             : 0x0000,       #R
    'Power'             : 0x0001,       #R
    'InputVol'          : 0x0002,       #R
    'Version'           : 0x0003,       #R
    'ParamSet'          : 0x0004,       #R/W
    'CommandFreq'       : 0x0005,       #R/W
    'OpCommand'         : 0x0006,       #R / RW
    'AccelTime'         : 0x0007,       #R/W
    'DecelTime'         : 0x0008,       #R/W
    'OutputCurrent'     : 0x0009,       #R
    'OutputFreq'        : 0x000A,       #R
    'OutputVol'         : 0x000B,       #R
    'OpStatus'          : 0x000E,       #R
    'RPM'               : 0x0015,       #R
    'OutputTorq'        : 0x001F,       #R
}

inverOpCommand = {
    'Stop'              : 0b00000001,
    'F_Run'             : 0b00000010,
    'R_Run'             : 0b00000100,
    'FaultReset'        : 0b00001000,
    'EmgStop'           : 0b00010000
}

inverOpStatus = {
    'MotorStop'         : 0b00000001,
    'F_Running'         : 0b00000010,
    'R_Running'         : 0b00000100,
    'MotorAccel'        : 0b00001000,
    'MotorDecel'        : 0b00010000,
    'Velocity'          : 0b00100000,
    'DCBracking'        : 0b01000000,
}

"""

class CInverterSim():   
    def __init__(self, commPort):
#        threading.Thread.__init__(self)
#        super(StoppableThread, self).__init__()

#        self._stop = threading.Event()
        self.Model = ''
        self.power = 0xFFFF     #04. kW
        self.inputValtage = 0   # 0 : 220V, 1 : 440V
        self.version = 0x0000
        self.commandFreq = 0
        self.opCommand = 0x0000
        self.accelTime = 0
        self.decelTime = 0
        self.outputFreq = 0
        self.rpm = 0

#        self.lock = threading.Lock()

        self.initSerialComm(commPort)

        log.logger.debug("CInverterSim __init__")

#    def stop(self):
#        self._stop.set()

#    def stopper(self):
#        return self._stop.isSet()

    def run(self):
        while True:
            self.getCommMessage()    
        
    def initSerialComm(self, commPort):
        self.ser = serial.Serial()
        self.ser.port = commPort     # 'COM5'
        self.ser.baudrate = 9600 
        self.ser.bytesize = 8
        self.ser.parity = 'N'        
        self.ser.stopbits = 2
        #self.ser.timeout = 5         # 5 sec
        self.ser.write_timeout = 5   # 5 sec        

        if self.ser._isOpen == False:
            log.logger.debug("Serial Port is not Open")
            self.ser.open()
            log.logger.debug("Serial Port is Open {0}".format(self.ser._isOpen))

        log.logger.debug(self.ser)
        log.logger.debug("CInverterSim Initialize serial comm")
       
        
    def getCommMessage(self):    
#       self.lock.acquire()
        BytesToRead = self.ser.inWaiting()
#        log.logger.debug("getCommMessage {0:d}".format(BytesToRead))
        if BytesToRead < 2:
            #log.logger.debug("readByte {0}".format(BytesToRead))
            time.sleep(0.7)     # 700 msec
            return

        log.logger.debug("--------  Start Get Message ----------")    

        readData = list(self.ser.read(BytesToRead))
#        readData = list(self.ser.read())
#        self.lock.release()
        log.logger.debug(readData)

        if len(readData) == 0:
            log.logger.debug("read data is empty")
            return

        if readData[0] == slaveDevice['inverterLS']:
            if readData[1] == FunctionCode['readInputReg']:
                param = self.make1Byte(readData[2:4])
                res = self.sendResponseStatus(param)
            elif readData[1] == FunctionCode['presetMultiReg']:
                param = self.make1Byte(readData[2:4])
                regCount = self.make1Byte(readData[4:6])
                commandData = self.make1Byte(readData[7:9])
                res = self.sendResponseCommand(param, regCount, commandData)
            else:
                log.logger.debug("Illigal Function Code !!!")    
        else:
            log.logger.debug("Illigal Slave Devie !!!")    
        
        log.logger.debug("CInverterSim getCommMessage End")

    def sendResponseStatus(self, param, byteCount=2):
        
        log.logger.debug("--------  Start sendResponseStatus ----------")   

        dataFrame = []
        dataFrame.append(slaveDevice['inverterLS'])        # Slave No.
        dataFrame.append(FunctionCode['readInputReg'])     # Function Code
    
        dataFrame.append(byteCount)

        log.logger.debug(" param {0:x}".format(param))

        if param == inverParamList['Model']:
            log.logger.debug(" RaramList {0:x}".format(inverParamList['Model']))
            responseData = ord('A')      #iG5A
        elif param == inverParamList['Power']:
            log.logger.debug(" RaramList {0:x}".format(inverParamList['Power']))
            responseData = 0x0003   #2.2kW
        elif param == inverParamList['InputVol']:
            log.logger.debug(" RaramList {0:x}".format(inverParamList['InputVol']))
            responseData = 0        # 0 : 220V, 1 : 440V
        elif param == inverParamList['Version']:
            log.logger.debug(" RaramList {0:x}".format(inverParamList['Version']))
            responseData = 0x0022   # Verion 2.2
        elif param == inverParamList['ParamSet']:
            log.logger.debug(" RaramList {0:x}".format(inverParamList['ParamSet']))
            responseData = 1        # 통신 설정
        elif param == inverParamList['CommandFreq']:
            log.logger.debug(" RaramList {0:x}".format(inverParamList['CommandFreq']))
            responseData = 100
        elif param == inverParamList['OpCommand']:
            log.logger.debug(" RaramList {0:x}".format(inverParamList['OpCommand']))
            responseData = 0x0041   # 통신 설정, 정지
        elif param == inverParamList['AccelTime']:
            log.logger.debug(" RaramList {0:x}".format(inverParamList['AccelTime']))
            responseData = 10
        elif param == inverParamList['DecelTime']:
            log.logger.debug(" RaramList {0:x}".format(inverParamList['DecelTime']))
            responseData = 20
        elif param == inverParamList['OutputCurrent']:
            log.logger.debug(" RaramList {0:x}".format(inverParamList['OutputCurrent']))
            responseData = 50
        elif param == inverParamList['OutputFreq']:
            responseData = 60
        elif param == inverParamList['OutputVol']:
            responseData = 230
        elif param == inverParamList['OpStatus']:
            responseData = 0x0001   #정지
        elif param == inverParamList['RPM']:
            responseData = 120
        else:
            responseData = 0xF0F0
            
        dataFrame.append(responseData >> 8)     # Memory Address Hi
        dataFrame.append(responseData & 0xFF)   # Memory Address Low  
    
        crc = modbusCRC.CRC16(dataFrame)    # Make CRC Checksum
        dataFrame.append(crc & 0xFF)        # CRC Low
        dataFrame.append(crc >> 8)          # CRC Hi

        log.logger.debug(dataFrame)
        log.logger.debug(bytearray(dataFrame))
#       self.lock.acquire()
        self.ser.write(bytearray(dataFrame))
#       self.lock.release()    

        log.logger.debug("CInverterSim sendResponseStatus")

    def sendResponseCommand(self, param, regCount, commandData):
        log.logger.debug("--------  Start sendResponseCommand ----------")   
        
        dataFrame = []
        dataFrame.append(slaveDevice['inverterLS'])         # Slave No.
        dataFrame.append(FunctionCode['presetMultiReg'])    # Function Code
    
        dataFrame.append(param >> 8)        # Memory Address Hi
        dataFrame.append(param & 0xFF)      # Memory Address Low  

        dataFrame.append(regCount >> 8)     # Register Count Hi
        dataFrame.append(regCount & 0xFF)   # Register Count Low  
    
        crc = modbusCRC.CRC16(dataFrame)    # Make CRC Checksum
        dataFrame.append(crc & 0xFF)        # CRC Low
        dataFrame.append(crc >> 8)          # CRC Hi

        log.logger.debug(dataFrame)
        log.logger.debug(bytearray(dataFrame))
        self.ser.write(bytearray(dataFrame))        
        
        log.logger.debug(" param {0:x}".format(param))
        log.logger.debug(" commandData {0:x}".format(commandData))

        if param == inverParamList['ParamSet']:
            log.logger.debug(" RaramList {0:x}".format(inverParamList['ParamSet']))
            pass
        elif param == inverParamList['CommandFreq']:
            log.logger.debug(" RaramList {0:x}".format(inverParamList['CommandFreq']))
            self.commandFreq = commandData
        elif param == inverParamList['OpCommand']:
            log.logger.debug(" RaramList {0:x}".format(inverParamList['OpCommand']))
            self.opCommand = commandData
        elif param == inverParamList['AccelTime']:
            log.logger.debug(" RaramList {0:x}".format(inverParamList['AccelTime']))
            self.accelTime = commandData
        elif param == inverParamList['DecelTime']:
            log.logger.debug(" RaramList {0:x}".format(inverParamList['DecelTime']))
            self.decelTime = commandData
        else:
            pass

        log.logger.debug("CInverterSim sendResponseCommand")

    def make1Byte(self, tempdata):
        log.logger.debug(tempdata)
        byteData = tempdata[0] << 8
        byteData |= tempdata[1]
        return byteData


if __name__ == "__main__":
#    invThread = CInverterSim("COM5")
#    invThread.daemon = True
#    invThread.start()
    invSim = CInverterSim("COM5")
    while True:
        res = invSim.getCommMessage()
#        res = invSim.getCommMessage()
#        if res == True:
#            log.logger.debug("Program end")
#            break