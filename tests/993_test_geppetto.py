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

# import httplib2
from xmlrpclib import Server
from pprint import pprint

import tests
# from tests.config import get_config

# GEPPETTO_HOST = get_config("geppetto/host")
# GEPPETTO_PORT = get_config("geppetto/port")
# GEPPETTO_PATH = get_config("geppetto/path")


class TestGeppetto(tests.FunctionalTest):
    def test_001_get_nodes(self):
        server = Server("http://%s:%s%s" % (self.hosts['geppetto']['host'],
                        self.hosts['geppetto']['port'],
                        self.hosts['geppetto']['path']))
        self.assertTrue(server.get_nodes())

    def test_002_get_nodes_in_role(self):
        server = Server("http://%s:%s%s" % (self.hosts['geppetto']['host'],
                        self.hosts['geppetto']['port'],
                        self.hosts['geppetto']['path']))
        self.assertTrue(server.get_nodes_in_role('os-vpx-nova-manage'),
            'No vpxs defined with role: "%s"' % "os-vpx-nova-manage")

    def test_003_get_nodes_not_in_role(self):
        server = Server("http://%s:%s%s" % (self.hosts['geppetto']['host'],
                        self.hosts['geppetto']['port'],
                        self.hosts['geppetto']['path']))
        # self.assertTrue(server.get_nodes_not_in_role('mysql'))
        node_list = server.get_nodes_not_in_role('os-vpx-nova-manage')
        self.assertFalse(node_list, 'Should not return any vpxs, '
            'currently returning: %s' % len(node_list))

    def test_004_role_has_node(self):
        server = Server("http://%s:%s%s" % (self.hosts['geppetto']['host'],
                        self.hosts['geppetto']['port'],
                        self.hosts['geppetto']['path']))
        self.assertTrue(server.role_has_node('os-vpx-nova-manage'),
            'No vpxs defined with role: "%s"' % "os-vpx-nova-manage")

    def test_005_get_config_default_xapi_pass(self):
        server = Server("http://%s:%s%s" % (self.hosts['geppetto']['host'],
                        self.hosts['geppetto']['port'],
                        self.hosts['geppetto']['path']))
        hv_passwd = server.get_config_parameter_default('XAPI_PASS')
        self.assertEqual(hv_passwd, "Hybr1d98")
#        self.assertTrue(server.get_config_parameter_default('XAPI_PASS'))

    def test_006_get_config_default_guest_network_bridge(self):
        server = Server("http://%s:%s%s" % (self.hosts['geppetto']['host'],
                        self.hosts['geppetto']['port'],
                        self.hosts['geppetto']['path']))
        bridge_dev = server.get_config_parameter_default(
                     'GUEST_NETWORK_BRIDGE')
        self.assertEqual(bridge_dev, "xenbr0")
#        self.assertTrue(server.get_config_parameter_default(
#                        'GUEST_NETWORK_BRIDGE'))

    def test_007_get_config_default_network_manager(self):
        server = Server("http://%s:%s%s" % (self.hosts['geppetto']['host'],
                        self.hosts['geppetto']['port'],
                        self.hosts['geppetto']['path']))
        net_manager = server.get_config_parameter_default(
                      'NETWORK_MANAGER')
        self.assertEqual(net_manager, "nova.network.manager.FlatManager")
#        self.assertTrue(server.get_config_parameter_default(
#                        'NETWORK_MANAGER'))

    def test_008_get_config_default_glance_store(self):
        server = Server("http://%s:%s%s" % (self.hosts['geppetto']['host'],
                        self.hosts['geppetto']['port'],
                        self.hosts['geppetto']['path']))
        store = server.get_config_parameter_default(
                     'GLANCE_STORE')
        self.assertEqual(store, "swift")
#        self.assertTrue(server.get_config_parameter_default(
#                        'GLANCE_STORE'))

    def test_009_get_config_default_swift_disk_size_gb(self):
        server = Server("http://%s:%s%s" % (self.hosts['geppetto']['host'],
                        self.hosts['geppetto']['port'],
                        self.hosts['geppetto']['path']))
        swift_disk = server.get_config_parameter_default(
                     'SWIFT_DISK_SIZE_GB')
        self.assertTrue(swift_disk > 20)
