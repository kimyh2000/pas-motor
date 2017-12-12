import logger as log
import serial
import time


class CNRTGT100Sim():   
    def __init__(self, commPort):
        self.deviceID = 0
        self.initSerialComm(commPort)
        log.logger.debug("CNRTGT100Sim __init__")

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
            log.logger.debug("Serial Port is not Open")
            self.ser.open()
            log.logger.debug("Serial Port is Open {0}".format(self.ser._isOpen))

        log.logger.debug(self.ser)
        log.logger.debug("CNRTGT100Sim Initialize serial comm")
       
        
    def getCommMessage(self):    
#       self.lock.acquire()
        
        BytesToRead = self.ser.inWaiting()
#        log.logger.debug("getCommMessage {0:d}".format(BytesToRead))
        if BytesToRead < 1:
            # log.logger.debug("readByte {0}".format(BytesToRead))
            time.sleep(0.7)     # 700 msec
            return
        
        log.logger.debug("--------  Start Get Message ----------")    

        #readData = list(self.ser.read(BytesToRead))
        readData = self.ser.read(BytesToRead)
        #BytesToRead = 8
#        self.lock.release()
        log.logger.debug("read Data is {0}, {1:d}".format(readData, BytesToRead))

        if BytesToRead != 23:
            log.logger.error("Receive Data is {0:d}, Data receive ERROR !!!".format(BytesToRead))
            return

        log.logger.debug("Receive Data is {0:d}, Data receive OK !!!".format(BytesToRead))

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
            return

        log.logger.debug("readDataEnd is {0},{1}, Data receive OK !!!".format(readDataEnd, readDataEnd.decode()))

        if readNrtStr.decode() != '%GT100S#':
            log.logger.error("NRTGT100 name is {0}, Data receive ERROR !!!".format(readNrtStr.decode()))
            return
        
        log.logger.debug("NRTGT100 name is {0}, Data receive OK !!!".format(readNrtStr.decode()))

        commandStr = readData[8:9]
        command = commandStr.decode()
        log.logger.debug("Receive Command is {0}, {1}".format(command, readData[8]))

        dataFrame = list(readData[9:21])
        log.logger.debug(dataFrame)

        if dataFrame[0] != self.deviceID:
            log.logger.error("NRTGT100 device ID is {0:d}, Data receive ERROR !!!".format(dataFrame[0]))
            return

        if command == 'M' or command == 'W':    # Command
            self.machineStatus = dataFrame[1]    # Stop / Start
            self.outPWM = dataFrame[3]

            bcc = dataFrame[-1] 
            log.logger.debug("Received BCC CheckSUm is {0:x}".format(bcc))

            bcc = self.bccCheckSum(dataFrame[:11])
            log.logger.debug("Sent BCC CheckSUm is {0:x}".format(bcc))

            self.sendResponse(command)
        else:
            log.logger.debug(" ERROR --- Received Illigal Message !!!")
                  
        log.logger.debug("CInverterSim getCommMessage End")


    def sendResponse(self, command, error = False):
        log.logger.debug('==============================================================================\n\r')
        log.logger.debug("CNRTGT100 sendResponse start {0}, {1}".format(command, error))

        dataString = '%GT100S#'
        dataFrame = []

        # index 8
        if command == 'M': # True = Commanddata
            dataString += 'M'

            log.logger.debug("dataString is {0}".format(dataString))
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
            log.logger.debug(dataFrame)
            
            self.ser.write(bytearray(dataFrame))
            
        elif command == 'W':
            checkSumFrame = []
            if error:
                dataString += '!'
                checkSumFrame.append(ord('!'))
            else:
                dataString += '$'
                checkSumFrame.append(ord('$'))

            log.logger.debug("dataString is {0}".format(dataString))
            self.ser.write(bytes(dataString.encode()))

            dataFrame.append(self.deviceID)
            checkSumFrame.append(self.deviceID)
            log.logger.debug(self.deviceID)
            log.logger.debug(dataFrame)

            # BCC Checksum
            bcc = self.bccCheckSum(checkSumFrame)
            dataFrame.append(bcc >> 8)   # Memory Address Hi
            dataFrame.append(bcc & 0xFF) # Memory Address Low
            log.logger.debug(dataFrame)
            
            self.ser.write(bytearray(dataFrame))
        else:
            log.logger.error(" ERROR --- Illigal Command !!!")                
            return    


        dataString = '\n\r'
        self.ser.write(bytes(dataString.encode()))

    def bccCheckSum(self, dataFrame):
        log.logger.debug("BCC data frame is {0}".format(dataFrame))

        bcc = 0
        for data in dataFrame:
            bcc ^= data

        log.logger.debug(" BCC is {0:x}".format(bcc))

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
#            log.logger.debug("Program end")
#            break