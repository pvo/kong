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
from tests.config import get_config

# GLANCE API TESTS Variables
# TEST_HOST = get_config("glance/host")
# TEST_PORT = get_config("glance/port")


class TestCleanUp(tests.FunctionalTest):
    def test_000_ghetto_fixup_variables(self):
        """
        This sets the host and port self variables so they
        are accessible by all other methods
        """
        # self.glance['host'] = get_config("glance/host")
        # self.glance['port'] = get_config("glance/port")
        self.glance['host'] = self.hosts['openstack-glance-api']['host'][0]
        self.glance['port'] = self.hosts['openstack-glance-api']['port']
    test_000_ghetto_fixup_variables.tags = ['olympus', 'glance', 'nova']

    def test_995_delete_server(self):
        path = "http://%s:%s/%s/servers/%s" % (self.nova['host'],
                                               self.nova['port'],
                                               self.nova['ver'],
                                               self.nova['single_server_id'])
        http = httplib2.Http()
        headers = {'X-Auth-User': '%s' % (self.nova['user']),
                   'X-Auth-Token': '%s' % (self.nova['X-Auth-Token'])}
        response, content = http.request(path, 'DELETE', headers=headers)
        self.assertEqual(202, response.status)
    test_995_delete_server.tags = ['olympus', 'nova']

    def test_996_delete_multi_server(self):
        print len(self.multi_server)
        for k, v in self.multi_server.iteritems():
            path = "http://%s:%s/%s/servers/%s" % (self.nova['host'],
                                                   self.nova['port'],
                                                   self.nova['ver'],
                                                   v)
            http = httplib2.Http()
            headers = {'X-Auth-User': '%s' % (self.nova['user']),
                       'X-Auth-Token': '%s' % (self.nova['X-Auth-Token'])}
            response, content = http.request(path, 'DELETE', headers=headers)
            self.assertEqual(202, response.status)
    test_996_delete_multi_server.tags = ['olympus', 'nova']

    def test_997_delete_kernel_from_glance(self):
        path = "http://%s:%s/images/%s" % (self.glance['host'],
                                           self.glance['port'],
                                           self.glance['kernel_id'])
        http = httplib2.Http()
        response, content = http.request(path, 'DELETE')
        self.assertEqual(200, response.status)
    test_997_delete_kernel_from_glance.tags = ['olympus', 'glance', 'nova']

    def test_998_delete_initrd_from_glance(self):
        path = "http://%s:%s/images/%s" % (self.glance['host'],
                                           self.glance['port'],
                                           self.glance['ramdisk_id'])
        http = httplib2.Http()
        response, content = http.request(path, 'DELETE')
        self.assertEqual(200, response.status)
    test_998_delete_initrd_from_glance.tags = ['olympus', 'glance', 'nova']

    def test_999_delete_image_from_glance(self):
        path = "http://%s:%s/images/%s" % (self.glance['host'],
                                           self.glance['port'],
                                           self.glance['image_id'])
        http = httplib2.Http()
        response, content = http.request(path, 'DELETE')
        self.assertEqual(200, response.status)
    test_999_delete_image_from_glance.tags = ['olympus', 'glance', 'nova']
