''' Include this file in MIDDLEWARE list in settings.py file.
Set the bucket size and refresh rate, expiry rate for token bucket
algorithm for rate limiting.

'''
import logging
from datetime import datetime, timedelta

import redis
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.http import JsonResponse


TIMESTAMP_FORMAT = "%d-%m-%Y %H:%M:%S"


class BaseRateLimiter(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        self.redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

    def __call__(self, request):
        if not self.eligible_for_serving(request):
            return JsonResponse({'error': 'rate limited'}, status=429)

        response = self.get_response(request)
        return response

    def eligible_for_serving(self, request):
        raise NotImplementedError('Base Rate limiter function called!')

    def get_ip_address(self, request):
        '''
            Extracts IP address from a given request object.
        '''
        # HTTP_X_FORWARDED_FOR is key to check for in case proxy is
        # being used by client. But if key is absent, It means that
        # IP will be present in REMOTE_ADDR`
        return request.META.get(
            'HTTP_X_FORWARDED_FOR',
            request.META.get('REMOTE_ADDR')
        )


class TokenBucketRateLimiterMiddleware(BaseRateLimiter):

    def eligible_for_serving(self, request):
        ip_address = self.get_ip_address(request)
        logging.info(f"Got request from IP Address:- {str(ip_address)}")

        if bytes(ip_address, 'utf-8') not in self.redis_client.keys():
            # Request has been made first time or after a very long time.
            self.redis_client.set(ip_address, 0)
            return True

        token_count = int(self.redis_client.get(ip_address))
        if token_count == 0:
            return False

        self.redis_client.set(ip_address, token_count-1)
        return True


class FixedWindowRateLimiterMiddleware(BaseRateLimiter):
    ''' Fixed window counter of time period defined in
    settings file. Each subsequent request increases a counter
    for given ip and if the number exceeds the threshold limit
    for a given request. The request is rejected.'''

    def refresh_required(self, ip_address, current_timestamp):
        ''' If request has been made first time or after
        a pre defined window time that has been set in
        settings.py, A new entry needs to be made in redis
        for the given ip address. '''

        if bytes(ip_address, 'utf-8') in self.redis_client.keys():
            prev_req_time_bytes = self.redis_client.hget(ip_address, 'request_time')
            prev_req_time_str = prev_req_time_bytes.decode()
            prev_req_time_obj = datetime.strptime(prev_req_time_str, TIMESTAMP_FORMAT)
            time_diff = current_timestamp - prev_req_time_obj
            window_period = timedelta(seconds=settings.FIXED_WINDOW_TIME_PERIOD)

            return time_diff > window_period

        return True


    def eligible_for_serving(self, request):
        ''' 
        There are four possible cases with a fixed window
        algorithm for request rate limiting.

        If a given request has been made first time or the last request from same IP was made
        a window time period, IP address is re-initiated for values.
        else
        required count is checked for given IP address and count is increased
        if it is still under the limit else request is rejected.
        '''
        ip_address = self.get_ip_address(request)
        logging.info(f"Got request from IP Address:- {str(ip_address)}")

        # Get current timestamp.
        current_timestamp = datetime.now()

        if self.refresh_required(ip_address, current_timestamp):
            self.redis_client.hset(
                ip_address,
                'request_time',
                current_timestamp.strftime(TIMESTAMP_FORMAT)
            )
            self.redis_client.hset(
                ip_address,
                'request_count',
                0
            )
            return True

        req_count = int(self.redis_client.hget(ip_address, 'request_count'))

        if req_count >= settings.FIXED_WINDOW_REQUEST_THRESHOLD:
            return False

        self.redis_client.hset(
            ip_address,
            'request_count',
            req_count + 1
        )

        return True