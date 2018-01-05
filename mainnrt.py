
import nrtgt100 as nrt

def print_menu():
    print("1. NRTGT100 상태")
    print("2. NRTGT100 RUN")
    print("3. NRTGT100 STOP")
    print("4. 종료")
    menu = input("select No.")
    return int(menu)

def run():
    nrtGT100 = nrt.CNRTGT100(0, 'COM6')

    while True:
        menu = print_menu()
        if menu == 1:
            nrtGT100.sendRequest(False, 0)
        elif menu == 2: # Start
            nrtGT100.sendRequest(True, True, 235)  #23.5 V
        elif menu == 3: # Start
            nrtGT100.sendRequest(True, True, 179) #
        elif menu == 4: # Stop
            nrtGT100.sendRequest(True, False, 179) #
        elif menu == 4:
            break


if __name__ == "__main__":
#    invThread = invSim.CInverterSim("COM5")
#    invThread.daemon = True
#    invThread.start()

    run()       