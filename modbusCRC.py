"""
이 함수는 시리얼 modbus-RTU 프로토콜에서 CRC checksum을 만드는 알고리즘 이다.
실제 CRC를 프로토콜에 실어 보낼때는 CRC checksum을 Hi Byte, Low Byte로 분리한 후,
Low Byte를 먼저 전송한 후 Hi Byte를 전송한다. 
"""

def CRC16(Output):
    crc = 0xFFFF 
    dataLength = len(Output)
    i = 0
    while i < dataLength:
        j = 0
        crc = crc ^ Output[i]
        while j < 8:
            if (crc & 0x1):
                mask = 0xA001
            else:
                mask = 0x00
            crc = ((crc >> 1) & 0x7FFF) ^ mask
            j += 1
        i += 1
    if crc < 0:
        crc -= 256
    return crc

