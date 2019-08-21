
import nrtgt100 as nrt

def print_menu():
    print("1. NRTGT100 상태")
    print("2. Set Voltage")
    print("3. NRTGT100 RUN")
    print("4. NRTGT100 STOP")
    print("5. 종료")
    menu = input("select No.")
    return int(menu)

def run():
    nrtGT100 = nrt.CNRTGT100(1, 'COM5')

    while True:
        menu = print_menu()
        if menu == 1:
            nrtGT100.getStatus()
        elif menu == 2: # Set Voltage
            nrtGT100.setVoltage(113) #16.6V
        elif menu == 3: # Start
            nrtGT100.run()
        elif menu == 4: # Stop
            nrtGT100.stop()
        elif menu == 5:
            break


if __name__ == "__main__":
#    invThread = invSim.CInverterSim("COM5")
#    invThread.daemon = True
#    invThread.start()

    run()        