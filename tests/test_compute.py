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

TEST_HOST = "10.127.52.126"
TEST_PORT = "8774"
TEST_VER = "v1.1"
TEST_USER = "dashboard"
TEST_KEY = "ef81eccc-172c-4aad-810b-05278bbdbbf3"

class TestComputeAPI(tests.FunctionalTest):
    def test_001_connect_to_compute_api(self):
    	path = "http://%s:%s/%s" % (TEST_HOST, TEST_PORT, TEST_VER)
    	http = httplib2.Http()
	headers = {'X-Auth-User' : '%s' % (TEST_USER),
		   'X-Auth-Key' : '%s' % (TEST_KEY) }
	response, content = http.request(path, 'GET', headers=headers)
        self.assertEqual(204, response.status)
        
