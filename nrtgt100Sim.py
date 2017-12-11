
import serial
import time


class CNRTGT100Sim():   
    def __init__(self, commPort):
        self.deviceID = 0
        self.initSerialComm(commPort)
        print("CNRTGT100Sim __init__")

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
        self.ser.stopbits = 1
        #self.ser.timeout = 5         # 5 sec
        self.ser.write_timeout = 5   # 5 sec        

        if self.ser._isOpen == False:
            print("Serial Port is not Open")
            self.ser.open()
            print("Serial Port is Open {0}".format(self.ser._isOpen))

        print(self.ser)
        print("CNRTGT100Sim Initialize serial comm")
       
        
    def getCommMessage(self):    
#       self.lock.acquire()
        
        BytesToRead = self.ser.inWaiting()
#        print("getCommMessage {0:d}".format(BytesToRead))
        if BytesToRead < 1:
            # print("readByte {0}".format(BytesToRead))
            time.sleep(0.7)     # 700 msec
            return
        
        print('==================================================================================\n\r')
        print("--------  Start Get Message ----------")    

        #readData = list(self.ser.read(BytesToRead))
        readData = self.ser.read(BytesToRead)
        #BytesToRead = 8
#        self.lock.release()
        print("read Data is {0}, {1:d}".format(readData, BytesToRead))

        if BytesToRead != 23:
            print("Receive Data is {0:d}, Data receive ERROR !!!".format(BytesToRead))
            return

        print("Receive Data is {0:d}, Data receive OK !!!".format(BytesToRead))

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
            return

        print("readDataEnd is {0},{1}, Data receive OK !!!".format(readDataEnd, readDataEnd.decode()))

        if readNrtStr.decode() != '%GT100S#':
            print("NRTGT100 name is {0}, Data receive ERROR !!!".format(readNrtStr.decode()))
            return
        
        print("NRTGT100 name is {0}, Data receive OK !!!".format(readNrtStr.decode()))

        commandStr = readData[8:9]
        command = commandStr.decode()
        print("Receive Command is {0}, {1}".format(command, readData[8]))

        dataFrame = list(readData[9:21])
        print(dataFrame)

        if dataFrame[0] != self.deviceID:
            print("NRTGT100 device ID is {0:d}, Data receive ERROR !!!".format(dataFrame[0]))
            return

        if command == 'M' or command == 'W':    # Command
            self.machineStatus = dataFrame[1]    # Stop / Start
            self.outPWM = dataFrame[3]

            bcc = dataFrame[-1] 
            print("Received BCC CheckSUm is {0:x}".format(bcc))

            bcc = self.bccCheckSum(dataFrame[:11])
            print("Sent BCC CheckSUm is {0:x}".format(bcc))

            self.sendResponse(command)
        else:
            print(" ERROR --- Received Illigal Message !!!")
                  
        print("CInverterSim getCommMessage End")


    def sendResponse(self, command, error = False):
        print('==================================================================================\n\r')
        print("CNRTGT100 sendResponse start {0}, {1}".format(command, error))

        dataString = '%GT100S#'
        dataFrame = []

        # index 8
        if command == 'M': # True = Commanddata
            dataString += 'M'

            print("dataString is {0}".format(dataString))
            self.ser.write(bytes(dataString.encode()))

            # index 9
            dataFrame.append(self.deviceID)
            
            # index 10 ~ 12
            dataFrame.append(self.machineStatus)     # Stop = 0x30, Run = 0x31
            dataFrame.append(self.outPWM >> 8)   # Memory Address Hi
            dataFrame.append(self.outPWM & 0xFF) # Memory Address Low
                
            # index 13 ~ 19
            dataFrame.extend([0, 0, 0, 0, 0, 0])
            dataFrame.append(0x30)

            # BCC Checksum
            bcc = self.bccCheckSum(dataFrame)
            dataFrame.append(bcc)
            print(dataFrame)
            
            self.ser.write(bytearray(dataFrame))
            
        elif command == 'W':
            checkSumFrame = []
            if error:
                dataString += '!'
                checkSumFrame.append(ord('!'))
            else:
                dataString += '$'
                checkSumFrame.append(ord('$'))

            print("dataString is {0}".format(dataString))
            self.ser.write(bytes(dataString.encode()))

            dataFrame.append(self.deviceID)
            checkSumFrame.append(self.deviceID)
            print(self.deviceID)
            print(dataFrame)

            # BCC Checksum
            bcc = self.bccCheckSum(checkSumFrame)
            dataFrame.append(bcc >> 8)   # Memory Address Hi
            dataFrame.append(bcc & 0xFF) # Memory Address Low
            print(dataFrame)
            
            self.ser.write(bytearray(dataFrame))
        else:
            print(" ERROR --- Illigal Command !!!")                
            return    


        dataString = '\n\r'
        self.ser.write(bytes(dataString.encode()))
        print('==================================================================================\n\r')

    def bccCheckSum(self, dataFrame):
        print("BCC data frame is {0}".format(dataFrame))

        bcc = 0
        for data in dataFrame:
            bcc ^= data

        print(" BCC is {0:x}".format(bcc))

        return bcc


if __name__ == "__main__":
#    invThread = CNRTGT100Sim("COM5")
#    invThread.daemon = True
#    invThread.start()
    nrtSim = CNRTGT100Sim("COM5")
    while True:
        res = nrtSim.getCommMessage()
#        res = nrtSim.getCommMessage()
#        if res == True:
#            print("Program end")
#            break