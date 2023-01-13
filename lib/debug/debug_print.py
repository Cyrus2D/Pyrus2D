import datetime as dt
import inspect

FILE_LINE_NUMBER = False # SLows the runtime!
TIME = False

def debug_print(*messages):
        
    prefix = ""
    
    if TIME:
        current_time = dt.datetime.now()
        prefix += f"{current_time} "
    
    if FILE_LINE_NUMBER:
        current_frame = inspect.currentframe()
        outer_frame = inspect.getouterframes(current_frame, 1)
        prefix += f"{outer_frame[1].filename} {outer_frame[1].lineno}: "
    
    message = ""
    for m in messages:
        message += f"{m} "
    
    if len(message) > 0:
        message = message[:-1]

    print(f"{prefix}{message}")


def debug_frame():
    frames = inspect.getouterframes(inspect.currentframe(), 1)

    s = ''
    for frame in frames[1:]:
        s += f"({frame.filename}:{frame.lineno}): in {frame.function} called {frame.code_context[0].strip()}-> "
    print(s[:-2])