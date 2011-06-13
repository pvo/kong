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

from pprint import pprint

import tests

NOVA_API_HOST = "10.127.52.126"
NOVA_API_PORT = "8774"
NOVA_API_VER = "v1.1"
NOVA_API_USER = "dashboard"
NOVA_API_KEY = "ef81eccc-172c-4aad-810b-05278bbdbbf3"

class TestNovaAPI(tests.FunctionalTest):
    def test_001_verify_nova_auth(self):
        path = "http://%s:%s/%s" % (NOVA_API_HOST, NOVA_API_PORT, NOVA_API_VER)
        http = httplib2.Http()
        headers = {'X-Auth-User' : '%s' % (NOVA_API_USER),
                   'X-Auth-Key' : '%s' % (NOVA_API_KEY) }
        response, content = http.request(path, 'HEAD', headers=headers)
        self.assertEqual(204, response.status)

	# Set up Auth Token for all future API interactions
	for key,val in response.items():
		if (key == 'x-auth-token'):
			self.nova['X-Auth-Token'] = val

    def test_002_list_images(self):
	path = "http://%s:%s/%s/images" % (NOVA_API_HOST, NOVA_API_PORT, NOVA_API_VER)
	http = httplib2.Http()
	headers = {'X-Auth-User' : '%s' % (NOVA_API_USER),
		   'X-Auth-Token' : '%s' % (self.nova['X-Auth-Token']) }
	response, content = http.request(path, 'GET', headers=headers)
	# self.assertEqual(200, response.status)
        # self.assertEqual('{"images": []}', content)
	pprint(self.glance['ramdisk_id'])

    def test_003_list_servers(self):
	path = "http://%s:%s/%s/servers" % (NOVA_API_HOST, NOVA_API_PORT, NOVA_API_VER)
	http = httplib2.Http()
	headers = {'X-Auth-User' : '%s' % (NOVA_API_USER),
		   'X-Auth-Token' : '%s' % (self.nova['X-Auth-Token']) }
	response, content = http.request(path, 'GET', headers=headers)
	self.assertEqual(200, response.status)
    	self.assertEqual('{"servers": []}', content)