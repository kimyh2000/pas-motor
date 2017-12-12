
import logger as log
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic

import inverter as inv
#import inverterSim as invSim

form_class = uic.loadUiType("inverterUI.ui")[0]

class InvWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)          # UI Wiget의 생성 및 바인딩을 수행한다. 
        self.initializeUiSignal()   # UI Wiget의 Signal / Slot 을 설정한다.
        self.initializeDevice()     # Comm Port 초기화 및 Inverter의 상태를 읽어온다.
        
    def initializeDevice(self):
        self.inveter = inv.CInverter('COM4')
        self.updateInverterStatus()

    def updateInverterStatus(self):
        self.inveter.getInverStatus()
        #for Debgging
        self.inveter.updateInverterStatus()
        
        data = "Model is LS {0}".format(self.inveter.Model)
        self.textEdit_InvInfo.append(data)

        data = "Power is {0:d}".format(self.inveter.power)
        self.textEdit_InvInfo.append(data)

        data = "Input Voltage is {0:d}".format(self.inveter.inputValtage)
        self.textEdit_InvInfo.append(data)

        data = "Software Version is {0}".format(self.inveter.version)
        self.textEdit_InvInfo.append(data)

        data = "Command Frequency is {0}".format(self.inveter.commandFreq)
        self.textEdit_InvInfo.append(data)

        data = "Operating Command is {0:x}".format(self.inveter.opCommand)
        self.textEdit_InvInfo.append(data)

        data = "Accelation time is {0}".format(self.inveter.accelTime)
        self.textEdit_InvInfo.append(data)

        data = "Decelation time is {0}".format(self.inveter.decelTime)
        self.textEdit_InvInfo.append(data)

        data = "Output Frequency is {0}".format(self.inveter.outputFreq)
        self.textEdit_InvInfo.append(data)

        data = "Motor RPM is {0}".format(self.inveter.rpm)
        self.textEdit_InvInfo.append(data)

        
    def initializeUiSignal(self):
        # inverter button signal
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

        self.lineEdit_Frq.setAlignment(Qt.AlignRight)
        self.lineEdit_Frq.setText("100")
        self.lineEdit_Frq.setValidator(QIntValidator(0, 100))
        self.lineEdit_Frq.editingFinished.connect(self.textChanged_Frq)

        self.lineEdit_AccTime.setAlignment(Qt.AlignRight)
        self.lineEdit_AccTime.setText("-1.234")
        self.lineEdit_AccTime.setValidator(QDoubleValidator(-10.000, 100.000, 3))
        self.lineEdit_AccTime.editingFinished.connect(self.textChanged_AccTime)


        self.lineEdit_DecTime.textChanged.connect(self.textChanged_DecTime)
        self.lineEdit_OpTime.textChanged.connect(self.textChanged_OpTime)
        self.lineEdit_Dist.textChanged.connect(self.textChanged_Dist)
        self.lineEdit_OutVol.textChanged.connect(self.textChanged_OutVol)

        self.textEdit_InvInfo.setReadOnly(True)
        self.textEdit_InvInfo.setAlignment(Qt.AlignLeft)
        self.textEdit_InvInfo.clear()
        


    def textChanged_Frq(self):
        newvalue = self.lineEdit_Frq.text()
        log.logger.debug("------ New Current {0} --------".format(newvalue))
        QMessageBox.about(self, "문자 변경", newvalue)
        

    def textChanged_AccTime(self):
        newvalue = self.lineEdit_AccTime.text()
        log.logger.debug("------ New Current {0} --------".format(newvalue))
        QMessageBox.about(self, "가속시간 변경", newvalue)
 
    def textChanged_DecTime(self):
        pass

    def textChanged_OpTime(self):
        pass

    def textChanged_Dist(self):
        pass

    def textChanged_OutVol(self):
        pass
    
    # setup buttons slot 
    def btnClicked_FrontRun(self):
        QMessageBox.about(self, "정회전", "정회전 동작 시작")
        self.inveter.runMotor(True)

    def btnClicked_BackRun(self):
        QMessageBox.about(self, "역회전", "역회전 동작 시작")
        self.inveter.runMotor(False)

    def btnClicked_Stop(self):
        QMessageBox.about(self, "정지", "정지 버튼 누름")
        self.inveter.motorStop()

    def btnClicked_EMGStop(self):
        self.inveter.motorStop(True)
        
    def btnClicked_ErrorReset(self):
        self.inveter.motorFaultReset()

    def btnClicked_ChangeFreq(self):
        pass

    def btnClicked_SetAccelTime(self):
        pass
        
    def btnClicked_SetDecelTime(self):
        pass
        
    def btnClicked_SetOpTime(self):
        pass
        
    def btnClicked_SetMovingDistance(self):
        pass
        
    def btnClicked_BreakStop(self):
        pass
        
    def btnClicked_BreakRun(self):
        pass      
    
    def btnClicked_ChangeOutVoltage(self):
        pass
        
    def btnClicked_Exit(self):
        pass

def print_menu():
    print("1. 인버터 상태")
    print("2. 모터 정방향 회전")
    print("3. 모터 역방향 회전")
    print("4. 모터 정지")
    print("5. 모터 긴급 정지")
    print("6. 모터 에러 리셋")
    print("7. 종료")
    menu = input("select No.")
    return int(menu)

def run():
    inveter = inv.CInverter('COM4')

    while True:
        menu = print_menu()
        if menu == 1:
            inveter.getInverStatus()
            inveter.updateInverterStatus()
        elif menu == 2:
            inveter.runMotor(True)
        elif menu == 3:
            inveter.runMotor(False)
        elif menu == 4:
            inveter.motorStop()
        elif menu == 5:
            inveter.motorStop(True)
        elif menu == 6:
            inveter.motorFaultReset()
        elif menu == 7:
            break




if __name__ == "__main__":
#    invThread = invSim.CInverterSim("COM5")
#    invThread.daemon = True
#    invThread.start()

#    run()            
    app = QApplication(sys.argv)
    myWindow = InvWindow()
    myWindow.show()
    app.exec_()   
