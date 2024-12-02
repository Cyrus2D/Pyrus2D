import logging
from typing import Union
import datetime
import coloredlogs
import sys
import os
import team_config


def get_logger(unum: Union[int, str] = None):
    logging.basicConfig()
    logger = logging.getLogger(name='mylogger')
    coloredlogs.install(logger=logger)
    logger.propagate = False
    coloredFormatter = coloredlogs.ColoredFormatter(
        datefmt='%H:%M:%S:%s',
        fmt=f'%(asctime)s %(filename)s u{unum} %(lineno)-3d %(levelname)s %(message)s',
        level_styles=dict(
            debug=dict(color='white'),
            info=dict(color='green'),
            warning=dict(color='yellow', bright=True),
            error=dict(color='red', bold=True, bright=True),
            critical=dict(color='black', bold=True, background='red'),
        ),
        field_styles=dict(
            name=dict(color='white'),
            asctime=dict(color='white'),
            funcName=dict(color='white'),
            lineno=dict(color='white'),
        )
    )
    if unum == 'coach':
        file_name = 'coach.txt'
    elif unum > 0:
        file_name = f'player-{unum}.txt'
    else:
        file_name = f'before-set-log.txt'
    path = team_config.LOG_PATH
    
    # remove all handlers
    for handler in logger.handlers:
        logger.removeHandler(handler)

    file_ch = logging.StreamHandler(stream=open(f'{path}/{file_name}', 'w'))
    file_ch.setFormatter(logging.Formatter('%(asctime)s %(filename)s %(lineno)-3d  %(message)s',
                                        '%H:%M:%S:%s'))
    file_ch.setLevel(level=team_config.FILE_LOG_LEVEL)
    logger.addHandler(hdlr=file_ch)
    
    console_ch = logging.StreamHandler(stream=sys.stdout)
    console_ch.setFormatter(fmt=coloredFormatter)
    console_ch.setLevel(level=team_config.CONSOLE_LOG_LEVEL)
    logger.addHandler(hdlr=console_ch)
    return logger

# logger = get_logger()
# logger.setLevel(level=logging.ERROR)
# logger.debug(msg="this is a debug message")
# logger.info(msg="this is an info message")
# logger.warning(msg="this is a warning message")
# logger.error(msg="this is an error message")
# logger.critical(msg="this is a critical message")