#        self.assertTrue(server.get_config_parameter_default(
#                        'SWIFT_DISK_SIZE_GB'))

    def test_030_minimum_swift_deployment(self):
        server = Server("http://%s:%s%s" % (self.hosts['geppetto']['host'],
                        self.hosts['geppetto']['port'],
                        self.hosts['geppetto']['path']))
        min_swift_roles = {
            'openstack-swift-account': 3,
            'openstack-swift-container': 3,
            'openstack-swift-object': 3,
            'openstack-swift-rsync': 3,
            'openstack-swift-proxy': 1,
            'memcached': 1}
        for role, min_count in min_swift_roles.items():
            nodes = server.get_nodes_in_role(role)
            self.assertTrue(len(nodes) >= min_count,
                "Expected %s nodes: %s, Geppetto shows: %s" %
                (role, min_count, len(nodes)))

    def test_031_minimum_nova_deployment(self):
        server = Server("http://%s:%s%s" % (self.hosts['geppetto']['host'],
                        self.hosts['geppetto']['port'],
                        self.hosts['geppetto']['path']))
        min_nova_roles = {
            'openstack-nova-api': 1,
            'openstack-nova-compute': 1,
            'openstack-nova-network': 1,
            'openstack-nova-scheduler': 1}
        for role, min_count in min_nova_roles.items():
            nodes = server.get_nodes_in_role(role)
            self.assertTrue(len(nodes) >= min_count,
                "Expected %s nodes: %s, Geppetto shows: %s" %
                (role, min_count, len(nodes)))

    def test_032_minimum_glance_deployment(self):
        server = Server("http://%s:%s%s" % (self.hosts['geppetto']['host'],
                        self.hosts['geppetto']['port'],
                        self.hosts['geppetto']['path']))
        min_glance_roles = {
            'openstack-glance-api': 1,
            'openstack-glance-registry': 1}
        for role, min_count in min_glance_roles.items():
            nodes = server.get_nodes_in_role(role)
            self.assertTrue(len(nodes) >= min_count,
                "Expected %s nodes: %s, Geppetto shows: %s" %
                (role, min_count, len(nodes)))

    def test_033_minimum_misc_deployment(self):
        server = Server("http://%s:%s%s" % (self.hosts['geppetto']['host'],
                        self.hosts['geppetto']['port'],
                        self.hosts['geppetto']['path']))
        min_misc_roles = {
            'openstack-dashboard': 1,
            'mysqld': 1,
            'rabbitmq-server': 1}
        for role, min_count in min_misc_roles.items():
            nodes = server.get_nodes_in_role(role)
            self.assertTrue(len(nodes) >= min_count,
                "Expected %s nodes: %s, Geppetto shows: %s" %
                (role, min_count, len(nodes)))

    def test_034_verify_roles_not_defined(self):
        server = Server("http://%s:%s%s" % (self.hosts['geppetto']['host'],
                        self.hosts['geppetto']['port'],
                        self.hosts['geppetto']['path']))
        not_defined_roles = [
            'openstack-nova-objectstore',
            'openstack-nova-volume']
        for role in not_defined_roles:
            nodes = server.get_nodes_in_role(role)
            self.assertEquals(len(nodes), 0,
                "%s should not be deployed, Geppetto shows: %s" %
                (role, len(nodes)))

    def test_050_dns_resolve_all_nodes(self):
        server = Server("http://%s:%s%s" % (self.hosts['geppetto']['host'],
                        self.hosts['geppetto']['port'],
                        self.hosts['geppetto']['path']))
        nodes = server.get_nodes()
        for node in nodes:
            try:
                self.assertTrue(self.resolver.query(node[0],
                                raise_on_no_answer=True))
            except:
                self.assertFalse(True, "DNS is unable to resolve host: %s"
                                       % node[0])
