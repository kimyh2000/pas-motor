

import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic

import inverter as inv
#import inverterSim as invSim

form_class = uic.loadUiType("inverterUI.ui")[0]

class InvWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)          # UI Wiget의 생성 및 바인딩을 수행한다. 
        self.initializeUiSignal()   # UI Wiget의 Signal / Slot 을 설정한다.
        #self.initializeDevice()
        
    def initializeDevice(self):
        self.inveter = inv.CInverter('COM4')
        self.updateInverterStatus()

    def updateInverterStatus(self):
        self.inveter.getInverStatus()
        self.inveter.updateInverterStatus()
        
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

        self.textEdit_Frq.textChanged.connect(self.textChanged_Frq)
        

    def textChanged_Frq(self):
        self.newFreq = self.textEdit_Frq.document()
        print("------ New Current %s --------" % self.newFreq)
        QMessageBox.about(self, self.newFreq, "변경")
        

    #def setupUi(self):

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
