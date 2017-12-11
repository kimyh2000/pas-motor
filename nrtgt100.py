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
        print('==============================================================================\n\r')
        print("CNRTGT100 sendRequest start {0}, {1}, {2}".format(commandType, runCommand, outPWM))
        # index 0 ~ 7
        dataString = '%GT100S#'

        # index 8
        if commandType: # True = Commanddata
            dataString += 'W'
        else:
            dataString += 'M'

        print("dataString is {0}".format(dataString))
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
        print(dataFrame)
        
        self.ser.write(bytearray(dataFrame))

        dataString = '\n\r'
        self.ser.write(bytes(dataString.encode()))

        print("CNrtGT100 sendRequest end {0}, {1}".format(runCommand, outPWM))

        if commandType: # True = Commanddata
            self.getCommandResponse()
        else:
            self.getMonitoringResponse()

        print("CNrtGT100 Response end")
        

    def getCommandResponse(self, BytesToRead = 14):    
        res = 'OK'
        
        readData = self.ser.read(BytesToRead)
        
        print('==============================================================================\n\r')        
        print("(1) read Data is {0}, {1},  {2:d}, Data receive OK !!!".format(readData, readData.decode(), BytesToRead))

        # For Debug
        listReadData = list(readData)
        print(listReadData)

        # 식별자
        readNrtStr = readData[:8]
        print(readNrtStr)
        print(readNrtStr.decode()) 

        # End Message    
        readDataEnd = readData[12:]
        if readDataEnd.decode() != '\n\r':
            print("(2) readDataEnd is {0},{1}, Data receive ERROR !!!".format(readDataEnd, readDataEnd.decode()))
            return 'NG'

        print("(3) readDataEnd is {0},{1}, Data receive OK !!!".format(readDataEnd, readDataEnd.decode()))

        if readNrtStr.decode() != '%GT100S#':
            print("(4) NRTGT100 name is {0}, Data receive ERROR !!!".format(readNrtStr.decode()))
            return 'NG'
        
        print("(5) NRTGT100 name is {0}, Data receive OK !!!".format(readNrtStr.decode()))

        commandRes = readData[8:9]
        command = commandRes.decode()
        print("(6) Receive Command is {0}".format(command))

        dataFrame = []
        dataFrame.append(ord(command))
        dataFrame.extend(list(readData[9:12]))
        print(dataFrame)

        if dataFrame[1] != self.deviceID:
            print("(7) NRTGT100 device ID is {0:d}, Data receive ERROR !!!".format(dataFrame[1]))
            return 'NG'

        if command == '!':    # Command
            print(" ERROR --- Received Illigal Message !!!")
        elif command == '$':    # Command
            print(" Good --- Received OK !!!")

        temp = dataFrame[2:]
        print(temp)
        readBcc = temp[0] << 8
        readBcc |= temp[1]


        print("Received BCC CheckSUm is {0:x}".format(readBcc))

        bcc = self.bccCheckSum(dataFrame[0:2])
        print("Sent BCC CheckSUm is {0:x}".format(bcc))

        print("CNrtGT100 getCommMessage End")
        print('==============================================================================\n\r')
        return 'OK'    


    def getMonitoringResponse(self, BytesToRead = 23):    
        res = 'OK'
        
        readData = self.ser.read(BytesToRead)
        print("read Data is {0}, {1},  {2:d}, Data receive OK !!!".format(readData, readData.decode(), BytesToRead))

        # For Debug
        listReadData = list(readData)
        print(listReadData)

        # 식별자
        readNrtStr = readData[:8]
        print(readNrtStr)
        print(readNrtStr.decode()) 

        # End Message    
        readDataEnd = readData[21:]
        if readDataEnd.decode() != '\n\r':
            print("readDataEnd is {0},{1}, Data receive ERROR !!!".format(readDataEnd, readDataEnd.decode()))
            return 'NG'

        print("readDataEnd is {0},{1}, Data receive OK !!!".format(readDataEnd, readDataEnd.decode()))

        if readNrtStr.decode() != '%GT100S#':
            print("NRTGT100 name is {0}, Data receive ERROR !!!".format(readNrtStr.decode()))
            return 'NG'
        
        print("NRTGT100 name is {0}, Data receive OK !!!".format(readNrtStr.decode()))

        commandStr = readData[8:9]
        command = commandStr.decode()
        print("Receive Command is {0}".format(command))

        dataFrame = list(readData[9:21])
        print(dataFrame)

        if dataFrame[0] != self.deviceID:
            print("NRTGT100 device ID is {0:d}, Data receive ERROR !!!".format(dataFrame[0]))
            return 'NG'

        if command != 'M':    # Command
            print(" ERROR --- Received Illigal Message !!!")
            return 'NG'

        self.machineStatus = dataFrame[1]    # Stop / Start
        self.outPWM = dataFrame[3]

        bcc = dataFrame[-1] 
        print("Received BCC CheckSUm is {0:x}".format(bcc))

        bcc = self.bccCheckSum(dataFrame[:11])
        print("Sent BCC CheckSUm is {0:x}".format(bcc))

        print("getMonitoringResponse End")

        return 'OK'    


    def bccCheckSum(self, dataFrame):
        print("BCC data frame is {0}".format(dataFrame))

        bcc = 0
        for data in dataFrame:
            bcc ^= data
            #print(" BCC is {0:x}, {1:x}".format(data, bcc))

        print(" Final BCC is {0:x}, {1}".format(bcc, bcc))

        return bcc
