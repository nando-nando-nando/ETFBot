import logging
import logging.handlers
def setupLogger(name, logFormat, logDateFormat, logDebugFile, logInfoFile):
    logger = logging.getLogger(name)

    formatter = logging.Formatter(logFormat, datefmt=logDateFormat)
    logger.setLevel(logging.DEBUG)

    file_handler_debug = logging.handlers.TimedRotatingFileHandler(
        filename=logDebugFile, 
        when='midnight', 
        backupCount=45)
    file_handler_debug.setFormatter(formatter)
    file_handler_debug.setLevel(logging.DEBUG)

    file_handler_info = logging.handlers.TimedRotatingFileHandler(
        filename=logInfoFile, 
        when='midnight', 
        backupCount=45)
    file_handler_info.setFormatter(formatter)
    file_handler_info.setLevel(logging.INFO)

    logger.addHandler(file_handler_debug)
    logger.addHandler(file_handler_info)

    return logger
