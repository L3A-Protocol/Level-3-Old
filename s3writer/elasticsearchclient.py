import os
import datetime
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
from osbot_utils.utils.Http import GET_json, GET
from base64 import b64encode

class ElasticsearchClient(object):

    def __init__(self):
        load_dotenv(override=True)
        self.host           = os.getenv("ELASTIC_HOST", '')
        self.port           = int(os.getenv("ELASTIC_PORT", 9200))
        self.kibana_port    = int(os.getenv("KIBANA_PORT", 5601))
        self.schema         = os.getenv("ELASTIC_SCHEMA", 'http')
        self.url            = f'{self.schema}://{self.host}:{self.port}'

        self.client = Elasticsearch([self.url])
        self.enabled = False
        self.server_online()

        if not self.enabled:
            print('Elasticsearch client failed to connect')

    def server_online(self):
        try:
            response = GET_json(self.url).get('tagline')
            assert response == "You Know, for Search"
            self.enabled = True
            return True
        except:
            return False

    def delete_index(self, index_name):
        response = None

        if not self.enabled:
            return None

        try:
            response = self.client.indices.delete(index=[index_name], request_timeout=20)
        except Exception as ex:
            print(ex)
            return None

        return response

class Index(object):
    def __init__(self, client:ElasticsearchClient, prefix:str, exchange:str, topic:str, taskid:str ):
        self.esclient = client
        self.taskid = taskid
        self.name = f'{prefix}-{taskid}'
        self.id = 0

        self.exchage = exchange
        self.topic = topic

    def delete(self):
        return self.esclient.delete_index(f'{self.name}*')

    def index_name(self, timestamp = None):
        if not timestamp:
            timestamp = datetime.datetime.utcnow()        
        return f'{self.name}-{timestamp.year}-{timestamp.month}-{timestamp.day}'

    def add_document(self, document, timestamp = None):
        response = None

        if not self.esclient.enabled:
            return None

        self.id += 1

        try:
            if not timestamp:
                timestamp = datetime.datetime.utcnow()

            data = {
                "timestamp" : timestamp.isoformat(),
                "exchange"  : self.exchage,
                "topic"     : self.topic,
                "taskid"    : self.taskid,
                "indexid"   : f'{self.exchage}-{self.topic}-{self.taskid}',
                "document"  : document
            }
            response = self.esclient.client.index(
                index = self.index_name(timestamp),
                id = self.id,
                document = data,
                refresh = True,
                request_timeout=20
            )
        except Exception as ex:
            print(ex)
            return None

        return response

    def delete_document(self, id):
        response = None
        try:
            response = self.esclient.client.delete(
                    index = self.index_name(),
                    id = id,
                    request_timeout=20
                )
        except Exception as ex:
            print(ex)
        return response

def delete_indexes(list):
    esclient = ElasticsearchClient()
    for item in list:
        print(f'Deleting {item}')
        print(esclient.delete_index(item))

def test_it():
    print('\nConnecting:')
    esclient = ElasticsearchClient()

    print('\nCreating index:')
    test_index = Index(client=esclient,prefix='python-test-index',exchange='ByBit',topic='kline',taskid='123456789')

    document = {
    'title': 'Moneyball',
    'director': 'Bennett Miller',
    'year': '2011'
    }

    print('\nAdding document:')
    print(test_index.add_document(document))

    print('\nDeleting document:')
    print(test_index.delete_document(test_index.id))

    print('\nDeleting index:')
    print(test_index.delete())

    esclient.delete_index("")

if __name__ == '__main__':
    # test_it()

    list = ['sysinfo-*', 'price-*', 'datafeed-*']
    delete_indexes(list=list)