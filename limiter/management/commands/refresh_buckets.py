import redis
import logging

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    ''' Updates the buckets in redis server that are present
    with respect to refresh rate defined in settings.py.
    '''
    help = 'Refill tokens in the bucket'

    def handle(self, *args, **kwargs):
        redis_client = redis.StrictRedis(host='localhost', port=6379, db=1)
        try:
            # Check if the server is up
            response = redis_client.ping()
            logging.info("Redis is connected")
        except redis.exceptions.ConnectionError as e:
            logging.info("Redis is not connected")
            # Add retry logic if required here
        
        # Get all the keys present in redis cache
        # and update the values present with 1
        for key in redis_client.keys():
            value = redis_client.get(key)
            value = int(value) + 1
            
            # Check if the value is less than bucket size=
            if value <= settings.BUCKET_SIZE:
                redis_client.set(key, value)

        logging.info("Bucket has been updated with token ")
        