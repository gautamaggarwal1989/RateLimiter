from time import sleep

from celery import shared_task
from django.core import management


# Create a task for the command
@shared_task
def refresh_bucket():
    ''' Task layering the command for refreshing buckets.
    '''
    management.call_command('refresh_buckets')
