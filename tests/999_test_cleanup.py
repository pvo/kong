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

"""Functional test case that utilizes cURL against the API server"""

import json
import os
import tempfile
import unittest
import httplib2
import urllib
import hashlib

from pprint import pprint

import tests

# GLANCE API TESTS Variables
TEST_HOST = "10.127.52.133"
TEST_PORT = "9292"

<<<<<<< HEAD
# NOVA API TESTS Variables
NOVA_API_HOST = "10.127.52.126"
NOVA_API_PORT = "8774"
NOVA_API_VER = "v1.1"
NOVA_API_USER = "dashboard"
NOVA_API_KEY = "ef81eccc-172c-4aad-810b-05278bbdbbf3"
=======
>>>>>>> 59980563e94c01f9b3abde938d6156076bbdb91b

class TestCleanUp(tests.FunctionalTest):
    def test_996_delete_server(self):
	path = "http://%s:%s/%s/servers/%s" % ( NOVA_API_HOST, NOVA_API_PORT, NOVA_API_VER, self.nova['server_id'])
	http = httplib2.Http()
	headers = {'X-Auth-User' : '%s' % (NOVA_API_USER),
                   'X-Auth-Token' : '%s' % (self.nova['X-Auth-Token']) }
	response, content = http.request(path, 'DELETE', headers=headers)
	self.assertEqual(204, response.status)
	
    def test_997_delete_kernel_from_glance(self):
        path = "http://%s:%s/images/%s" % (TEST_HOST, TEST_PORT, self.glance['kernel_id'])
        http = httplib2.Http()
        # response, content = http.request(path, 'DELETE')
        # self.assertEqual(200, response.status)

    def test_998_delete_initrd_from_glance(self):
        path = "http://%s:%s/images/%s" % (TEST_HOST, TEST_PORT, self.glance['ramdisk_id'])
        http = httplib2.Http()
        # response, content = http.request(path, 'DELETE')
        # self.assertEqual(200, response.status)

    def test_999_delete_image_from_glance_api(self):
        path = "http://%s:%s/images/%s" % (TEST_HOST, TEST_PORT, self.glance['image_id'])
        http = httplib2.Http()
        # response, content = http.request(path, 'DELETE')
        # self.assertEqual(200, response.status)
