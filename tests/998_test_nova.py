# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 OpenStack, LLC
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Functional test case against the OpenStack Nova API server"""

import json
import os
import tempfile
import unittest
import httplib2
import urllib
import hashlib
import time

from pprint import pprint

import tests

from tests.config import get_config

# Need to do something smarter on importing the connection information
# like line #96 of nova-trunk/smoketests/base.py
NOVA_API_HOST = get_config("nova/host")
NOVA_API_PORT = get_config("nova/port")
NOVA_API_VER = get_config("nova/apiver")
NOVA_API_USER = get_config("nova/user")
NOVA_API_KEY = get_config("nova/key")


class TestNovaAPI(tests.FunctionalTest):
    def test_001_verify_nova_auth(self):
        path = "http://%s:%s/%s" % (NOVA_API_HOST, NOVA_API_PORT,
                                    NOVA_API_VER)
        http = httplib2.Http()
        headers = {'X-Auth-User': '%s' % (NOVA_API_USER),
                   'X-Auth-Key': '%s' % (NOVA_API_KEY)}
        response, content = http.request(path, 'HEAD', headers=headers)
        self.assertEqual(204, response.status)

        # Set up Auth Token for all future API interactions
        for key, val in response.items():
            if (key == 'x-auth-token'):
                self.nova['X-Auth-Token'] = val

    def test_003_list_flavors_v1_1(self):
        path = "http://%s:%s/%s/flavors" % (NOVA_API_HOST, NOVA_API_PORT,
                                            NOVA_API_VER)
        http = httplib2.Http()
        headers = {'X-Auth-User': '%s' % (NOVA_API_USER),
                   'X-Auth-Token': '%s' % (self.nova['X-Auth-Token'])}
        response, content = http.request(path, 'GET', headers=headers)
        self.assertEqual(200, response.status)
        self.assertNotEqual('{"flavors": []}', content)

    def test_004_verify_kernel_active_v1_1(self):
        # Change 180 in the URL string to self.glance['kernel_id']
        path = "http://%s:%s/%s/images/%s" % (NOVA_API_HOST, NOVA_API_PORT,
                                              NOVA_API_VER,
                                              self.glance['kernel_id'])
        http = httplib2.Http()
        headers = {'X-Auth-User': '%s' % (NOVA_API_USER),
                   'X-Auth-Token': '%s' % (self.nova['X-Auth-Token'])}
        response, content = http.request(path, 'GET', headers=headers)
        self.assertEqual(200, response.status)
        data = json.loads(content)
        self.assertEqual(data['image']['status'], 'ACTIVE')

    def test_005_verify_ramdisk_active_v1_1(self):
        # Change 181 in the URL string to self.glance['ramdisk_id']
        path = "http://%s:%s/%s/images/%s" % (NOVA_API_HOST, NOVA_API_PORT,
                                              NOVA_API_VER,
                                              self.glance['ramdisk_id'])
        http = httplib2.Http()
        headers = {'X-Auth-User': '%s' % (NOVA_API_USER),
                   'X-Auth-Token': '%s' % (self.nova['X-Auth-Token'])}
        response, content = http.request(path, 'GET', headers=headers)
        self.assertEqual(200, response.status)
        data = json.loads(content)
        self.assertEqual(data['image']['status'], 'ACTIVE')

    def test_006_verify_image_active_v1_1(self):
        # Change 182 in the URL string to self.glance['image_id']
        path = "http://%s:%s/%s/images/%s" % (NOVA_API_HOST, NOVA_API_PORT,
                                              NOVA_API_VER,
                                              self.glance['image_id'])
        http = httplib2.Http()
        headers = {'X-Auth-User': '%s' % (NOVA_API_USER),
                   'X-Auth-Token': '%s' % (self.nova['X-Auth-Token'])}
        response, content = http.request(path, 'GET', headers=headers)
        self.assertEqual(200, response.status)
        data = json.loads(content)
        self.assertEqual(data['image']['status'], 'ACTIVE')

    def test_007_create_server(self):
        path = "http://%s:%s/%s/servers" % (NOVA_API_HOST, NOVA_API_PORT,
                                            NOVA_API_VER)
        http = httplib2.Http()
        headers = {'X-Auth-User': '%s' % (NOVA_API_USER),
                   'X-Auth-Token': '%s' % (self.nova['X-Auth-Token']),
                   'Content-Type': 'application/json'}

        # Change imageRef to self.glance['image_id']
        json_str = {"server":
            {
                "name": "testing server creation",
                "flavorRef": "http://%s:%s/%s/flavors/3" % (NOVA_API_HOST,
                                             NOVA_API_PORT, NOVA_API_VER),
                "imageRef": "http://%s:%s/%s/images/%s" % (NOVA_API_HOST,
                                             NOVA_API_PORT, NOVA_API_VER,
                                             self.glance['image_id'])
            }
        }
        data = json.dumps(json_str)
        response, content = http.request(path, 'POST', headers=headers,
                                         body=data)
        json_return = json.loads(content)
        self.assertEqual(200, response.status)
        self.assertEqual(json_return['server']['status'], "BUILD")
        self.nova['server_id'] = json_return['server']['id']

    def test_008_server_exits_build(self):
        count = 0
        path = "http://%s:%s/%s/servers/%s" % (NOVA_API_HOST, NOVA_API_PORT,
                                       NOVA_API_VER, self.nova['server_id'])
        http = httplib2.Http()
        headers = {'X-Auth-User': '%s' % (NOVA_API_USER),
                   'X-Auth-Token': '%s' % (self.nova['X-Auth-Token'])}
        response, content = http.request(path, 'GET', headers=headers)
        self.assertEqual(200, response.status)
        data = json.loads(content)
        while (data['server']['status'] != 'ACTIVE'):
            response, content = http.request(path, 'GET', headers=headers)
            data = json.loads(content)
            time.sleep(10)
            count = count + 10
        self.assertEqual(data['server']['status'], "ACTIVE")
        data = json.loads(content)
        while (data['server']['status'] != 'ACTIVE'):
            response, content = http.request(path, 'GET', headers=headers)
            data = json.loads(content)
            time.sleep(10)
            count = count + 10
        self.assertEqual(data['server']['status'], "ACTIVE")

    def test_009_create_multiple(self):
        path = "http://%s:%s/%s/servers" % (NOVA_API_HOST, NOVA_API_PORT,
                                            NOVA_API_VER)
        http = httplib2.Http()
        headers = {'X-Auth-User': '%s' % (NOVA_API_USER),
                   'X-Auth-Token': '%s' % (self.nova['X-Auth-Token']),
                   'Content-Type': 'application/json'}

        for i in range(1, 10):
            print i
            # Change imageRef to self.glance['image_id']
            json_str = {"server":
                {
                    "name": "test %s" % (i),
                    "flavorRef": "http://%s:%s/%s/flavors/3" % (
                            NOVA_API_HOST, NOVA_API_PORT,
                            NOVA_API_VER),
                    "imageRef": "http://%s:%s/%s/images/%s" % (
                            NOVA_API_HOST, NOVA_API_PORT,
                            NOVA_API_VER, self.glance['image_id'])
                }
            }
            data = json.dumps(json_str)
            response, content = http.request(path, 'POST', headers=headers,
                                             body=data)
            json_return = json.loads(content)
            self.assertEqual(200, response.status)
            self.assertEqual(json_return['server']['status'], "BUILD")
