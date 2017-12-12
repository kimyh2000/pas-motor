# NRTGT100.py
"""
본 모듈은 Tesntion(장력) Controller 를 제어히기 위한 모듈이다.
controller의 tension은 상의 제어 시스템 (PC, PLC 등)에서 RS485 통신을 통해 제어한다.

class



"""
import logger as log
import serial
import time
from operator import eq

class CNRTGT100:
    def __init__(self, deviceID, commPort):
        self.deviceID = deviceID
        self.opStstus = [0x30, 0x31]    # STOP : 0x30, RUN : 0x31
        self.machineStus = 0x30         # STOP
        self.curPWM = 0
        self.initSerialComm(commPort)
        log.logger.debug("========== CNrtGT100 initialize end")

    # Baurate : 9600
    # Data Bits : 8 Bit
    # Stop Bits : 1 Bit
    # Parity Bit : No Parity
    def initSerialComm(self, commPort):
        #log.logger.debug("(2) comport {0}".format(commPort))
        log.logger.debug("CNrtGT100 comm port {0} initialize".format(commPort))
        self.ser = serial.Serial()
        self.ser.port = commPort     # 'COM4'
        self.ser.baudrate = 9600 
        self.ser.bytesize = 8
        self.ser.parity = 'N'        
        self.ser.stopbits = 1
        self.ser.timeout = 5         # 5 sec
        self.ser.write_timeout = 5   # 5 sec        

        if self.ser._isOpen == False:
            log.logger.debug("Serial Port is not Open")
            self.ser.open()
            log.logger.debug("Serial Port is Open {0}".format(self.ser._isOpen))

        log.logger.debug(self.ser)            
        log.logger.debug("CNrtGT100 Initialize serial comm")

    # Write PWM Data to Device
    #
    #
    def sendRequest(self, commandType, runCommand, outPWM = 0):
        log.logger.debug("CNRTGT100 sendRequest start {0}, {1}, {2}".format(commandType, runCommand, outPWM))

        # index 0 ~ 7
        dataString = '%GT100S#'

        # index 8
        if commandType: # True = Commanddata
            dataString += 'W'
        else:
            dataString += 'M'

        log.logger.debug("dataString is {0}".format(dataString))
        self.ser.write(bytes(dataString.encode()))

        # index 9
        dataFrame = []

        dataFrame.append(self.deviceID)
        
        # index 10 ~ 12
        if commandType: # True = Command
            dataFrame.append(self.opStstus[runCommand])     # Stop = 0x30, Run = 0x31
            dataFrame.append(outPWM >> 8)   # Memory Address Hi
            dataFrame.append(outPWM & 0xFF) # Memory Address Low
        else:
            dataFrame.append(0x30)
            dataFrame.append(0)             # Memory Address Hi
            dataFrame.append(0x30)          # Memory Address Low
            
        # index 13 ~ 19
        dataFrame.extend([0, 0, 0, 0, 0, 0])
        dataFrame.append(0x30)

        # BCC Checksum
        bcc = self.bccCheckSum(dataFrame)
        dataFrame.append(bcc)
        log.logger.debug(dataFrame)
        
        self.ser.write(bytearray(dataFrame))

        dataString = '\n\r'
        self.ser.write(bytes(dataString.encode()))

        log.logger.debug("CNrtGT100 sendRequest end {0}, {1}".format(runCommand, outPWM))

        if commandType: # True = Commanddata
            self.getCommandResponse()
        else:
            self.getMonitoringResponse()

        log.logger.debug("CNrtGT100 Response end")
        

    def getCommandResponse(self, BytesToRead = 14):    
        res = 'OK'
        
        readData = self.ser.read(BytesToRead)
        
        log.logger.debug("(1) read Data is {0}, {1},  {2:d}, Data receive OK !!!".format(readData, readData.decode(), BytesToRead))

        # For Debug
        listReadData = list(readData)
        log.logger.debug(listReadData)

        # 식별자
        readNrtStr = readData[:8]
        log.logger.debug(readNrtStr)
        log.logger.debug(readNrtStr.decode()) 

        # End Message    
        readDataEnd = readData[12:]
        if readDataEnd.decode() != '\n\r':
            log.logger.error("(2) readDataEnd is {0},{1}, Data receive ERROR !!!".format(readDataEnd, readDataEnd.decode()))
            return 'NG'

        log.logger.debug("(3) readDataEnd is {0},{1}, Data receive OK !!!".format(readDataEnd, readDataEnd.decode()))

        if readNrtStr.decode() != '%GT100S#':
            log.logger.error("(4) NRTGT100 name is {0}, Data receive ERROR !!!".format(readNrtStr.decode()))
            return 'NG'
        
        log.logger.debug("(5) NRTGT100 name is {0}, Data receive OK !!!".format(readNrtStr.decode()))

        commandRes = readData[8:9]
        command = commandRes.decode()
        log.logger.debug("(6) Receive Command is {0}".format(command))

        dataFrame = []
        dataFrame.append(ord(command))
        dataFrame.extend(list(readData[9:12]))
        log.logger.debug(dataFrame)

        if dataFrame[1] != self.deviceID:
            log.logger.error("(7) NRTGT100 device ID is {0:d}, Data receive ERROR !!!".format(dataFrame[1]))
            return 'NG'

        if command == '!':    # Command
            log.logger.debug(" ERROR --- Received Illigal Message !!!")
        elif command == '$':    # Command
            log.logger.debug(" Good --- Received OK !!!")

        temp = dataFrame[2:]
        log.logger.debug(temp)
        readBcc = temp[0] << 8
        readBcc |= temp[1]


        log.logger.debug("Received BCC CheckSUm is {0:x}".format(readBcc))

        bcc = self.bccCheckSum(dataFrame[0:2])
        log.logger.debug("Sent BCC CheckSUm is {0:x}".format(bcc))

        log.logger.debug("CNrtGT100 getCommMessage End")
        return 'OK'    


    def getMonitoringResponse(self, BytesToRead = 23):    
        res = 'OK'
        
        readData = self.ser.read(BytesToRead)
        log.logger.debug("read Data is {0}, {1},  {2:d}, Data receive OK !!!".format(readData, readData.decode(), BytesToRead))

        # For Debug
        listReadData = list(readData)
        log.logger.debug(listReadData)

        # 식별자
        readNrtStr = readData[:8]
        log.logger.debug(readNrtStr)
        log.logger.debug(readNrtStr.decode()) 

        # End Message    
        readDataEnd = readData[21:]
        if readDataEnd.decode() != '\n\r':
            log.logger.error("readDataEnd is {0},{1}, Data receive ERROR !!!".format(readDataEnd, readDataEnd.decode()))
            return 'NG'

        log.logger.debug("readDataEnd is {0},{1}, Data receive OK !!!".format(readDataEnd, readDataEnd.decode()))

        if readNrtStr.decode() != '%GT100S#':
            log.logger.error("NRTGT100 name is {0}, Data receive ERROR !!!".format(readNrtStr.decode()))
            return 'NG'
        
        log.logger.debug("NRTGT100 name is {0}, Data receive OK !!!".format(readNrtStr.decode()))

        commandStr = readData[8:9]
        command = commandStr.decode()
        log.logger.debug("Receive Command is {0}".format(command))

        dataFrame = list(readData[9:21])
        log.logger.debug(dataFrame)

        if dataFrame[0] != self.deviceID:
            log.logger.error("NRTGT100 device ID is {0:d}, Data receive ERROR !!!".format(dataFrame[0]))
            return 'NG'

        if command != 'M':    # Command
            log.logger.error(" ERROR --- Received Illigal Message !!!")
            return 'NG'

        self.machineStatus = dataFrame[1]    # Stop / Start
        self.outPWM = dataFrame[3]

        bcc = dataFrame[-1] 
        log.logger.debug("Received BCC CheckSUm is {0:x}".format(bcc))

        bcc = self.bccCheckSum(dataFrame[:11])
        log.logger.debug("Sent BCC CheckSUm is {0:x}".format(bcc))

        log.logger.debug("getMonitoringResponse End")

        return 'OK'    


    def bccCheckSum(self, dataFrame):
        log.logger.debug("BCC data frame is {0}".format(dataFrame))

        bcc = 0
        for data in dataFrame:
            bcc ^= data
            #log.logger.debug(" BCC is {0:x}, {1:x}".format(data, bcc))

        log.logger.debug(" Final BCC is {0:x}, {1}".format(bcc, bcc))

        return bcc
