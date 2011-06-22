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

"""
Functional test case to check the status of gepetto and
set information of hosts etc..
"""

import json
import os
import tempfile
import unittest
import httplib2
import urllib
import hashlib
import time
import dns
from xmlrpclib import Server
from pprint import pprint

import tests
from tests.config import get_config

# GEPPETTO_HOST = get_config("geppetto/host")
# GEPPETTO_PORT = get_config("geppetto/port")
# GEPPETTO_PATH = get_config("geppetto/path")


class TestGeppetto(tests.FunctionalTest):
    def test_001_get_nodes(self):
        server = Server("http://%s:%s%s" % (self.hosts['geppetto']['host'],
                        self.hosts['geppetto']['port'], self.hosts['geppetto']['path']))
        self.assertTrue(server.get_nodes())

    def test_002_get_nodes_in_role(self):
        server = Server("http://%s:%s%s" % (self.hosts['geppetto']['host'],
                        self.hosts['geppetto']['port'], self.hosts['geppetto']['path']))
        self.assertTrue(server.get_nodes_in_role('os-vpx-nova-manage'),
            'No vpxs defined with role: "%s"' % "os-vpx-nova-manage")

    def test_003_get_nodes_not_in_role(self):
        server = Server("http://%s:%s%s" % (self.hosts['geppetto']['host'],
                        self.hosts['geppetto']['port'], self.hosts['geppetto']['path']))
        # self.assertTrue(server.get_nodes_not_in_role('mysql'))
        node_list = server.get_nodes_not_in_role('os-vpx-nova-manage')
        self.assertFalse(node_list, 'Should not return any vpxs, '
            'currently returning: %s' % len(node_list))

    def test_004_role_has_node(self):
        server = Server("http://%s:%s%s" % (self.hosts['geppetto']['host'],
                        self.hosts['geppetto']['port'], self.hosts['geppetto']['path']))
        self.assertTrue(server.role_has_node('os-vpx-nova-manage'),
            'No vpxs defined with role: "%s"' % "os-vpx-nova-manage")

    def test_010_dns_resolution_is_working(self):
        server = Server("http://%s:%s%s" % (self.hosts['geppetto']['host'],
                        self.hosts['geppetto']['port'], self.hosts['geppetto']['path']))
        #for key, val in geppetto_srv.get_nodes():
        #    query = self.resolver.query(key, raise_on_no_answer=True)
        #    self.hosts[key] = query[0].address
        #print self.hosts

    def test_030_minimum_roles_for_deployment(self):
        server = Server("http://%s:%s%s" % (self.hosts['geppetto']['host'],
                        self.hosts['geppetto']['port'], self.hosts['geppetto']['path']))
