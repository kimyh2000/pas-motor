import logging
import logging.handlers
 
# 1. 로거 인스턴스를 만든다
logger = logging.getLogger('mylogger')

# 2. 포매터를 만든다
fomatter = logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')
#fomatter = logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s] %(msecs)d > %(message)s')
 
# 3. 스트림과 파일로 로그를 출력하는 핸들러를 각각 만든다.
#fileHandler = logging.FileHandler('./myLoggerTest.log')
fileMaxByte = 1024 * 1024 * 100 # 100 MB
fileBackupCount = 10
fileHandler = logging.handlers.RotatingFileHandler("./myLogger.log", fileMaxByte, fileBackupCount)
streamHandler = logging.StreamHandler()
 
# 4. 각 핸들러에 포매터를 지정한다.
fileHandler.setFormatter(fomatter)
streamHandler.setFormatter(fomatter)

# 5. 1번에서 만든 로거 인스턴스에 스트림 핸들러와 파일핸들러를 붙인다.
logger.addHandler(fileHandler)
logger.addHandler(streamHandler)
 
# 6. 로거 레벨을 설정한다.
logger.setLevel(logging.DEBUG)