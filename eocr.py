# eocr.py
"""[summary]


[description]
"""

import logger as log
import time, threading
from pyModbusTCP.client import ModbusClient

#import logging
#import logging.handlers
 
# 1. 로거 인스턴스를 만든다
eocrLogger = log.logging.getLogger('eocrlogger')

# 2. 포매터를 만든다
eocrFomatter = log.logging.Formatter('%(asctime)s > %(message)s')
#eocrFomatter = log.logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s] %(msecs)d > %(message)s')
 
# 3. 스트림과 파일로 로그를 출력하는 핸들러를 각각 만든다.
#fileHandler = logging.FileHandler('./myLoggerTest.log')
eocrFileMaxByte = 1024 * 1024 * 100 # 100 MB
eocrFileBackupCount = 10
eocrFileHandler = log.logging.handlers.RotatingFileHandler("./eocrLogger.log", eocrFileMaxByte, eocrFileBackupCount)
eocrStreamHandler = log.logging.StreamHandler()
 
# 4. 각 핸들러에 포매터를 지정한다.
eocrFileHandler.setFormatter(eocrFomatter)
eocrStreamHandler.setFormatter(eocrFomatter)

# 5. 1번에서 만든 로거 인스턴스에 스트림 핸들러와 파일핸들러를 붙인다.
eocrLogger.addHandler(eocrFileHandler)
eocrLogger.addHandler(eocrStreamHandler)
 
# 6. 로거 레벨을 설정한다.
eocrLogger.setLevel(log.logging.DEBUG)

SERVER_HOST = "169.254.0.10"
SERVER_PORT = 502


class CEOCRTest(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.__suspend = True
        self.__exit = False
        self.motorDirection = 'F'
        self.motorFreq = 0.0
        self.breakVoltage = 0.0
        # Modbus initialize
        log.logger.debug("EOCR Start !!!")
        self.client = ModbusClient(SERVER_HOST, SERVER_PORT, auto_open=True)
        log.logger.debug(self.client)
        
        if not self.client.is_open():
            if not self.client.open():
                log.logger.error("Modudbus TCP Open ERROR !!!")
            if self.client.is_open():
                log.logger.debug("Modudbus TCP Open OK !!!")
    

    def run(self):
        while True:
            ### Suspend ###
            while self.__suspend == True:
                time.sleep(0.5)
                 
            ### Process ###
            while self.__suspend == False:        
                currentIL1 = self.client.read_holding_registers(522, 2)
                currentIL2 = self.client.read_holding_registers(524, 2)
                currentIL3 = self.client.read_holding_registers(526, 2)
                #eocrLogger.debug("[M_D,M_Frq, B_Vol, Cur_L1,L2,L3],{0},{1},{2},{3},{4},{5}".format(self.motorDirection, self.motorFreq, self.breakVoltage, currentIL1, currentIL2, currentIL3))
                eocrLogger.debug("{0},{1},{2},{3},{4},{5}".format(self.motorDirection, self.motorFreq, self.breakVoltage, currentIL1, currentIL2, currentIL3))
            
                time.sleep(0.1)
 
            ### Exit ###
            if self.__exit:
                break

    def setMotorInfo(self, dir, freq):
        self.motorDirection = dir
        self.motorFreq = freq

    def setBreakVoltage(self, voltage):
        self.breakVoltage = voltage  

    def setMotorBreakInfo(self, dir, freq, voltage):
        self.motorDirection = dir
        self.motorFreq = freq
        self.breakVoltage = voltage  

    def eocrSuspend(self):
        log.logger.debug("EOCR Therad Suspend")
        self.__suspend = True
         
    def eocrResume(self):
        log.logger.debug("EOCR Therad Resume")
        self.__suspend = False
         
    def eocrExit(self):
        log.logger.debug("EOCR Therad Exit")        
        self.__exit = True

    