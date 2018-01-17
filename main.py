
import logger as log
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
import time

import inverter as inv
import nrtgt100 as nrt
import eocr

#import inverterSim as invSim

form_class = uic.loadUiType("inverterUI.ui")[0]

class InvWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)          # UI Wiget의 생성 및 바인딩을 수행한다. 
        self.initializeUiSignal()   # UI Wiget의 Signal / Slot 을 설정한다.
        self.initializeDevice()     # Comm Port 초기화 및 Inverter의 상태를 읽어온다.
        
    def initializeDevice(self):
        self.inveter = inv.CInverter('COM5')
        self.nrtGT100 = nrt.CNRTGT100(0, 'COM6')
        self.eocr = eocr.CEOCRTest()
        self.eocr.daemon = True
        self.eocr.start()
        self.updateInverterStatus()
        self.btnClicked_ChangeFreq()
        self.btnClicked_ChangeOutVoltage()

    def updateInverterStatus(self):
        self.inveter.getInverterStatus()
        #for Debgging
        self.inveter.updateInverterStatus()
        
        data = "Model is LS {0}".format(self.inveter.Model)
        self.textEdit_InvInfo.append(data)

        data = "Power is {0}".format(self.inveter.power)
        self.textEdit_InvInfo.append(data)

        data = "Input Voltage is {0}".format(self.inveter.inputValtage)
        self.textEdit_InvInfo.append(data)

        data = "Software Version is 0x{0:02x}".format(self.inveter.version)
        self.textEdit_InvInfo.append(data)

        #data = "Command Frequency is {0}".format(self.inveter.commandFreq)
        #self.textEdit_InvInfo.append(data)

        #data = "Operating Command is {0:x}".format(self.inveter.opCommand)
        #self.textEdit_InvInfo.append(data)

        data = "Accelation time is {0}".format(self.inveter.accelTime)
        self.textEdit_InvInfo.append(data)

        data = "Decelation time is {0}".format(self.inveter.decelTime)
        self.textEdit_InvInfo.append(data)

        #data = "Output Frequency is {0}".format(self.inveter.outputFreq)
        #self.textEdit_InvInfo.append(data)

        #data = "Motor RPM is {0}".format(self.inveter.rpm)
        #self.textEdit_InvInfo.append(data)

        
    def initializeUiSignal(self):
        # inverter button signal
        self.pushButton_Update.clicked.connect(self.btnClicked_Update)
        self.pushButton_FrontRun.clicked.connect(self.btnClicked_FrontRun)
        self.pushButton_BackRun.clicked.connect(self.btnClicked_BackRun)
        self.pushButton_Stop.clicked.connect(self.btnClicked_Stop)
        self.pushButton_EMGStop.clicked.connect(self.btnClicked_EMGStop)
        self.pushButton_ErrorReset.clicked.connect(self.btnClicked_ErrorReset)
        self.pushButton_ChangeFreq.clicked.connect(self.btnClicked_ChangeFreq)
        self.pushButton_SetAccelTime.clicked.connect(self.btnClicked_SetAccelTime)
        self.pushButton_SetDecelTime.clicked.connect(self.btnClicked_SetDecelTime)
        self.pushButton_SetOpTime.clicked.connect(self.btnClicked_SetOpTime)
        self.pushButton_SetMovingDistance.clicked.connect(self.btnClicked_SetMovingDistance)

        # break button signal
        self.pushButton_BreakStop.clicked.connect(self.btnClicked_BreakStop)
        self.pushButton_BreakRun.clicked.connect(self.btnClicked_BreakRun)
        self.pushButton_ChangeOutVoltage.clicked.connect(self.btnClicked_ChangeOutVoltage)

        # quit program signal
        self.pushButton_Exit.clicked.connect(self.btnClicked_Exit)
        self.pushButton_Exit.setVisible(False)

        # Edit command frequency
        self.lineEdit_Frq.setAlignment(Qt.AlignRight)
        self.lineEdit_Frq.setValidator(QDoubleValidator(0.00, 60.00, 2))    # 0.00 Hz : Min, 60.00 Hz : Max
        self.lineEdit_Frq.editingFinished.connect(self.textChanged_Frq)
        self.lineEdit_Frq.setText("30.00")  # Default Value : 40.00 Hz
        self.invCommandFraq = int(float(self.lineEdit_Frq.text()) * 100)

        # Edit Accelation time
        self.lineEdit_AccTime.setAlignment(Qt.AlignRight)
        self.lineEdit_AccTime.setValidator(QIntValidator(0, 6000))
        self.lineEdit_AccTime.editingFinished.connect(self.textChanged_AccTime)
        self.lineEdit_AccTime.setText("5")

        # Edit decelation time
        self.lineEdit_DecTime.setAlignment(Qt.AlignRight)
        self.lineEdit_DecTime.setText("10")
        self.lineEdit_DecTime.setValidator(QIntValidator(0, 6000))
        self.lineEdit_DecTime.editingFinished.connect(self.textChanged_DecTime)

        # Edit others (doesn't use)
        self.lineEdit_OpTime.textChanged.connect(self.textChanged_OpTime)
        self.lineEdit_Dist.textChanged.connect(self.textChanged_Dist)

        self.lineEdit_OutVol.setAlignment(Qt.AlignRight)
        self.lineEdit_OutVol.setValidator(QDoubleValidator(0.0, 24.0, 1))    # 0.0 V : Min, 24.0 V : Max
        self.lineEdit_OutVol.textChanged.connect(self.textChanged_OutVol)
        self.lineEdit_OutVol.setText("0.0")  # Default Value : 0.0 V
        self.breakOutVol = int(float(self.lineEdit_OutVol.text()) * 10)

        # Show inveter information
        self.textEdit_InvInfo.setReadOnly(True)
        self.textEdit_InvInfo.setAlignment(Qt.AlignLeft)
        self.textEdit_InvInfo.clear()
        

    def textChanged_Frq(self):
        strValue = self.lineEdit_Frq.text()
        self.invCommandFraq = int(float(self.lineEdit_Frq.text()) * 100)
        log.logger.debug("textChanged_Frq : Command Frequency is {0}, {1:d}".format(strValue, self.invCommandFraq))
        #self.inveter.sendParameter('CommandFreq', self.invCommandFraq)
        

    def textChanged_AccTime(self):
        strValue = self.lineEdit_AccTime.text()
        self.invAccTime = int(strValue)
        log.logger.debug("textChanged_AccTime : Acceleation time is {0}, {1:d}".format(strValue, self.invAccTime))
        #self.inveter.sendParameter('AccelTime', valueAccTime)
 
    def textChanged_DecTime(self):
        strValue = self.lineEdit_DecTime.text()
        self.invDecTime = int(strValue)
        log.logger.debug("textChanged_DecTime : Deceleation time is {0}, {1:d}".format(strValue, self.invDecTime))
        #self.inveter.sendParameter('DecelTime', self.invDecTime)

    def textChanged_OpTime(self):
        pass

    def textChanged_Dist(self):
        pass

    def textChanged_OutVol(self):
        strValue = self.lineEdit_OutVol.text()
        self.breakOutVol = int(float(self.lineEdit_OutVol.text()) * 10)
        log.logger.debug("textChanged_OutVol : Command Voltage is {0}, {1:d}".format(strValue, self.breakOutVol))
    
    # setup buttons slot 
    def btnClicked_Update(self):
        log.logger.debug("btnClicked_Update : Command is INVERTER STATUS")
        self.textEdit_InvInfo.clear()
        self.updateInverterStatus()
    
    def btnClicked_FrontRun(self):
        log.logger.debug("btnClicked_FrontRun : Command is FRONT RUN")
        self.inveter.runMotor(True)
        self.eocr.setMotorInfo('F', self.invCommandFraq / 100)
        self.eocr.setBreakVoltage(self.breakOutVol / 10)
        self.eocr.eocrResume()

        self.pushButton_FrontRun.setEnabled(False)
        self.pushButton_BackRun.setEnabled(False)       

    def btnClicked_BackRun(self):
        log.logger.debug("btnClicked_FrontRun : Command is BACK RUN")
        self.inveter.runMotor(False)
        self.eocr.setMotorInfo('R', self.invCommandFraq / 100)
        self.eocr.setBreakVoltage(self.breakOutVol / 10)
        self.eocr.eocrResume()

        self.pushButton_FrontRun.setEnabled(False)
        self.pushButton_BackRun.setEnabled(False)       


    def btnClicked_Stop(self):
        log.logger.debug("btnClicked_Stop : Command is motor STOP")
        self.inveter.motorStop()
        self.eocr.eocrSuspend()

        self.pushButton_FrontRun.setEnabled(True)
        self.pushButton_BackRun.setEnabled(True)       

    def btnClicked_EMGStop(self):
        log.logger.debug("btnClicked_EMGStop : Command is motor FEEE RUN STOP")
        self.inveter.motorStop(True)
        self.eocr.eocrSuspend()        

        self.pushButton_FrontRun.setEnabled(True)
        self.pushButton_BackRun.setEnabled(True)       


    def btnClicked_ErrorReset(self):
        log.logger.debug("btnClicked_ErrorReset : Command is motor TRIP RESET")
        self.inveter.motorFaultReset()

    def btnClicked_ChangeFreq(self):
        log.logger.debug("btnClicked_ChangeFreq : Command Frequency is {0:d}".format(self.invCommandFraq))
        self.inveter.sendParameter('CommandFreq', self.invCommandFraq)

    def btnClicked_SetAccelTime(self):
        log.logger.debug("btnClicked_SetAccelTime : Acceleation time is {0:d}".format(self.invAccTime))
        self.inveter.sendParameter('AccelTime', self.invAccTime)
        
    def btnClicked_SetDecelTime(self):
        log.logger.debug("textChanged_DecTime : Deceleation time is {0:d}".format(self.invDecTime))
        self.inveter.sendParameter('DecelTime', self.invDecTime)
        
    def btnClicked_SetOpTime(self):
        pass
        
    def btnClicked_SetMovingDistance(self):
        pass
        
    def btnClicked_BreakStop(self):
        log.logger.debug("btnClicked_BreakStop")
        self.breakOutVol = 0
        self.nrtGT100.sendRequest(True, False, 0)
        
    def btnClicked_BreakRun(self):
        strValue = self.lineEdit_OutVol.text()
        self.breakOutVol = int(float(self.lineEdit_OutVol.text()) * 10)
        log.logger.debug("btnClicked_BreakRun : Command Voltage is {0:d}".format(self.breakOutVol))
        self.nrtGT100.sendRequest(True, True, self.breakOutVol)
    
    def btnClicked_ChangeOutVoltage(self):
        strValue = self.lineEdit_OutVol.text()
        self.breakOutVol = int(float(self.lineEdit_OutVol.text()) * 10)
        log.logger.debug("btnClicked_ChangeOutVoltage : Command Voltage is {0:d}".format(self.breakOutVol))
        self.nrtGT100.sendRequest(True, True, self.breakOutVol)

        
    def btnClicked_Exit(self):
        pass

    def closeEvent(self, event):
        log.logger.debug("$$$$$$$$$ UI 종료함 $$$$$$$$$$$$$")
        self.eocr.eocrExit()
        #self.eocr.join()
        time.sleep(1)

        self.deleteLater()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = InvWindow()
    myWindow.show()
    sys.exit(app.exec_())   
