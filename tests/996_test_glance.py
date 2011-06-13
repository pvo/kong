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
# from tests.utils import execute

# Need to do something smarter on importing the connection information
# like line #96 of nova-trunk/smoketests/base.py
TEST_HOST = "10.127.52.133"
TEST_PORT = "9292"


class TestGlanceAPI(tests.FunctionalTest):
    def test_001_connect_to_glance_api(self):
        path = "http://%s:%s/images" % (TEST_HOST, TEST_PORT)
        http = httplib2.Http()
        response, content = http.request(path, 'GET')
        self.assertEqual(200, response.status)
        self.assertEqual('{"images": []}', content)

    def test_002_upload_kernel_to_glance(self):
	kernel = "sample_vm/vmlinuz-2.6.32-23-server"
        # md5sum = self._md5sum_file(kernel)
        # content_length = os.path.getsize(kernel)
        path = "http://%s:%s/images" % (TEST_HOST, TEST_PORT)
        headers = {'x-image-meta-is-public': 'true',
                   'x-image-meta-name': 'test-kernel',
                   'x-image-meta-disk-format': 'aki',
                   'x-image-meta-container-format': 'aki',
                   'Content-Length': '%d' % os.path.getsize(kernel),
                   'Content-Type': 'application/octet-stream'}
        image_file = open(kernel, "rb")
        http = httplib2.Http()
        response, content = http.request(path, 'POST', headers=headers, body=image_file)
        image_file.close()
        self.assertEqual(201, response.status)
        # pprint(content)
        data = json.loads(content)
        self.glance['kernel_id'] = data['image']['id']
        self.assertEqual(data['image']['name'], "test-kernel")
        self.assertEqual(data['image']['checksum'], self._md5sum_file(kernel))

    def test_003_upload_initrd_to_glance(self):
        initrd = "sample_vm/initrd.img-2.6.32-23-server"
        path = "http://%s:%s/images" % (TEST_HOST, TEST_PORT)
        headers = {'x-image-meta-is-public': 'true',
                   'x-image-meta-name': 'test-ramdisk',
                   'x-image-meta-disk-format': 'ari',
                   'x-image-meta-container-format': 'ari',
                   'Content-Length': '%d' % os.path.getsize(initrd),
                   'Content-Type': 'application/octet-stream'}
        image_file = open(initrd, "rb")
        http = httplib2.Http()
        response, content = http.request(path, 'POST', headers=headers, body=image_file)
        image_file.close()
        self.assertEqual(201, response.status)
        # pprint(content)
        data = json.loads(content)
        self.glance['ramdisk_id'] = data['image']['id']
        self.assertEqual(data['image']['name'], "test-ramdisk")
        self.assertEqual(data['image']['checksum'], self._md5sum_file(initrd))

    def test_004_upload_image(self):
        image = "sample_vm/ubuntu-lucid.img"
        upload_data = ""
        for chunk in self._read_in_chunks(image):
            upload_data += chunk
        path = "http://%s:%s/images" % (TEST_HOST, TEST_PORT)
        headers = {'x-image-meta-is-public': 'true',
                   'x-image-meta-name': 'test-image',
                   'x-image-meta-disk-format': 'ami',
                   'x-image-meta-container-format': 'ami',
                   'x-image-meta-property-Kernel_id': '%s' % self.glance['kernel_id'],
                   'x-image-meta-property-Ramdisk_id': '%s' % self.glance['ramdisk_id'],
                   'Content-Length': '%d' % os.path.getsize(image),
                   'Content-Type': 'application/octet-stream'}
        http = httplib2.Http()
        response, content = http.request(path, 'POST', headers=headers, body=upload_data)
        self.assertEqual(201, response.status)
        pprint(content)
        data = json.loads(content)
        self.glance['image_id'] = data['image']['id']
        self.assertEqual(data['image']['name'], "test-image")
        self.assertEqual(data['image']['checksum'], self._md5sum_file(image))
