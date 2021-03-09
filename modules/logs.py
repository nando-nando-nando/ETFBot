import logging
import logging.handlers
import os
streamLevel="INFO"

def setupLogger(name, logFormat, streamFormat, logDateFormat, streamDateFormat, streamLevel, logDebugFile, logInfoFile):
    logger = logging.getLogger()

    logFormatter = logging.Formatter(logFormat, datefmt=logDateFormat)
    streamFormatter = logging.Formatter(streamFormat, datefmt=streamDateFormat)
    logger.setLevel(os.environ.get("LOGLEVEL", "DEBUG"))

    # Log all root debug to file 
    file_handler_debug = logging.handlers.TimedRotatingFileHandler(
        filename=logDebugFile, 
        when='midnight', 
        backupCount=45)
    file_handler_debug.setFormatter(logFormatter)
    file_handler_debug.setLevel(os.environ.get("LOGLEVEL", "DEBUG"))

    # Log all root info to file 
    file_handler_info = logging.handlers.TimedRotatingFileHandler(
        filename=logInfoFile, 
        when='midnight', 
        backupCount=45)
    file_handler_info.setFormatter(logFormatter)
    file_handler_info.setLevel(os.environ.get("LOGLEVEL", "INFO"))

    # Log all root info to stdout
    handler = logging.StreamHandler()
    handler.setFormatter(streamFormatter)
    handler.setLevel(os.environ.get("LOGLEVEL", streamLevel))

    logger.addHandler(file_handler_debug)
    logger.addHandler(file_handler_info)
    logger.addHandler(handler)

    return logger
