import logging
from typing import Union

import coloredlogs
import sys


def get_logger(unum: Union[int, str] = None, on_file=False):
    logging.basicConfig()
    logger = logging.getLogger(name='mylogger')
    coloredlogs.install(logger=logger)
    logger.propagate = False
    coloredFormatter = coloredlogs.ColoredFormatter(
        datefmt='%H:%M:%S:%s',
        fmt=f'%(asctime)s %(filename)s %(lineno)-3d {unum} %(message)s',
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
    if on_file:
        if unum == 'coach':
            file_name = 'coach.txt'
        elif unum > 0:
            file_name = f'player-{unum}.txt'
        else:
            file_name = f'coach-log.txt'
        ch = logging.StreamHandler(stream=open(file_name, 'w'))
        ch.setFormatter(logging.Formatter('%(asctime)s %(filename)s %(lineno)-3d  %(message)s',
                                          '%H:%M:%S:%s'))
    else:
        ch = logging.StreamHandler(stream=sys.stdout)
        ch.setFormatter(fmt=coloredFormatter)
    logger.addHandler(hdlr=ch)
    logger.setLevel(level=logging.DEBUG)
    return logger

# logger = get_logger()
# logger.setLevel(level=logging.ERROR)
# logger.debug(msg="this is a debug message")
# logger.info(msg="this is an info message")
# logger.warning(msg="this is a warning message")
# logger.error(msg="this is an error message")
# logger.critical(msg="this is a critical message")
