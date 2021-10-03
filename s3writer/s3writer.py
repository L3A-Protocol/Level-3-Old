import os
import sys
import errno
from dotenv import load_dotenv
from osbot_utils.utils.Files import file_exists
from osbot_utils.utils.Json import str_to_json

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

load_dotenv(override=True)
c_bin_path = os.getenv("C_BINARY_PATH", None)
topic      = os.getenv("TOPIC", None)

if not c_bin_path:
    print ("The binary path is not specified")
    sys.exit()

if not topic:
    print ("The topic is not specified")
    sys.exit()

if not file_exists(c_bin_path):
    print (f"File {c_bin_path} does not exist")
    sys.exit()

FIFO = f'/tmp/{topic}'

try:
    os.system(f'{c_bin_path} --topic {topic} &')
except OSError as oe: 
    if oe.errno != errno.EEXIST:
        print (f'Failed to start {c_bin_path}')
        sys.exit()

try:
    os.mkfifo(FIFO)
except OSError as oe: 
    if oe.errno != errno.EEXIST:
        print (f"Failed to create the pipe: {FIFO}")
        sys.exit()

print("Opening FIFO...")
with open(FIFO) as fifo:
    print("FIFO opened")
    while True:
        # data = fifo.read()
        line = readline(fifo)
        if len(line) == 0:
            print("Writer closed")
            break
        print (line)
        try:
            data = str_to_json(line)
            if "cross_seq" in data:
                print(data["cross_seq"])
        except Exception as ex:
            print (ex)