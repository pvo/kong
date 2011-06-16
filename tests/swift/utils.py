import os
import socket
import sys
from httplib import HTTPException, HTTPConnection, HTTPSConnection
from time import sleep
from urlparse import urlparse, urlunparse

conf = {
    'auth_host': "10.127.52.134",
    'auth_port': "443",
    'auth_prefix': "/auth/",
    'auth_ssl': "yes",
    'account': 'system',
    'username': 'root',
    'password': 'citrix',
}

# If no conf was read, we will fall back to old school env vars
swift_test_auth = os.environ.get('SWIFT_TEST_AUTH')
swift_test_user = [os.environ.get('SWIFT_TEST_USER'), None, None]
swift_test_key = [os.environ.get('SWIFT_TEST_KEY'), None, None]


def get_auth(url, user, key, snet=False):
    """
    Get authentication/authorization credentials.

    The snet parameter is used for Rackspace's ServiceNet internal network
    implementation. In this function, it simply adds *snet-* to the beginning
    of the host name for the returned storage URL. With Rackspace Cloud Files,
    use of this network path causes no bandwidth charges but requires the
    client to be running on Rackspace's ServiceNet network.

    :param url: authentication/authorization URL
    :param user: user to authenticate as
    :param key: key or password for authorization
    :param snet: use SERVICENET internal network (see above), default is False
    :returns: tuple of (storage URL, auth token)
    :raises Exceptions: HTTP GET request to auth URL failed
    """
    parsed, conn = http_connection(url)
    conn.request('GET', parsed.path, '',
                 {'X-Auth-User': user, 'X-Auth-Key': key})
    resp = conn.getresponse()
    resp.read()
    if resp.status < 200 or resp.status >= 300:
        raise Exception('Auth GET failed')
    url = resp.getheader('x-storage-url')
    if snet:
        parsed = list(urlparse(url))
        # Second item in the list is the netloc
        parsed[1] = 'snet-' + parsed[1]
        url = urlunparse(parsed)
    return url, resp.getheader('x-storage-token',
                                                resp.getheader('x-auth-token'))

if conf:
    swift_test_auth = 'http'
    if conf.get('auth_ssl', 'no').lower() in ('yes', 'true', 'on', '1'):
        swift_test_auth = 'https'
    if 'auth_prefix' not in conf:
        conf['auth_prefix'] = '/'
    try:
        swift_test_auth += \
                '://%(auth_host)s:%(auth_port)s%(auth_prefix)sv1.0' % conf
    except KeyError:
        pass  # skip
    if 'account' in conf:
        swift_test_user[0] = '%(account)s:%(username)s' % conf
    else:
        swift_test_user[0] = '%(username)s' % conf
    swift_test_key[0] = conf['password']
    try:
        swift_test_user[1] = '%s%s' % ('%s:' % conf['account2'] if 'account2'
                                       in conf else '', conf['username2'])
        swift_test_key[1] = conf['password2']
    except KeyError, err:
        pass  # old conf, no second account tests can be run
    try:
        swift_test_user[2] = '%s%s' % ('%s:' % conf['account'] if 'account'
                                       in conf else '', conf['username3'])
        swift_test_key[2] = conf['password3']
    except KeyError, err:
        pass  # old conf, no third account tests can be run

skip = not all([swift_test_auth, swift_test_user[0], swift_test_key[0]])
if skip:
    print >>sys.stderr, 'SKIPPING FUNCTIONAL TESTS DUE TO NO CONFIG'


class AuthError(Exception):
    pass


class InternalServerError(Exception):
    pass


url = [None, None, None]
token = [None, None, None]
parsed = [None, None, None]
conn = [None, None, None]


def http_connection(url):
    """
    Make an HTTPConnection or HTTPSConnection

    :param url: url to connect to
    :returns: tuple of (parsed url, connection object)
    :raises ClientException: Unable to handle protocol scheme
    """
    parsed = urlparse(url)
    if parsed.scheme == 'http':
        conn = HTTPConnection(parsed.netloc)
    elif parsed.scheme == 'https':
        conn = HTTPSConnection(parsed.netloc)
    else:
        raise Exception('Cannot handle protocol scheme %s for url %s' %
                              (parsed.scheme, repr(url)))
    return parsed, conn


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
        except AuthError, _:
            url[use_account] = token[use_account] = None
            continue
        except InternalServerError, _:
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
