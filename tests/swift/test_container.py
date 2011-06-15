#!/usr/bin/python

import json
import unittest
from uuid import uuid4

from constraints import MAX_META_COUNT, MAX_META_NAME_LENGTH, \
    MAX_META_OVERALL_SIZE, MAX_META_VALUE_LENGTH

from utils import check_response, retry


class TestContainer(unittest.TestCase):

    def setUp(self):
        self.name = uuid4().hex
        def put(url, token, parsed, conn):
            conn.request('PUT', parsed.path + '/' + self.name, '',
                         {'X-Auth-Token': token})
            return check_response(conn)
        resp = retry(put)
        resp.read()
        self.assertEquals(resp.status, 201)

    def tearDown(self):
        def get(url, token, parsed, conn):
            conn.request('GET', parsed.path + '/' + self.name + '?format=json',
                         '', {'X-Auth-Token': token})
            return check_response(conn)
        def delete(url, token, parsed, conn, obj):
            conn.request('DELETE',
                         '/'.join([parsed.path, self.name, obj['name']]), '',
                         {'X-Auth-Token': token})
            return check_response(conn)
        while True:
            resp = retry(get)
            body = resp.read()
            self.assert_(resp.status // 100 == 2, resp.status)
            objs = json.loads(body)
            if not objs:
                break
            for obj in objs:
                resp = retry(delete, obj)
                resp.read()
                self.assertEquals(resp.status, 204)
        def delete(url, token, parsed, conn):
            conn.request('DELETE', parsed.path + '/' + self.name, '',
                         {'X-Auth-Token': token})
            return check_response(conn)
        resp = retry(delete)
        resp.read()
        self.assertEquals(resp.status, 204)

    def test_multi_metadata(self):
        def post(url, token, parsed, conn, name, value):
            conn.request('POST', parsed.path + '/' + self.name, '',
                {'X-Auth-Token': token, name: value})
            return check_response(conn)
        def head(url, token, parsed, conn):
            conn.request('HEAD', parsed.path + '/' + self.name, '',
                         {'X-Auth-Token': token})
            return check_response(conn)
        resp = retry(post, 'X-Container-Meta-One', '1')
        resp.read()
        self.assertEquals(resp.status, 204)
        resp = retry(head)
        resp.read()
        self.assert_(resp.status in (200, 204), resp.status)
        self.assertEquals(resp.getheader('x-container-meta-one'), '1')
        resp = retry(post, 'X-Container-Meta-Two', '2')
        resp.read()
        self.assertEquals(resp.status, 204)
        resp = retry(head)
        resp.read()
        self.assert_(resp.status in (200, 204), resp.status)
        self.assertEquals(resp.getheader('x-container-meta-one'), '1')
        self.assertEquals(resp.getheader('x-container-meta-two'), '2')

    def test_PUT_metadata(self):
        def put(url, token, parsed, conn, name, value):
            conn.request('PUT', parsed.path + '/' + name, '',
                {'X-Auth-Token': token, 'X-Container-Meta-Test': value})
            return check_response(conn)
        def head(url, token, parsed, conn, name):
            conn.request('HEAD', parsed.path + '/' + name, '',
                         {'X-Auth-Token': token})
            return check_response(conn)
        def get(url, token, parsed, conn, name):
            conn.request('GET', parsed.path + '/' + name, '',
                         {'X-Auth-Token': token})
            return check_response(conn)
        def delete(url, token, parsed, conn, name):
            conn.request('DELETE', parsed.path + '/' + name, '',
                         {'X-Auth-Token': token})
            return check_response(conn)
        name = uuid4().hex
        resp = retry(put, name, 'Value')
        resp.read()
        self.assertEquals(resp.status, 201)
        resp = retry(head, name)
        resp.read()
        self.assert_(resp.status in (200, 204), resp.status)
        self.assertEquals(resp.getheader('x-container-meta-test'), 'Value')
        resp = retry(get, name)
        resp.read()
        self.assert_(resp.status in (200, 204), resp.status)
        self.assertEquals(resp.getheader('x-container-meta-test'), 'Value')
        resp = retry(delete, name)
        resp.read()
        self.assertEquals(resp.status, 204)

        name = uuid4().hex
        resp = retry(put, name, '')
        resp.read()
        self.assertEquals(resp.status, 201)
        resp = retry(head, name)
        resp.read()
        self.assert_(resp.status in (200, 204), resp.status)
        self.assertEquals(resp.getheader('x-container-meta-test'), None)
        resp = retry(get, name)
        resp.read()
        self.assert_(resp.status in (200, 204), resp.status)
        self.assertEquals(resp.getheader('x-container-meta-test'), None)
        resp = retry(delete, name)
        resp.read()
        self.assertEquals(resp.status, 204)

    def test_POST_metadata(self):
        def post(url, token, parsed, conn, value):
            conn.request('POST', parsed.path + '/' + self.name, '',
                {'X-Auth-Token': token, 'X-Container-Meta-Test': value})
            return check_response(conn)
        def head(url, token, parsed, conn):
            conn.request('HEAD', parsed.path + '/' + self.name, '',
                         {'X-Auth-Token': token})
            return check_response(conn)
        def get(url, token, parsed, conn):
            conn.request('GET', parsed.path + '/' + self.name, '',
                         {'X-Auth-Token': token})
            return check_response(conn)
        resp = retry(head)
        resp.read()
        self.assert_(resp.status in (200, 204), resp.status)
        self.assertEquals(resp.getheader('x-container-meta-test'), None)
        resp = retry(get)
        resp.read()
        self.assert_(resp.status in (200, 204), resp.status)
        self.assertEquals(resp.getheader('x-container-meta-test'), None)
        resp = retry(post, 'Value')
        resp.read()
        self.assertEquals(resp.status, 204)
        resp = retry(head)
        resp.read()
        self.assert_(resp.status in (200, 204), resp.status)
        self.assertEquals(resp.getheader('x-container-meta-test'), 'Value')
        resp = retry(get)
        resp.read()
        self.assert_(resp.status in (200, 204), resp.status)
        self.assertEquals(resp.getheader('x-container-meta-test'), 'Value')

    def test_PUT_bad_metadata(self):
        def put(url, token, parsed, conn, name, extra_headers):
            headers = {'X-Auth-Token': token}
            headers.update(extra_headers)
            conn.request('PUT', parsed.path + '/' + name, '', headers)
            return check_response(conn)
        def delete(url, token, parsed, conn, name):
            conn.request('DELETE', parsed.path + '/' + name, '',
                         {'X-Auth-Token': token})
            return check_response(conn)
        name = uuid4().hex
        resp = retry(put, name,
                {'X-Container-Meta-' + ('k' * MAX_META_NAME_LENGTH): 'v'})
        resp.read()
        self.assertEquals(resp.status, 201)
        resp = retry(delete, name)
        resp.read()
        self.assertEquals(resp.status, 204)
        name = uuid4().hex
        resp = retry(put, name,
               {'X-Container-Meta-' + ('k' * (MAX_META_NAME_LENGTH + 1)): 'v'})
        resp.read()
        self.assertEquals(resp.status, 400)
        resp = retry(delete, name)
        resp.read()
        self.assertEquals(resp.status, 404)

        name = uuid4().hex
        resp = retry(put, name,
                {'X-Container-Meta-Too-Long': 'k' * MAX_META_VALUE_LENGTH})
        resp.read()
        self.assertEquals(resp.status, 201)
        resp = retry(delete, name)
        resp.read()
        self.assertEquals(resp.status, 204)
        name = uuid4().hex
        resp = retry(put, name,
              {'X-Container-Meta-Too-Long': 'k' * (MAX_META_VALUE_LENGTH + 1)})
        resp.read()
        self.assertEquals(resp.status, 400)
        resp = retry(delete, name)
        resp.read()
        self.assertEquals(resp.status, 404)

        name = uuid4().hex
        headers = {}
        for x in xrange(MAX_META_COUNT):
            headers['X-Container-Meta-%d' % x] = 'v'
        resp = retry(put, name, headers)
        resp.read()
        self.assertEquals(resp.status, 201)
        resp = retry(delete, name)
        resp.read()
        self.assertEquals(resp.status, 204)
        name = uuid4().hex
        headers = {}
        for x in xrange(MAX_META_COUNT + 1):
            headers['X-Container-Meta-%d' % x] = 'v'
        resp = retry(put, name, headers)
        resp.read()
        self.assertEquals(resp.status, 400)
        resp = retry(delete, name)
        resp.read()
        self.assertEquals(resp.status, 404)

        name = uuid4().hex
        headers = {}
        header_value = 'k' * MAX_META_VALUE_LENGTH
        size = 0
        x = 0
        while size < MAX_META_OVERALL_SIZE - 4 - MAX_META_VALUE_LENGTH:
            size += 4 + MAX_META_VALUE_LENGTH
            headers['X-Container-Meta-%04d' % x] = header_value
            x += 1
        if MAX_META_OVERALL_SIZE - size > 1:
            headers['X-Container-Meta-k'] = \
                'v' * (MAX_META_OVERALL_SIZE - size - 1)
        resp = retry(put, name, headers)
        resp.read()
        self.assertEquals(resp.status, 201)
        resp = retry(delete, name)
        resp.read()
        self.assertEquals(resp.status, 204)
        name = uuid4().hex
        headers['X-Container-Meta-k'] = \
            'v' * (MAX_META_OVERALL_SIZE - size)
        resp = retry(put, name, headers)
        resp.read()
        self.assertEquals(resp.status, 400)
        resp = retry(delete, name)
        resp.read()
        self.assertEquals(resp.status, 404)

    def test_POST_bad_metadata(self):
        def post(url, token, parsed, conn, extra_headers):
            headers = {'X-Auth-Token': token}
            headers.update(extra_headers)
            conn.request('POST', parsed.path + '/' + self.name, '', headers)
            return check_response(conn)
        resp = retry(post,
                {'X-Container-Meta-' + ('k' * MAX_META_NAME_LENGTH): 'v'})
        resp.read()
        self.assertEquals(resp.status, 204)
        resp = retry(post,
               {'X-Container-Meta-' + ('k' * (MAX_META_NAME_LENGTH + 1)): 'v'})
        resp.read()
        self.assertEquals(resp.status, 400)

        resp = retry(post,
                {'X-Container-Meta-Too-Long': 'k' * MAX_META_VALUE_LENGTH})
        resp.read()
        self.assertEquals(resp.status, 204)
        resp = retry(post,
              {'X-Container-Meta-Too-Long': 'k' * (MAX_META_VALUE_LENGTH + 1)})
        resp.read()
        self.assertEquals(resp.status, 400)

        headers = {}
        for x in xrange(MAX_META_COUNT):
            headers['X-Container-Meta-%d' % x] = 'v'
        resp = retry(post, headers)
        resp.read()
        self.assertEquals(resp.status, 204)
        headers = {}
        for x in xrange(MAX_META_COUNT + 1):
            headers['X-Container-Meta-%d' % x] = 'v'
        resp = retry(post, headers)
        resp.read()
        self.assertEquals(resp.status, 400)

        headers = {}
        header_value = 'k' * MAX_META_VALUE_LENGTH
        size = 0
        x = 0
        while size < MAX_META_OVERALL_SIZE - 4 - MAX_META_VALUE_LENGTH:
            size += 4 + MAX_META_VALUE_LENGTH
            headers['X-Container-Meta-%04d' % x] = header_value
            x += 1
        if MAX_META_OVERALL_SIZE - size > 1:
            headers['X-Container-Meta-k'] = \
                'v' * (MAX_META_OVERALL_SIZE - size - 1)
        resp = retry(post, headers)
        resp.read()
        self.assertEquals(resp.status, 204)
        headers['X-Container-Meta-k'] = \
            'v' * (MAX_META_OVERALL_SIZE - size)
        resp = retry(post, headers)
        resp.read()
        self.assertEquals(resp.status, 400)

    def test_public_container(self):
        def get(url, token, parsed, conn):
            conn.request('GET', parsed.path + '/' + self.name)
            return check_response(conn)
        try:
            resp = retry(get)
            raise Exception('Should not have been able to GET')
        except Exception, err:
            self.assert_(str(err).startswith('No result after '), err)
        def post(url, token, parsed, conn):
            conn.request('POST', parsed.path + '/' + self.name, '',
                         {'X-Auth-Token': token,
                          'X-Container-Read': '.r:*,.rlistings'})
            return check_response(conn)
        resp = retry(post)
        resp.read()
        self.assertEquals(resp.status, 204)
        resp = retry(get)
        resp.read()
        self.assertEquals(resp.status, 204)
        def post(url, token, parsed, conn):
            conn.request('POST', parsed.path + '/' + self.name, '',
                         {'X-Auth-Token': token, 'X-Container-Read': ''})
            return check_response(conn)
        resp = retry(post)
        resp.read()
        self.assertEquals(resp.status, 204)
        try:
            resp = retry(get)
            raise Exception('Should not have been able to GET')
        except Exception, err:
            self.assert_(str(err).startswith('No result after '), err)


if __name__ == '__main__':
    unittest.main()
