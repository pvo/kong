import tests
import os
import socket
import sys
from httplib import HTTPException, HTTPConnection, HTTPSConnection
from time import sleep
from urlparse import urlparse, urlunparse
from tests.config import get_config
from pprint import pprint

def retry(func, *args, **kwargs):
       """
       You can use the kwargs to override the 'retries' (default: 5) and
       'use_account' (default: 1).
       """
       global url, token, parsed, conn
       retries = kwargs.get('retries', 5)
       use_account = 1
       if 'use_account' in kwargs:
           use_account = kwargs['use_account']
           del kwargs['use_account']
       use_account -= 1
       attempts = 0
       backoff = 1
       while attempts <= retries:
           attempts += 1
           try:
               if not url[use_account] or not token[use_account]:
                   url[use_account], token[use_account] = \
                       get_auth(swift_test_auth, swift_test_user[use_account],
                                swift_test_key[use_account])
                   parsed[use_account] = conn[use_account] = None
               if not parsed[use_account] or not conn[use_account]:
                   parsed[use_account], conn[use_account] = \
                       http_connection(url[use_account])
               return func(url[use_account], token[use_account],
                          parsed[use_account], conn[use_account], *args, **kwargs)
           except (socket.error, HTTPException):
               if attempts > retries:
                   raise
               parsed[use_account] = conn[use_account] = None
           except AuthError:
               url[use_account] = token[use_account] = None
               continue
           except InternalServerError:
               pass
           if attempts <= retries:
               sleep(backoff)
               backoff *= 2
       raise Exception('No result after %s retries.' % retries)


def check_response(conn):
   resp = conn.getresponse()
   if resp.status == 401:
          resp.read()
          raise AuthError()
   elif resp.status // 100 == 5:
          resp.read()
          raise InternalServerError()
   return resp
