from nameko import config
from nameko.extensions import DependencyProvider
import redis

from products.exceptions import NotFound


REDIS_URI_KEY = 'REDIS_URI'


class StorageWrapper:
    """
    Product storage

    A very simple example of a custom Nameko dependency. Simplified
    implementation of products database based on Redis key value store.
    Handling the product ID increments or keeping sorted sets of product
    names for ordering the products is out of the scope of this example.

    """

    NotFound = NotFound

    def __init__(self, client):
        self.client = client

    def _format_key(self, product_id):
        return 'products:{}'.format(product_id)

    # def _from_hash(self, document):
    #     return {
    #         'id': document[b'id'].decode('utf-8'),
    #         'title': document[b'title'].decode('utf-8'),
    #         'passenger_capacity': int(document[b'passenger_capacity']),
    #         'maximum_speed': int(document[b'maximum_speed']),
    #         'in_stock': int(document[b'in_stock'])
    #     }
    def _from_hash(self, document): #made the following changes because I was getting a decoding error. Saved error on local for documentation.
        def decode_bytes(key):
            # Check if the key exists in the dictionary before decoding
            if key in document:
                return document[key].decode('utf-8')
            return None  # Return None if the key does not exist
        return {
            'id': decode_bytes(b'id'),
            'title': decode_bytes(b'title'),
            'passenger_capacity': int(decode_bytes(b'passenger_capacity') or 0),  # Handle missing or invalid values
            'maximum_speed': int(decode_bytes(b'maximum_speed') or 0),  # Handle missing or invalid values
            'in_stock': int(decode_bytes(b'in_stock') or 0)  # Handle missing or invalid values
        }


    def get(self, product_id):
        product = self.client.hgetall(self._format_key(product_id))
        if not product:
            raise NotFound('Product ID {} does not exist'.format(product_id))
        else:
            return self._from_hash(product)

    def list(self):
        keys = self.client.keys(self._format_key('*'))
        for key in keys:
            yield self._from_hash(self.client.hgetall(key))

    def create(self, product):
        self.client.hmset(
            self._format_key(product['id']),
            product)

    def decrement_stock(self, product_id, amount):
        return self.client.hincrby(
            self._format_key(product_id), 'in_stock', -amount)

    def delete(self, product_id):
        key = self._format_key(product_id)
        deleted = self.client.delete(key)
        if not deleted:
            raise NotFound(f'Product with ID {product_id} not found')

class Storage(DependencyProvider):

    def setup(self):
        self.client = redis.StrictRedis.from_url(config.get(REDIS_URI_KEY))

    def get_dependency(self, worker_ctx):
        return StorageWrapper(self.client)
