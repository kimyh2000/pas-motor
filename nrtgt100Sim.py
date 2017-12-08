
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
        
        print("--------  Start Get Message ----------")    

        #readData = list(self.ser.read(BytesToRead))
        readData = self.ser.read(BytesToRead)
        #BytesToRead = 8
#        self.lock.release()
        print("read Data is {0}, {1},  {2:d}".format(readData, readData.decode(), BytesToRead))

        if readData.decode() == '%GT100S#':
            print("Same")
        else:
            print("Different")
        return

        if len(readData) == 0:
            print("read data is empty")
            return

        temp = "".join(readData[:8])
        print("Get Message is {0}".format(temp))
        return

        if temp != "%GT100S#":
            return       
        
        if readData[8] == 'W' or readData[8] == 'M':  # Command
            self.machineStatus = readData[10]
            self.outPWM = readData[11:13]

            bcc = readData[20] 
            print("Received BCC CheckSUm is {0:x}".format(bcc))

            bcc = self.bccCheckSum(readData[9:20])
            print("Sent BCC CheckSUm is {0:x}".format(bcc))

            commandType = readData[8]
            self.sendResponse(commandType)
        else:
            print(" ERROR --- Received Illigal Message !!!")
                  
        print("CInverterSim getCommMessage End")


    def sendResponse(self, commandType):
        print("CNRTGT100 sendResponse start {0}".format(commandType))

        dataFrame = []

        # index 0 ~ 7
        dataFrame.append('%GT100S#')
        
        # index 8
        print("Command Type is {0}".format(commandType))

        if commandType == 'W':
            dataFrame.append('$')
            dataFrame.append(self.deviceID)
            bcc = self.bccCheckSum(dataFrame[8:])
            dataFrame.append(bcc)
            dataFrame.append('\n\r')           
        else:
            dataFrame.append('M')
            dataFrame.append(self.deviceID)
            dataFrame.append(0x31)  # RUN
            outPWM = 0xF0
            dataFrame.append(outPWM >>8)
            dataFrame.append(outPWM & 0xFF)

            dataFrame.append(0)
            dataFrame.append(0)
            dataFrame.append(0)
            dataFrame.append(0)
            dataFrame.append(0)
            dataFrame.append(0)
            dataFrame.append(0x30)

            bcc = self.bccCheckSum(dataFrame[9:20])
            dataFrame.append(bcc)
            dataFrame.append('\n\r')           

        print(dataFrame)
        print(bytearray(dataFrame))
        #print(self.ser)

        self.ser.write(bytearray(dataFrame))

        print("CNrtGT100 sendResponse end")


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