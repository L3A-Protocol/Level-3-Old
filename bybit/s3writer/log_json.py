import json

class log_json(object):

    def create(self, type, message, body = None):

        log = {'type': type, "message": message}
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

