import serial
import time
from operator import eq

class CNRTGT100:
    def __init__(self, deviceID, commPort):
        print("(1) comport {0}".format(commPort))
        self.deviceID = deviceID
        self.opStstus = [0x30, 0x31]    # STOP : 0x30, RUN : 0x31
        self.machineStus = 0x30         # STOP
        self.curPWM = 0
        self.initSerialComm(commPort)
        print("CNrtGT100 __init__")

    # Baurate : 9600
    # Data Bits : 8 Bit
    # Stop Bits : 1 Bit
    # Parity Bit : No Parity
    def initSerialComm(self, commPort):
        print("(2) comport {0}".format(commPort))
        self.ser = serial.Serial()
        self.ser.port = commPort     # 'COM4'
        self.ser.baudrate = 9600 
        self.ser.bytesize = 8
        self.ser.parity = 'N'        
        self.ser.stopbits = 1
        self.ser.timeout = 5         # 5 sec
        self.ser.write_timeout = 5   # 5 sec        

        if self.ser._isOpen == False:
            print("Serial Port is not Open")
            self.ser.open()
            print("Serial Port is Open {0}".format(self.ser._isOpen))

        print(self.ser)            
        print("CNrtGT100 Initialize serial comm")

    # Write PWM Data to Device
    #
    #
    def sendRequest(self, commandType, runCommand, outPWM = 0):
        print("CNRTGT100 sendRequest start {0}, {1}, {2}".format(commandType, runCommand, outPWM))

        dataFrame = []

        # index 0 ~ 7
        dataFrame.append('%GT100S#'.encode())
        # index 8
        if commandType: # True = Command
            dataFrame.append('W'.encode())
        else:
            dataFrame.append('M'.encode())
        # index 9
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
        dataFrame.append(0)
        dataFrame.append(0)
        dataFrame.append(0)
        dataFrame.append(0)
        dataFrame.append(0)
        dataFrame.append(0)
        dataFrame.append(0x30)

        # BCC Checksum
        #bccFrame = dataFrame[9:]
        bcc = self.bccCheckSum(dataFrame[9:])
        #bcc = 0
        #for data in bccFrame:
        #    bcc ^= data
        # index 20 ~ 22
        dataFrame.append(bcc)
        dataFrame.append('\n\r'.encode())
        
        print(dataFrame)
        print(bytearray(dataFrame))
        #print(self.ser)

        self.ser.write(bytearray(dataFrame))

        print("CNrtGT100 sendRequest end {0}, {1}".format(opCommand, outPWM))

    def getCommandResponse(self, BytesToRead = 14):    
        res = 'OK'
        
        readData = list(self.ser.read(BytesToRead))
        print("getCommandResponse ReadData ")
        print(readData)

#        if len(readData) < BytesToRead:
#            res = 'NG'
        if len(readData) >= BytesToRead:
            checkData = "".join(readData[:8])
            if checkData == '%GT100S#':
                if readData[8] == '$' and readData[9] == self.deviceID:
                    bcc = self.bccCheckSum(readData[8:10])
                    res = 'OK'
                elif readData[8] == '!' and readData[9] == self.deviceID:
                    res = 'NG'
                else:
                    res = 'NG'                    
            else:
                res = 'NG'

        return res


    def getMonitoringResponse(self, BytesToRead = 22):    
        res = 'OK'
        
        readData = list(self.ser.read(BytesToRead))
        print("getMonitoringResponse ReadData ")
        print(readData)

#        if len(readData) < BytesToRead:
#            res = 'NG'
        if len(readData) >= BytesToRead:
            checkData = "".join(readData[:9])
            if checkData == '%GT100S#M' and readData[9] == self.deviceID:
                self.machineStus = readData[10] # STOP, RUN
                temp = readData[11:13]
                self.curPWM = temp[0] << 8
                self.curPWM |= temp[1]                    
                bcc = self.bccCheckSum(readData[9:20])

                res = 'OK'
            else:
                res = 'NG'

        return res    


    def bccCheckSum(self, dataFrame):
        print("BCC data frame is {0}".format(dataFrame))

        bcc = 0
        for data in dataFrame:
            bcc ^= data

        print(" BCC is {0:x}".format(bcc))

        return bcc