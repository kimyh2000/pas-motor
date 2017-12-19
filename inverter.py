import logger as log
import serial
import time
import modbusCRC



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
    #확장 공통영역 : 인버터 모니터링 영역 파라미터 (R)
    'Model'             : 0x0300,       #R
    'Power'             : 0x0301,       #R
    'InputVol'          : 0x0302,       #R
    'Version'           : 0x0303,       #R
    'OpStatus'          : 0x0305,       #R
    'OutputCurrent'     : 0x0310,       #R
    'OutputFreq'        : 0x0311,       #R
    'RPM'               : 0x0312,       #R
    'OutputVol'         : 0x0314,       #R
    
    #확장 공통영역 : 인버터 제어 영역 파라미터 (R/W)
    'CommandFreq'       : 0x0380,       #R/W
    'OpCommand'         : 0x0382,       #R/W
    'AccelTime'         : 0x0383,       #R/W
    'DecelTime'         : 0x0384,       #R/W
}

inverOpCommand = {
    'Stop'              : 0b00000001,   # 0 : Stop, 1 : Run
    'F_Run'             : 0b00000010,   # 0 : R,    1 : F
    'Trip_Rerset'       : 0b00000100,   # 1 : Trip Reset 
    'FreeRun_Stop'      : 0b00001000,   # 1 : Free Run Stop
#    'EmgStop'           : 0b00010000
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


class CInverter:
    def __init__(self, commPort):
        log.logger.debug("(1) comport {0}".format(commPort))
        self.Model = ''
        self.power = 0xFFFF     #04. kW
        self.inputValtage = 0   # 0 : 220V, 1 : 440V
        self.version = 0x0000
        self.status = 0
        self.outputCurrent = 0
        self.outputFreq = 0
        self.rpm = 0
        self.outputVol = 0

        self.commandFreq = 0
        self.opCommand = 0x0000
        self.accelTime = 0
        self.decelTime = 0
        self.initSerialComm(commPort)
        log.logger.debug("CInverter __init__")

    def initSerialComm(self, commPort):
        log.logger.debug("(2) comport {0}".format(commPort))
        self.ser = serial.Serial()
        self.ser.port = commPort     # 'COM4'
        self.ser.baudrate = 9600 
        self.ser.bytesize = 8
        self.ser.parity = 'N'        
        self.ser.stopbits = 2
        self.ser.timeout = 5         # 5 sec
        self.ser.write_timeout = 5   # 5 sec        

        if self.ser.isOpen() == False:
            log.logger.debug("Serial Port is not Open")
            self.ser.open()
            log.logger.debug("Serial Port is Open {0}".format(self.ser.isOpen()))

        log.logger.debug(self.ser)            
        log.logger.debug("CInverter Initialize serial comm")

    def getInverStatus(self):
        res = 'OK'
        
        # get Inverter Model
        self.sendRequest('Model')
        res, readData = self.getResponse()
        if res == 'NG':
            return res
        self.Model = readData
        time.sleep(0.7)     # 100 msec

        # get Inverter Power
        self.sendRequest('Power')
        res, readData = self.getResponse()
        if res == 'NG':
            return res
        self.power = readData 
        time.sleep(0.7)
      
        # get Inverter Input Voltage
        self.sendRequest('InputVol')
        res, readData = self.getResponse()
        if res == 'NG':  
            return res
        self.inputValtage = readData 
        time.sleep(0.7)

        # get Inverter Version
        self.sendRequest('Version')
        res, readData = self.getResponse()
        if res == 'NG':
            return res
        self.version = readData 
        time.sleep(0.7)

       # get Inverter Version
        self.sendRequest('OpStatus')
        res, readData = self.getResponse()
        if res == 'NG':
            return res
        self.status = readData 
        time.sleep(0.7)

        # get Inverter Output Frequency
        self.sendRequest('OutputCurrent')
        res, readData = self.getResponse()
        if res == 'NG':  
            return res
        self.outputCurrent = readData 
        time.sleep(0.7)

        # get Inverter Output Frequency
        self.sendRequest('OutputFreq')
        res, readData = self.getResponse()
        if res == 'NG':  
            return res
        self.outputFreq = readData 
        time.sleep(0.7)

        # get Inverter RPM
        self.sendRequest('RPM')
        res, readData = self.getResponse()
        if res == 'NG':  
            return res
        self.rpm = readData 

        # get Inverter Out Voltage
        self.sendRequest('OutputVol')
        res, readData = self.getResponse()
        if res == 'NG':  
            return res
        self.outputVol = readData 

        # get Inverter Command Frequency
        self.sendRequest('CommandFreq')
        res, readData = self.getResponse()
        if res == 'NG':  
            return res
        self.commandFreq = readData 
        time.sleep(0.7)

        # get Inverter Operation Command Option
        self.sendRequest('OpCommand')
        res, readData = self.getResponse()
        if res == 'NG':  
            return res

        time.sleep(0.7)    

        # get Inverter Accelation Time
        self.sendRequest('AccelTime')
        res, readData = self.getResponse()
        if res == 'NG':  
            return res
        self.accelTime = readData 
        time.sleep(0.7)

        # get Inverter Decelation Time
        self.sendRequest('DecelTime')
        res, readData = self.getResponse()
        if res == 'NG':  
            return res
        self.decelTime = readData 
        time.sleep(0.7)
            
        log.logger.debug("CInverter getInverStatus")

        return res

    def sendRequest(self, readMem, regCount=1):
        log.logger.debug("CInverter sendRequest start {0}".format(readMem))

        dataFrame = []
        dataFrame.append(slaveDevice['inverterLS'])        # Slave No.
        dataFrame.append(FunctionCode['readInputReg'])     # Function Code

        addr = inverParamList[readMem] -1
        dataFrame.append(addr >> 8)     # Memory Address Hi
        dataFrame.append(addr & 0xFF)   # Memory Address Low

        # Quantity Of Registers
        dataFrame.append(regCount >> 8)     # Quantity Of Registers Hi
        dataFrame.append(regCount & 0xFF)   # Quantity Of Registers Low

        crc = modbusCRC.CRC16(dataFrame)    # Make CRC Checksum
        dataFrame.append(crc & 0xFF)        # CRC Low
        dataFrame.append(crc >> 8)          # CRC Hi

        log.logger.debug(dataFrame)
        log.logger.debug(bytearray(dataFrame))
        #log.logger.debug(self.ser)

        self.ser.write(bytearray(dataFrame))

        log.logger.debug("#############  CInverter sendRequest end {0}".format(readMem))


    #
    # get response from Inverter
    # BytesToRead = Address(1 Byte) + Function(1 Byte) + Data Byte 수(1 Byte) + Data(Word) + CRC(2 Byte) = 7
    # response :
    #   - OK/NG
    #   - readData List
    def getResponse(self, BytesToRead = 7):    
        res = 'OK'
        readValue = 0;
        
        #readData = [0x01, 0x04, 0x02, 0x12, 0x34, 0xA1, 0xB1]
        readByteData = self.ser.read(BytesToRead)
        readData = list(readByteData)
        log.logger.debug("getResponse ReadData {0}, {1}".format(len(readByteData), len(readData)))
        log.logger.debug(readByteData)
        log.logger.debug(readData)

#        if len(readData) < BytesToRead:
#            res = 'NG'
        if len(readData) >= BytesToRead:      
            if (readData[0] != slaveDevice['inverterLS']) or (readData[1] != FunctionCode['readInputReg']):
                res = 'NG'
            
            # Word 단위로 변경함
            if res == 'OK':
                temp = readData[3:5]
                readValue = temp[0] << 8
                readValue |= temp[1]
            
            log.logger.debug("$$$$$$$$$$$  CInverter getResponse is {0}, Data is {1}".format(res, readValue))
        else:
            res = 'NG'

        return res, readValue


    # 16 Bit 단위로 데이터 요청함
    # Dara = Address(1 Byte) + Function(1 Byte) + start Add(2 Byte) + Register 수 (2 Byte) + Byte Count(1 Byte) + Data(Word) + CRC(2 Byte) =11   
    def sendWriteData(self, readMem, writeData):
        dataFrame = []
        dataFrame.append(slaveDevice['inverterLS'])        # Slave No.
        dataFrame.append(FunctionCode['presetSingleReg'])     # Function Code

        addr = inverParamList[readMem] - 1
        dataFrame.append(addr >> 8)     # Memory Address Hi
        dataFrame.append(addr & 0xFF)   # Memory Address Low

        # Quantity Of Registers
        #dataFrame.append(regCount >> 8)     # Quantity Of Registers Hi
        #dataFrame.append(regCount & 0xFF)   # Quantity Of Registers Low

        #dataFrame.append(byteCount)        # Write data count

        # Write Data
        dataFrame.append(writeData >> 8)     # Write Data Hi
        dataFrame.append(writeData & 0xFF)   # Write Data Low
        log.logger.debug(writeData)

        crc = modbusCRC.CRC16(dataFrame)    # Make CRC Checksum
        dataFrame.append(crc & 0xFF)        # CRC Low
        dataFrame.append(crc >> 8)          # CRC Hi
        log.logger.debug(crc)

        log.logger.debug(dataFrame)
        log.logger.debug(bytearray(dataFrame))
        self.ser.write(bytearray(dataFrame))

        log.logger.debug("CInverter sendWriteData")

        return writeData, len(dataFrame)

    #
    # get response from Inverter
    # BytesToRead = Address(1 Byte) + Function(1 Byte) + 시작 Address(2 Byte) + 제어 Register(2 Byte) + CRC(2 Byte) = 8
    # response :
    #   - OK/NG
    #   - readData List
    def getWriteResponse(self, writeData, BytesToRead):    
        res = 'OK'
        readValue = 0;
        
        #readData = [0x01, 0x10, 0x00, 0x06, 0x01, 0x02, 0x11, 0x12]
        readData = list(self.ser.read(BytesToRead))
        if len(readData) < BytesToRead:
            res = 'NG'
        
        if readData[0] != slaveDevice['inverterLS'] or readData[1] != FunctionCode['presetSingleReg']:
            res = 'NG'


        log.logger.debug("-----------CInverter getWriteResponse is {0}".format(res))       
        
        return res

    def sendParameter(self, addr, param):
        wData, count = self.sendWriteData(addr, param)
        res = self.getWriteResponse(wData, count)

        log.logger.debug("CInverter runMotor {0}, {1}".format(wData, count)) 
        
        return res

    def runMotor(self, direction = True):
        self.sendRequest('OpCommand')
        res, opCommand = self.getResponse()
        log.logger.debug("(1) CInverter runMotor {0}, {1:x}".format(opCommand, opCommand)) 
        
        if res == 'OK':
            if (opCommand & inverOpCommand['Stop'] == 0): 
                log.logger.debug("(2) CInverter runMotor was Stop") 
                
                if direction == True:
                    #opCommand |= inverOpCommand['F_Run']
                    opCommand |= 0x0011
                    log.logger.debug("(3) CInverter runMotor {0}, {1:x}".format(opCommand, opCommand)) 
                #else:
                #    opCommand |= inverOpCommand['R_Run']
                    
                wData, count = self.sendWriteData('OpCommand', opCommand)
                res = self.getWriteResponse(wData, count)
        
        log.logger.debug("CInverter runMotor {0}".format(direction)) 

        return res        
        
    def motorStop(self, emgStop = False):
        self.sendRequest('OpCommand')
        res, opCommand = self.getResponse()
        log.logger.debug("(1) CInverter motorStop {0}, {1:x}".format(opCommand, opCommand)) 
        
        if res == 'OK':
            #if emgStop == True:
            #    opCommand |= inverOpCommand['EmgStop']
            #else:
            #opCommand &= inverOpCommand['Stop']
            opCommand = 0
            log.logger.debug("(2) CInverter motorStop {0}, {1:x}".format(opCommand, opCommand)) 
                
            wData, count = self.sendWriteData('OpCommand', opCommand)
            res = self.getWriteResponse(wData, count)
        
        log.logger.debug("CInverter motorStop {0}".format(emgStop)) 

        return res 

    def motorFaultReset(self):
        self.sendRequest('OpCommand')
        res, opCommand = self.getResponse()
        log.logger.debug("Before : motorFaultReset{0} {1:x}".format(res, opCommand))

        if res == 'OK':
            opCommand |= inverOpCommand['FaultReset']
            wData, count = self.sendWriteData('OpCommand', opCommand)
            res = self.getWriteResponse(wData, count)

        log.logger.debug("After : motorFaultReset{0} {1:x}".format(res, opCommand))
        log.logger.debug("CInverter motorFaultReset")         
        return res 


    def updateInverterStatus(self):
        log.logger.debug("CInverter motorFaultReset")         
        log.logger.debug("Model {0}".format(self.Model))
        log.logger.debug("Power {0:x}".format(self.power))
        log.logger.debug("Input Voltage {0:d}".format(self.inputValtage))
        log.logger.debug("Version {0:x}".format(self.version))
        log.logger.debug("Command Freq {0:d}".format(self.commandFreq))
        log.logger.debug("OP Command {0:x}".format(self.opCommand))
        log.logger.debug("Accel Time {0:d}".format(self.accelTime))
        log.logger.debug("Decel Time {0:d}".format(self.decelTime))
        log.logger.debug("Output Freq {0:d}".format(self.outputFreq))
        log.logger.debug("RPM {0:d}".format(self.rpm))
#        return  self.Model, self.power, self.inputValtage, \n
#                self.version, self.commandFreq, self.opCommand, \n
#                self.accelTime, self.decelTime, self.outputFreq, self.rpm