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

from pprint import pprint

import tests
# from tests.utils import execute

# Need to do something smarter on importing the connection information
# like line #96 of nova-trunk/smoketests/base.py
TEST_HOST = "10.127.52.133"
TEST_PORT = "9292"

class TestGlanceAPI(tests.FunctionalTest):
    def test_001_connect_to_glance_api(self):
        path = "http://%s:%s/images" % (TEST_HOST,TEST_PORT)
        http = httplib2.Http()
        response,content = http.request(path, 'GET')
	self.assertEqual(200, response.status)
        self.assertEqual('{"images": []}', content)

    def test_002_upload_image_to_glance_api(self):
        path = "http://%s:%s/images" % (TEST_HOST,TEST_PORT)
        headers = {'x-image-meta-is-public': 'true',
                   'x-image-meta-name': 'test-image',
                   'x-image-meta-disk-format': 'raw',
                   'Content-Type': 'application/octet-stream'}
        image_file = open("openwrt-x86-ext2.image", "rb")
	body = image_file.read(8)
        http = httplib2.Http()
        response,content = http.request(path, 'POST', headers=headers, body=body)
        self.assertEqual(201, response.status)
        # pprint(content)
	data = json.loads(content)
	self.glance['image_id'] = data['image']['id']
	self.assertEqual(data['image']['name'], "test-image")

    def test_999_delete_image_from_glance_api(self):
        path = "http://%s:%s/images/%s" % (TEST_HOST,TEST_PORT,self.glance['image_id'])
        http = httplib2.Http()
        response,content = http.request(path, 'DELETE')
        self.assertEqual(200, response.status)
