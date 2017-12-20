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
"""
inverOpCommand = {
    'Stop'              : 0b00000001,   # 0 : Stop, 1 : Run
    'F_Run'             : 0b00000010,   # 0 : R,    1 : F
    'Trip_Rerset'       : 0b00000100,   # 1 : Trip Reset  (Error Reset)
    'FreeRun_Stop'      : 0b00001000,   # 1 : Free Run Stop (EMG Stop)
}
"""
inverOpCommand = {
    'Stop'              : 1,   # 0 : Stop, 1 : Run
    'F_Run'             : 2,   # 0 : R,    1 : F
    'Trip_Rerset'       : 3,   # 1 : Trip Reset  (Error Reset)
    'FreeRun_Stop'      : 4,   # 1 : Free Run Stop (EMG Stop)
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

InvRun = 0
InvRFRun = 1
InvTripReset = 2
InvFreeRunStop = 3

class CInverter:
    def __init__(self, commPort):
        self.Model = 0
        self.power = 0          #04. kW
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
        log.logger.debug("CInverter __init__ Complete")

    def initSerialComm(self, commPort):
        log.logger.debug("CInverter comport is {0}".format(commPort))
        self.ser = serial.Serial()
        self.ser.port = commPort
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
        log.logger.debug("CInverter Initialize serial comm port complete")


    def getInvModel(self, data):
        if data == 0x000A:
            model = 'iG5A'
        else:
            model = 'LS None Model'

        log.logger.debug("CInverter getInvModel : data is {0:x}, model is {1}".format(data, model))
        return model

    def getInvPower(self, data):
        if data == 0x0019:
            invPower = '0.4kW'
        elif data == 0x3200:
            invPower = '0.75kW'
        elif data == 0x4015:
            invPower = '1.5kW'
        elif data == 0x4022:
            invPower = '2.2kW'
        elif data == 0x4037:
            invPower = '3.7kW'
        elif data == 0x4040:
            invPower = '4.0kW'
        elif data == 0x4055:
            invPower = '5.5kW'
        elif data == 0x4075:
            invPower = '7.5kW'
        elif data == 0x4080:
            invPower = '11kW'
        elif data == 0x40F0:
            invPower = '15kW'
        elif data == 0x4125:
            invPower = '18.5kW'
        elif data == 0x4160:
            invPower = '22kW'
        else:
            invPower = 'Invalid Power'

        log.logger.debug("CInverter getInvPower : data is {0:x}, power is {1}".format(data, invPower))
        return invPower

    def getInvInputVol(self, data):
        if data == 0x0220:
            inputVol = '200V 단상 자냉'
        elif data == 0x0230:
            inputVol = '200V 삼상 자냉'
        elif data == 0x0221:
            inputVol = '200V 단상 강냉'
        elif data == 0x0231:
            inputVol = '200V 삼상 강냉'
        elif data == 0x0420:
            inputVol = '400V 단상 자냉'
        elif data == 0x0430:
            inputVol = '400V 삼상 자냉'
        elif data == 0x0421:
            inputVol = '400V 단상 강냉'
        elif data == 0x0431:
            inputVol = '400V 삼상 강냉'
        else:
            inputVol = 'Invalid Voltage'
            
        log.logger.debug("CInverter getInvInputVol : data is {0:x}, input vol. is {1}".format(data, inputVol))
        return inputVol


    def getInverterStatus(self):
        res = 'OK'
        
        # get Inverter Model
        self.sendRequest('Model')
        res, readData = self.getResponse()
        if res == 'NG':
            return res
        self.Model = self.getInvModel(readData)
        time.sleep(0.1)     # 100 msec

        # get Inverter Power
        self.sendRequest('Power')
        res, readData = self.getResponse()
        if res == 'NG':
            return res
        self.power = self.getInvPower(readData) 
        time.sleep(0.1)
      
        # get Inverter Input Voltage
        self.sendRequest('InputVol')
        res, readData = self.getResponse()
        if res == 'NG':  
            return res
        self.inputValtage = self.getInvInputVol(readData) 
        time.sleep(0.1)

        # get Inverter Version
        self.sendRequest('Version')
        res, readData = self.getResponse()
        if res == 'NG':
            return res
        self.version = readData 
        time.sleep(0.1)

       # get Inverter Operation Status
        self.sendRequest('OpStatus')
        res, readData = self.getResponse()
        if res == 'NG':
            return res
        self.status = readData 
        time.sleep(0.1)

        # get Inverter Output Current
        self.sendRequest('OutputCurrent')
        res, readData = self.getResponse()
        if res == 'NG':  
            return res
        self.outputCurrent = readData 
        time.sleep(0.1)

        # get Inverter Output Frequency
        self.sendRequest('OutputFreq')
        res, readData = self.getResponse()
        if res == 'NG':  
            return res
        self.outputFreq = readData 
        time.sleep(0.1)

        # get Inverter RPM
        self.sendRequest('RPM')
        res, readData = self.getResponse()
        if res == 'NG':  
            return res
        self.rpm = readData 
        time.sleep(0.1)

        # get Inverter Out Voltage
        self.sendRequest('OutputVol')
        res, readData = self.getResponse()
        if res == 'NG':  
            return res
        self.outputVol = readData 
        time.sleep(0.1)

        # get Inverter Command Frequency
        self.sendRequest('CommandFreq')
        res, readData = self.getResponse()
        if res == 'NG':  
            return res
        self.commandFreq = readData 
        time.sleep(0.1)

        # get Inverter Operation Command Option
        self.sendRequest('OpCommand')
        res, readData = self.getResponse()
        if res == 'NG':  
            return res
        time.sleep(0.1)    

        # get Inverter Accelation Time
        self.sendRequest('AccelTime')
        res, readData = self.getResponse()
        if res == 'NG':  
            return res
        self.accelTime = readData 
        time.sleep(0.1)

        # get Inverter Decelation Time
        self.sendRequest('DecelTime')
        res, readData = self.getResponse()
        if res == 'NG':  
            return res
        self.decelTime = readData 
            
        log.logger.debug("CInverter getInverterStatus complete")

        return res

    def sendRequest(self, readMem, regCount=1):
        log.logger.debug("###  CInverter sendRequest start {0}".format(readMem))

        dataFrame = []
        dataFrame.append(slaveDevice['inverterLS'])        # Slave No.
        dataFrame.append(FunctionCode['readInputReg'])     # Function Code

        # !!!! 중요 !!!!
        # LS 산전 iG5A Inverter 메뉴얼 오류로 인해
        # 메뉴얼에 표기되어 있는 확정 공통영역 주소에서 -1 을 위치에서 데이터 읽어야 함 
        addr = inverParamList[readMem] - 1
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

        self.ser.write(bytearray(dataFrame))

        log.logger.debug("###  CInverter sendRequest end {0}".format(readMem))


    #
    # get response from Inverter
    # BytesToRead = Address(1 Byte) + Function(1 Byte) + Data Byte 수(1 Byte) + Data(Word) + CRC(2 Byte) = 7
    # response :
    #   - OK/NG
    #   - readData List
    def getResponse(self, BytesToRead = 7):    
        res = 'OK'
        readValue = 0;
        
        readByteData = self.ser.read(BytesToRead)
        readData = list(readByteData)

        log.logger.debug("###  CInverter getResponse start : ReadData Count is {0}, {1}".format(len(readByteData), len(readData)))
        log.logger.debug(readByteData)
        log.logger.debug(readData)

#        if len(readData) < BytesToRead:
#            res = 'NG'

        if len(readData) >= BytesToRead:      
            if (readData[0] != slaveDevice['inverterLS']) or (readData[1] != FunctionCode['readInputReg']):
                res = 'NG'
                log.logger.debug("###  CInverter getResponse Error : Res is {0}, Data is {1}".format(res, readData))
            
            # Word 단위로 변경함
            if res == 'OK':
                temp = readData[3:5]
                readValue = temp[0] << 8
                readValue |= temp[1]      
                log.logger.debug("###  CInverter getResponse complete : Res is {0}, Data is {1}".format(res, readValue))
        else:
            res = 'NG'

        return res, readValue


    # 16 Bit 단위로 데이터 요청함
    # Data = Device ID(1 Byte) + Function(1 Byte) + start Address(2 Byte) + Data(Word:2 Byte) + CRC(2 Byte) =8 Byte   
    def sendWriteData(self, readMem, writeData):
        dataFrame = []
        dataFrame.append(slaveDevice['inverterLS'])        # Slave No.
        dataFrame.append(FunctionCode['presetSingleReg'])     # Function Code

        # !!!! 중요 !!!!
        # LS 산전 iG5A Inverter 메뉴얼 오류로 인해
        # 메뉴얼에 표기되어 있는 확정 공통영역 주소에서 -1 을 위치에서 데이터 읽어야 함 
        addr = inverParamList[readMem] - 1
        dataFrame.append(addr >> 8)     # Memory Address Hi
        dataFrame.append(addr & 0xFF)   # Memory Address Low

        # Write Data
        dataFrame.append(writeData >> 8)     # Write Data Hi
        dataFrame.append(writeData & 0xFF)   # Write Data Low
        log.logger.debug(writeData)

        crc = modbusCRC.CRC16(dataFrame)    # Make CRC Checksum
        dataFrame.append(crc & 0xFF)        # CRC Low
        dataFrame.append(crc >> 8)          # CRC Hi

        log.logger.debug(dataFrame)
        log.logger.debug(bytearray(dataFrame))
        self.ser.write(bytearray(dataFrame))

        log.logger.debug("### CInverter sendWriteData complete")

        return writeData, len(dataFrame)

    #
    # get response from Inverter
    # Read Data = Device ID(1 Byte) + Function(1 Byte) + start Address(2 Byte) + Data(Word:2 Byte) + CRC(2 Byte) =8 Byte   
    # response :
    #   - OK/NG
    #   - readData List
    def getWriteResponse(self, writeData, BytesToRead):    
        res = 'OK'
        readValue = 0;
        
        readData = list(self.ser.read(BytesToRead))
        if len(readData) < BytesToRead:
            res = 'NG'
        
        if readData[0] != slaveDevice['inverterLS'] or readData[1] != FunctionCode['presetSingleReg']:
            res = 'NG'
            log.logger.debug("###  CInverter getWriteResponse Error : Res is {0}, Data is {1}".format(res, readData))


        log.logger.debug("###  CInverter getWriteResponse Complete : Res is {0}".format(res))       
        
        return res

    def sendParameter(self, addr, param):
        log.logger.debug("###  CInverter sendParameter start : Address is {0}, Param is {1}".format(addr, param)) 

        wData, count = self.sendWriteData(addr, param)
        res = self.getWriteResponse(wData, count)

        log.logger.debug("###  CInverter sendParameter end : Res is {0}".format(res)) 
        
        return res

    def isBitOn(self, data, bit):
        data &= (0x01 << bit)
        log.logger.debug("###  CInverter isBitOn : Data is {0:b}".format(data))        

        return data

    def bitSet(self, data, bit, bitOn):
        if bitOn:   
            data |= (0x01 << bit)
        else:
            data &= ~(0x01 << bit)

        log.logger.debug("###  CInverter bitSet : Data is {0:b}".format(data))        

        return data


    def runMotor(self, direction = True):
        self.sendRequest('OpCommand')
        res, opCommand = self.getResponse()

        log.logger.debug("###  CInverter runMotor start : Direction is {0}, Res is {1}, OpCommand is {2:x}".format(direction, res, opCommand)) 
        
        if res == 'OK':
            if self.isBitOn(opCommand, InvRun): 
                log.logger.debug("###  CInverter runMotor : Motor is already Running") 
                return
                
            if direction == True:   # 정회전
                opCommand = self.bitSet(opCommand, InvRFRun, True)
            else:                   # 역회전
                opCommand = self.bitSet(opCommand, InvRFRun, False)

            opCommand = self.bitSet(opCommand, InvRun, True)
            log.logger.debug("###  CInverter runMotor command set : data is {0:x}".format(opCommand)) 
                
            wData, count = self.sendWriteData('OpCommand', opCommand)
            res = self.getWriteResponse(wData, count)
        
            log.logger.debug("###  CInverter runMotor end") 

        return res        
        
    def motorStop(self, emgStop = False):
        self.sendRequest('OpCommand')
        res, opCommand = self.getResponse()

        log.logger.debug("###  CInverter motorStop start : EMG is {0}, Res is {1}, OpCommand is {2:x}".format(emgStop, res, opCommand)) 
        
        if res == 'OK':
            if emgStop == True:
                opCommand = self.bitSet(opCommand, InvFreeRunStop, True)
            else:
                opCommand = self.bitSet(opCommand, InvFreeRunStop, False)
                
            opCommand = self.bitSet(opCommand, InvRun, False)
            log.logger.debug("###  CInverter motorStop command set : data is {0:x}".format(opCommand)) 
                
            wData, count = self.sendWriteData('OpCommand', opCommand)
            res = self.getWriteResponse(wData, count)
        
            log.logger.debug("###  CInverter motorStop end") 

        return res 

    def motorFaultReset(self):
        self.sendRequest('OpCommand')
        res, opCommand = self.getResponse()

        log.logger.debug("###  CInverter motorFaultReset start : Res is {0}, OpCommand is {1:x}".format(res, opCommand)) 

        if res == 'OK':
            if self.isBitOn(opCommand, InvRun): 
                log.logger.debug("###  CInverter motorFaultReset : Motor is already Running") 
                return
            
            opCommand = self.bitSet(opCommand, InvTripReset, True)
            log.logger.debug("###  CInverter motorFaultReset command set : data is {0:x}".format(opCommand)) 

            wData, count = self.sendWriteData('OpCommand', opCommand)
            res = self.getWriteResponse(wData, count)

            log.logger.debug("###  CInverter motorFaultReset end") 

        return res 


    def updateInverterStatus(self):
        log.logger.debug("CInverter motorFaultReset")         
        log.logger.debug("Model {0}".format(self.Model))
        log.logger.debug("Power {0}".format(self.power))
        log.logger.debug("Input Voltage {0}".format(self.inputValtage))
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