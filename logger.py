import logging
import logging.handlers

#logger instance를 만든다
logger = logging.getLogger("myLogger")

#Formater 를 만든다.
fomatter = logging.Formatter('[%(levelname)s|%(filename)s : %(lineno)s] %(asctime)s -> %(meaasge)s')

#스트림과 파일로 로그를 출력하는 핸들러를 만든다
#fileHandler = logging.FileHandler("./myLogger.log")
fileMaxByte = 1024 * 1024 * 100 # 100 MB
fileBackupCount = 5
fileHandler = logging.handlers.RotatingFileHandler("./myLogger.log", fileMaxByte, fileBackupCount)
streamHandler = logging.StreamHandler(fomatter)

#로그에 핸들러를 붙인다
logger.addHandler(fileHandler)
logger.addHandler(streamHandler)

logger.setLevel(logging.DEBUG)