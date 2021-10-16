import os
from dotenv import load_dotenv

exchange    = os.getenv("EXCHANGE", 'none')
topic       = os.getenv("TOPIC", 'none')

class log_json(object):

    def create(self, type, message, body = None):

        log = {'metadata':
                {
                    'exchange': exchange,
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

