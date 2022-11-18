from typing import Union


chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ().+-*/?<>_0123456789"

def convert_to_words(val: int, size: int) -> str:
        n_chars = len(chars)
        words = []
        for _ in range(size - 1):
            words.append(val%n_chars)
            val = val // n_chars
        
        words.append(val)
        msg = ''
        for word in words:
            msg += chars[word]
        
        return msg

def convert_to_int(msg: str)  -> Union[int, None]:
    if msg == '':
        return None
    
    msg = msg[::-1]
    
    n_chars = len(chars)
    digit = len(msg) - 1
    
    val: int = 0
    
    for c in msg:
        i = chars.find(c)
        val += i * int(n_chars**digit)
        digit -= 1
    
    return val