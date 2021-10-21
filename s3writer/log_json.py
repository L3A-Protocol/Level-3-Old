import os
from dotenv import load_dotenv
from osbot_utils.utils.Json import str_to_json, json_to_str, json_parse


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

        if body:
            try:
                log.update(body)          
            finally:
                pass

        print (json_to_str(log, indent=0).replace('\n',''))

if __name__ == '__main__':
    log = log_json()
    log.create("Error","Something happened")
    log.create("Error","Something happened",{"more":{"details":"Noting special"}})

