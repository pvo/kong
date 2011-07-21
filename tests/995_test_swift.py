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

"""Functional test case for OpenStack Swift """

import json
import os
import tempfile
import unittest
import httplib2
import urllib
import hashlib
import time
import os

from pprint import pprint

import tests

from tests.config import get_config

SMALL_OBJ="include/swift_objects/swift_small"
MED_OBJ="include/swift_objects/swift_medium"
LRG_OBJ="include/swift_objects/swift_large"

class TestSwift(tests.FunctionalTest):
    def build_md5sums(self,filename):
        infile = open(filename, 'rb')
        content = infile.read()
        infile.close()
        m = hashlib.md5()
        m.update(content)
        md5 = m.hexdigest()
        
    def test000_auth(self):
        if self.swift['auth_ssl'] == 'yes':
           prot = "https://"
        else:
           prot = "http://"

        path = "%s%s:%s%s%s" % (prot, self.swift['auth_host'],
                                      self.swift['auth_port'],
                                      self.swift['auth_prefix'],
                                      self.swift['ver'])

        http = httplib2.Http(disable_ssl_certificate_validation=True)
        self.swift['auth_user'] = '%s:%s' % (self.swift['account'], self.swift['username'])
        headers = {'X-Auth-User': '%s' % (self.swift['auth_user']),
                   'X-Auth-Key': '%s' % (self.swift['password'])}
        response, content = http.request(path, 'GET', headers=headers)
        self.assertEqual(200, response.status)
        self.assertIsNotNone(response['x-auth-token'])
        self.assertIsNotNone(response['x-storage-token'])
        self.assertIsNotNone(response['x-storage-url'])

        for k,v in response.items():
            if (k == 'x-auth-token'):
                self.swift['x-auth-token'] = v
            if (k == 'x-storage-token'):
                self.swift['x-storage-token'] = v

        # Since we don't have DNS this is a bit of a hack, but works
        url = response['x-storage-url'].split('/')
        self.swift['storage_url'] = "%s//%s/%s/%s" % (url[0], self.swift['auth_host'], url[3], url[4])

    def test001_create_container(self):
        path = "%s/%s" % (self.swift['storage_url'], "test_container")
        http = httplib2.Http(disable_ssl_certificate_validation=True)
        headers = {'X-Auth-User': '%s:%s' % (self.swift['account'], self.swift['username']),
                   'X-Storage-Token': '%s' % (self.swift['x-storage-token'])}
        response, content = http.request(path, 'PUT', headers=headers)
        self.assertEqual(201, response.status)

    def test002_list_containers(self):
        http = httplib2.Http(disable_ssl_certificate_validation=True)
        headers = {'X-Auth-Token': '%s' % (self.swift['x-auth-token'])}
        response, content = http.request(self.swift['storage_url'], 'GET', headers=headers)
        self.assertEqual(200, response.status)
        self.assertLessEqual('1', response['x-account-container-count'])

    def test010_create_single_object(self):
        md5 = self.build_md5sums(SMALL_OBJ)
        path = "%s/%s/%s" % (self.swift['storage_url'], "test_container", "swift_small")
        http = httplib2.Http(disable_ssl_certificate_validation=True)
        headers = {'X-Auth-User': '%s:%s' % (self.swift['account'], self.swift['username']),
                   'X-Storage-Token': '%s' % (self.swift['x-storage-token']),
                   #'ETag': '%s' % (md5),
                   'Content-Length': '%d' % os.path.getsize(SMALL_OBJ),
                   'Content-Type': 'application/octet-stream'}
        upload = open(SMALL_OBJ, "rb")
        response, content = http.request(path, 'PUT', headers=headers, body=upload)

    # def test019_delete_single_object(self):
        # path = "%s/%s/%s" % (self.swift['storage_url'], "test_container", "object1")
        # http = httplib2.Http(disable_ssl_certificate_validation=True)
        # headers = {'X-Auth-User': '%s:%s' % (self.swift['account'], self.swift['username']),
                   # 'X-Storage-Token': '%s' % (self.swift['x-storage-token'])}
        # response, content = http.request(path, 'DELETE', headers=headers)
        # pprint(response)
 
    def test030_check_container_metadata(self):
        path = "%s/%s" % (self.swift['storage_url'], "test_container")
        http = httplib2.Http(disable_ssl_certificate_validation=True)
        headers = {'X-Auth-User': '%s:%s' % (self.swift['account'], self.swift['username']),
                   'X-Storage-Token': '%s' % (self.swift['x-storage-token'])}
        response, content = http.request(path, 'HEAD', headers=headers)
        self.assertEqual(204, response.status)
        # pprint(response)
        
    def test050_delete_container(self):
        path = "%s/%s" % (self.swift['storage_url'], "test_container")
        http = httplib2.Http(disable_ssl_certificate_validation=True)
        headers = {'X-Auth-User': '%s:%s' % (self.swift['account'], self.swift['username']),
                   'X-Storage-Token': '%s' % (self.swift['x-storage-token'])}
        response, content = http.request(path, 'DELETE', headers=headers)
        self.assertEqual(204, response.status)
