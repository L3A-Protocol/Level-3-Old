import os
from opensearchpy import OpenSearch
from dotenv import load_dotenv
from osbot_utils.utils.Http import GET_json, GET
from base64 import b64encode

class OpenSearchClient(object):

    def __init__(self):
        load_dotenv(override=True)
        self.host = os.getenv("OPENSEARCH_HOST", '')
        self.port = int(os.getenv("OPENSEARCH_PORT", 443))
        self.schema = 'https'
        user = os.getenv("OPENSEARCH_USER", '')
        psw  = os.getenv("OPENSEARCH_PASSWORD", '')
        authstr   = (f'{user}:{psw}').encode("ascii")
        userAndPass = b64encode(authstr).decode("ascii")
        self.headers = { 'Authorization' : 'Basic %s' %  userAndPass }

        # Create the client with SSL/TLS enabled, but hostname verification disabled.
        self.client = OpenSearch(
            hosts = [{'host': self.host, 'port': self.port}],
            http_compress = True, # enables gzip compression for request bodies
            http_auth = (user, psw),
            use_ssl = True,
            verify_certs = False,
            ssl_assert_hostname = False,
            ssl_show_warn = False,
        )

        self.enabled = False

    def server_online(self):
        elastic_url = f'{self.schema}://{self.host}:{self.port}'
        try:
            response = GET_json(elastic_url, headers=self.headers).get('tagline')
            assert response == "The OpenSearch Project: https://opensearch.org/"
            self.enabled = True
            return True
        except:
            return False

    def create_index(self, index_name):

        if not self.enabled:
            return False

        try:
            self.client.indices.delete(index_name)
        except Exception as ex:
            print(ex)
            return False

        index_body = {
            'settings': {
                'index': {
                'number_of_shards': 4
                }
            }
        }

        try:
            response = self.client.indices.create(index_name, body=index_body)
            # print(response)
        except Exception as ex:
            print(ex)
            return False
        return True

    def add_document(self, index_name, id, document):
        if not self.enabled:
            return False

        try:
            response = self.client.index(
                index = index_name,
                body = document,
                id = id,
                refresh = True
            )
            # print(response)
        except Exception as ex:
            print(ex)
            return False
        return True


def test_it():
    osclient = OpenSearchClient()

    print(osclient.client.info)
    print(osclient.server_online())


    # Create an index with non-default settings.
    index_name = 'python-test-index'
    print('\nCreating index:')
    osclient.create_index(index_name)

    # Add a document to the index.
    document = {
    'title': 'Moneyball',
    'director': 'Bennett Miller',
    'year': '2011'
    }
    id = '1'

    print('\nAdding document:')
    osclient.add_document(index_name, id, document)

    # Search for the document.
    q = 'miller'
    query = {
    'size': 5,
    'query': {
        'multi_match': {
        'query': q,
        'fields': ['title^2', 'director']
        }
    }
    }

    response = osclient.client.search(
        body = query,
        index = index_name
    )
    print('\nSearch results:')
    print(response)

    # Delete the document.
    response = osclient.client.delete(
        index = index_name,
        id = id
    )

    print('\nDeleting document:')
    print(response)

    # Delete the index.
    response = osclient.client.indices.delete(
        index = index_name
    )

    print('\nDeleting index:')
    print(response)


# test_it()