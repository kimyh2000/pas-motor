

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
        
    
    def initializeUiSignal(self):
        self.pushButton_Stop.clicked.connect(self.btnClicked_Stop)
        self.pushButton_FrontRun.clicked.connect(self.btnClicked_FrontRun)
        self.pushButton_BackRun.clicked.connect(self.btnClicked_BackRun)

    #def setupUi(self):
        #self.btnClicked_Stop()
        #self.pushButton_Stop.clicked.connect(self.btnClicked_Stop)
        #pushButton_FrontRun.clicked.connect(self.btnClicked_FrontRun)
        #pushButton_BackRun.clicked.connect(self.btnClicked_BackRun)

    def btnClicked_Stop(self):
        QMessageBox.about(self, "정지", "정지 버튼 누름")

    def btnClicked_FrontRun(self):
        QMessageBox.about(self, "정회전", "정회전 동작 시작")

    def btnClicked_BackRun(self):
        QMessageBox.about(self, "역회전", "역회전 동작 시작")


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
            
