# eocr.py
"""[summary]


[description]
"""

import logger as log
from pyModbusTCP.client import ModbusClient

SERVER_HOST = "localhost"
SERVER_PORT = 502

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

if __name__ == '__main__':
    client = ModbusClient(SERVER_HOST, SERVER_PORT, auto_open=True)
    if not client.is_open():
        if not client.open():
            log.logger.error("Modudbus TCP Open ERROR !!!")
    
    if client.is_open():
        currentIL1 = client.read_holding_register(522, 2)
        currentIL2 = client.read_holding_register(524, 2)
        currentIL3 = client.read_holding_register(526, 2)
        log.logger.debug("IL1 Current : {0}".format(currentIL1))
        log.logger.debug("IL2 Current : {0}".format(currentIL2))
        log.logger.debug("IL3 Current : {0}".format(currentIL3))
        
        
    