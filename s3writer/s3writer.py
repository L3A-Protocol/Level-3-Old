import os
import sys
import errno

FIFO = '/tmp/instrument_info.100ms.BTCUSD'

def readline(fifo):
    line = ''
    try:
        while True:
            line += fifo.read(1)
            if line.endswith('\n'):
                break
    except:
        pass
    return line

try:
    os.mkfifo(FIFO)
except OSError as oe: 
    if oe.errno != errno.EEXIST:
        raise

print("Opening FIFO...")
with open(FIFO) as fifo:
    print("FIFO opened")
    while True:
        # data = fifo.read()
        data = readline(fifo)
        if len(data) == 0:
            print("Writer closed")
            break
        print(data)