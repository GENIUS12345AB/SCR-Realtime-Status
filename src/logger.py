import logging
import sys
import os

def stream_supports_colour(stream) -> bool:
    is_a_tty = hasattr(stream, "isatty") and stream.isatty()
    if 'PYCHARM_HOSTED' in os.environ or os.environ.get('TERM_PROGRAM') == 'vscode':
        return is_a_tty
    elif sys.platform != 'win32':
        return is_a_tty
    else:
        return is_a_tty and ('ANSICON' in os.environ or 'WT_SESSION' in os.environ)

class ColourFormatter(logging.Formatter):
    LEVEL_COLOURS = {
        logging.DEBUG: '\x1b[40;1m',    
        logging.INFO: '\x1b[34;1m',     
        logging.WARNING: '\x1b[33;1m',  
        logging.ERROR: '\x1b[31m',      
        logging.CRITICAL: '\x1b[41m',   
    }

    def format(self, record):
        colour = self.LEVEL_COLOURS.get(record.levelno, '\x1b[0m')
        formatter = logging.Formatter(
            
            f'\x1b[30;1m%(asctime)s\x1b[0m {colour}%(levelname)-8s\x1b[0m \x1b[35m%(filename)s\x1b[0m %(message)s',
            "%H:%M:%S"
        )
        return formatter.format(record)

def CreateLogger(level=logging.INFO):
    logger = logging.getLogger()
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        if stream_supports_colour(handler.stream):
            handler.setFormatter(ColourFormatter())
        else:
            handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)-8s] %(message)s', "%H:%M:%S"))
        logger.addHandler(handler)
        logger.setLevel(level)
    return logger

log = CreateLogger(logging.INFO)
NOTSET = logging.NOTSET