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

        if self.ser.isOpen() == False:
            log.logger.debug("Serial Port is not Open")
            self.ser.open()
            log.logger.debug("Serial Port is Open {0}".format(self.ser.isOpen()))

        log.logger.debug(self.ser)            
        log.logger.debug("CNrtGT100 Initialize serial comm")

    # Write PWM Data to Device
    #
    #
    def sendRequestOld(self, commandType, runCommand, outPWM = 0):
        log.logger.debug("CNRTGT100 sendRequest start {0}, {1}".format(commandType, outPWM))

        # index 0 ~ 7
        dataString = '%GT100S#'

        # index 8
        if commandType: # True = Commanddata
            dataString2 = 'W'
        else:
            dataString2 = 'M'

        # index 9
        dataString2 += str(self.deviceID)

        # index 10 ~ 12
        if commandType: # True = Command (RUN/STOP)
            if runCommand :
                dataString2 += '1'  # RUN
            else:
                dataString2 += '0'  # STOP    
            #outPWM = 123
            dataString2 += '{:02x}'.format(outPWM)
        else:  
            dataString2 += '000'
            
        # index 13 ~ 19
        dataString2 += '0000000'
        log.logger.debug(dataString2)
        
        # BCC Checksum
        # index 20, 21
        bcc = self.bccCheckSum(dataString2)     
        dataString2 += '{:02x}'.format(bcc)
        log.logger.debug(dataString2)
        
        dataString2 += '\r\n'
        dataString += dataString2
        log.logger.debug(dataString)
        
        self.ser.write(bytes(dataString.encode()))
        
        log.logger.debug("CNrtGT100 sendRequest end {0}".format(outPWM))

        ####
        #datax = [0x25, 0x47, 0x54, 0x31, 0x30, 0x30, 0x53, 0x23, 0x4d, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x37, 0x44, 0x0d, 0x0a]
        #log.logger.debug(datax)
        #self.ser.write(bytearray(datax))
        
        ###
        #if commandType: # True = Command data
        #    self.getCommandResponse()
        #else:
        #    self.getMonitoringResponse()

        log.logger.debug("CNrtGT100 Response end")
    
    #    
    # Naretech V2.3 Protocol 변경에 따라 수정함
    #     



    def sendRequest(self, commandType, runCommand = -1, outPWM = 0):
        log.logger.debug("CNRTGT100 sendRequest start {0}, {1}".format(commandType, outPWM))

        stx = '\x02'
        etx = '\x03'

        # index 0
        dataString = stx
        # index 1
        dataString += str(self.deviceID)

        if commandType == 'W': # Write
            # index 2,3
            dataString += 'WX' 
            # index 4, 5, 6
            if runCommand == 1:     # Command RUN
                dataString += '010'
            elif runCommand == 0:   # Command STOP
                dataString += '000'
            elif runCommand == -1:  # Voltage Setting
                dataString += '1'
                # 정수를 대문자 아스키 값으로 변경하여 저장
                dataString += '{:02X}'.format(outPWM)

            # index 7                
            dataString += etx        
        else: # Read
            # index 2, 3 
            dataString +='RX'
            # index 4, 5, 6, 7
            dataString += '0000'
            # index 8
            dataString += etx

        log.logger.debug(dataString)
        
        # BCC Checksum
        # index 20, 21
        bcc = self.bccCheckSum(dataString)     
        #dataString += '{:02x}'.format(bcc)
        dataString += bcc
        log.logger.debug(dataString)

        self.ser.write(bytes(dataString.encode()))
        
        log.logger.debug("CNrtGT100 sendRequest end {0}".format(outPWM))

        log.logger.debug("CNrtGT100 Response end")

    def getCommandResponse(self, BytesToRead = 8):    
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
        while True:
            BytesToRead = self.ser.inWaiting()
            if BytesToRead < 10:
                log.logger.debug("readByte {0}".format(BytesToRead))
                time.sleep(0.7)     # 700 msec
                continue
            else:
                break

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


    def bccCheckSum(self, dataString):
        log.logger.debug("BCC data String is {0}".format(dataString))

        bcc = 0
        for data in dataString:
            bcc ^= ord(data)
            #log.logger.debug(" BCC is {0:x}, {1:x}".format(data, bcc))

        log.logger.debug(" Final BCC is {0:x}, {1}".format(bcc, bcc))

        return chr(bcc)

    def run(self):
        self.sendRequest("W", 1) 

    def stop(self):
        self.sendRequest("W", 0)

    def setVoltage(self, voltage):
        log.logger.debug(" Voltage is {0}, {1}".format(voltage, type(voltage)))
        self.sendRequest("W", -1, voltage)

    def getStatus(self):
        self.sendRequest("R")
