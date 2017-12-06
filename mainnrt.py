
import nrtgt100 as nrt

def print_menu():
    print("1. NRTGT100 상태")
    print("2. NRTGT100 RUN")
    print("3. NRTGT100 STOP")
    print("4. 종료")
    menu = input("select No.")
    return int(menu)

def run():
    nrtGT100 = nrt.CNRTGT100(0, 'COM4')

    while True:
        menu = print_menu()
        if menu == 1:
            nrtGT100.sendRequest(False, 0x30)
        elif menu == 2:
            nrtGT100.sendRequest(True, 0x31, 0x0F)
        elif menu == 3:
            nrtGT100.sendRequest(True, 0x30, 0x11)
        elif menu == 4:
            break


if __name__ == "__main__":
#    invThread = invSim.CInverterSim("COM5")
#    invThread.daemon = True
#    invThread.start()

    run()       