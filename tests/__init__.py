# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010-2011 OpenStack LLC.
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

import unittest
import os
import ConfigParser
import nose.plugins.skip
from hashlib import md5
from dns import resolver
from xmlrpclib import Server
from pprint import pprint

TEST_DATA = {}
TEST_NOVA = {}
SWIFT_CONF = {}
OLYMPUS_HOSTS = {}
MULTI_SERVER = {}
CONFIG_FILE = "/etc/olympus-validation/defaults.ini"

class skip_test(object):
    """Decorator that skips a test."""
    def __init__(self, msg):
        self.message = msg

    def __call__(self, func):
        def _skipper(*args, **kw):
            """Wrapped skipper function."""
            raise nose.SkipTest(self.message)
        _skipper.__name__ = func.__name__
        _skipper.__doc__ = func.__doc__
        return _skipper


class skip_if(object):
    """Decorator that skips a test."""
    def __init__(self, condition, msg):
        self.condition = condition
        self.message = msg

    def __call__(self, func):
        def _skipper(*args, **kw):
            """Wrapped skipper function."""
            if self.condition:
                raise nose.SkipTest(self.message)
        _skipper.__name__ = func.__name__
        _skipper.__doc__ = func.__doc__
        return _skipper


class skip_unless(object):
    """Decorator that skips a test."""
    def __init__(self, condition, msg):
        self.condition = condition
        self.message = msg

    def __call__(self, func):
        def _skipper(*args, **kw):
            """Wrapped skipper function."""
            if not self.condition:
                raise nose.SkipTest(self.message)
        _skipper.__name__ = func.__name__
        _skipper.__doc__ = func.__doc__
        return _skipper

class FunctionalTest(unittest.TestCase):
    def setUp(self):
        global TEST_DATA, TEST_NOVA, OLYMPUS_HOSTS, MULTI_SERVER, SWIFT_CONF
        self.glance = TEST_DATA
        self.nova = TEST_NOVA
        self.resolver = resolver.Resolver(filename='etc/resolv.conf',
                                          configure=True)
        self.hosts = OLYMPUS_HOSTS
        self.swift = SWIFT_CONF
        self.multi_server = MULTI_SERVER

        self.geppetto_host = os.getenv('GEPPETTO_HOST')
        self.hosts['geppetto'] = {}
        self.hosts['geppetto']['host'] = os.getenv('GEPPETTO_HOST')
        self.hosts['geppetto']['port'] = os.getenv('GEPPETTO_PORT')
        self.hosts['geppetto']['path'] = os.getenv('GEPPETTO_PATH')

        if os.getenv('OFFLINE_MODE'):
            self._fake_geppetto()
        else:
            self._find_geppetto_api_endpoints()
            self._parse_defaults_file()
        # pprint(self.hosts)
    
        self.swift = {
            'auth_host': self.hosts['openstack-swift-proxy']['host'][0],
            'auth_port': self.hosts['openstack-swift-proxy']['auth_port'],
            'auth_prefix': self.hosts['openstack-swift-proxy']['auth_prefix'],
            'auth_ssl': self.hosts['openstack-swift-proxy']['auth_ssl'],
            'account': self.hosts['openstack-swift-proxy']['account'],
            'username': self.hosts['openstack-swift-proxy']['username'],
            'password': self.hosts['openstack-swift-proxy']['password'],
        }

    def _find_geppetto_api_endpoints(self):
        self.roles = ['openstack-glance-api', 'openstack-nova-api',
                      'openstack-swift-proxy', 'rabbitmq-server']
        self.hosts['roles'] = self.roles
        server = Server("http://%s:%s%s" % (self.hosts['geppetto']['host'],
                        self.hosts['geppetto']['port'],
                        self.hosts['geppetto']['path']))
        for role in self.roles:
            self.hosts[role] = {}
            if server.role_has_node(role):
                self.hosts[role]['host'] = []
                for entry in server.get_nodes_in_role(role):
                    query = self.resolver.query(entry[0],
                                 raise_on_no_answer=True)
                    self.hosts[role]['host'].append(query[0].address)
            else:
                print 'Role [%s] has no member nodes' % role

    def _fake_geppetto(self):
        self.roles = ['openstack-glance-api', 'openstack-nova-api',
                      'openstack-swift-proxy', 'rabbitmq-server']
        self.hosts['roles'] = self.roles
        for role in self.roles:
            self.hosts[role] = {}
            self.hosts[role]['host'] = ['127.0.0.1']

    def _md5sum_file(self, path):
        md5sum = md5()
        with open(path, 'rb') as file:
            for chunk in iter(lambda: file.read(8192), ''):
                md5sum.update(chunk)
        return md5sum.hexdigest()

    def _read_in_chunks(self, infile, chunk_size=1024 * 64):
        file_data = open(infile, "rb")
        while True:
            # chunk = file_data.read(chunk_size).encode('base64')
            chunk = file_data.read(chunk_size)
            if chunk:
                yield chunk
            else:
                return
        file_data.close()

    def _parse_defaults_file(self):
        cfg = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   "..", "etc", "defaults.ini"))
        if os.path.exists(CONFIG_FILE):
            self._build_config(CONFIG_FILE)
        elif os.path.exists(cfg):
            self._build_config(cfg)

        # if not CONFIG:
        #    raise Exception("Cannot read config")

    def _build_config(self, config_file):
        if not os.path.exists(config_file):
            raise Exception("%s does not exists" % (config_file))

        parser = ConfigParser.ConfigParser()
        parser.read(config_file)

        for section in parser.sections():
            if section in self.hosts:
                # pprint(section)
                for value in parser.options(section):
                    self.hosts[section][value] = parser.get(section, value)
                    # print "%s = %s" % (value, parser.get(section, value))
