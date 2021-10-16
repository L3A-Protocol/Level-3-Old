import os
from dotenv import load_dotenv

c_bin_path  = os.getenv("C_BINARY_PATH", 'none')
topic       = os.getenv("TOPIC", 'none')

class log_json(object):

    def create(self, type, message, body = None):

        log = {'metadata':
                {
                    'binary':   c_bin_path,
                    'topic':    topic
                },
                'type':     type,
                "message":  message
            }

        if not body:
            print (log)
            return

        try:
            log.update(body)
            print(log)
        finally:
            pass

if __name__ == '__main__':
    log = log_json()
    log.create("Error","Something happened")
    log.create("Error","Something happened",{"more":{"details":"Noting special"}})

