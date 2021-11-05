import os
from opensearchpy import OpenSearch
from dotenv import load_dotenv

class OpenSearchClient(object):

    def __init__(self):
        load_dotenv(override=True)
        host = os.getenv("OPENSEARCH_HOST", '')
        port = int(os.getenv("OPENSEARCH_PORT", 443))
        user = os.getenv("OPENSEARCH_USER", '')
        psw  = os.getenv("OPENSEARCH_PASSWORD", '')

        # Create the client with SSL/TLS enabled, but hostname verification disabled.
        self.client = OpenSearch(
            hosts = [{'host': host, 'port': port}],
            http_compress = True, # enables gzip compression for request bodies
            http_auth = (user, psw),
            use_ssl = True,
            verify_certs = False,
            ssl_assert_hostname = False,
            ssl_show_warn = False,
        )

    def create_index(self, index_name):
        index_body = {
            'settings': {
                'index': {
                'number_of_shards': 4
                }
            }
        }

        try:
            response = self.client.indices.create(index_name, body=index_body)
            print(response)
        except Exception as ex:
            print(ex)
            return False
        return True

    def add_document(self, index_name, id, document):
        try:
            response = self.client.index(
                index = index_name,
                body = document,
                id = id,
                refresh = True
            )
            print(response)
        except Exception as ex:
            print(ex)
            return False
        return True

os_client = OpenSearchClient()

# Create an index with non-default settings.
index_name = 'python-test-index'
print('\nCreating index:')
os_client.create_index(index_name)

# Add a document to the index.
document = {
  'title': 'Moneyball',
  'director': 'Bennett Miller',
  'year': '2011'
}
id = '1'

print('\nAdding document:')
os_client.add_document(index_name, id, document)

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

response = os_client.client.search(
    body = query,
    index = index_name
)
print('\nSearch results:')
print(response)

# Delete the document.
response = os_client.client.delete(
    index = index_name,
    id = id
)

print('\nDeleting document:')
print(response)

# Delete the index.
response = os_client.client.indices.delete(
    index = index_name
)

print('\nDeleting index:')
print(response)


