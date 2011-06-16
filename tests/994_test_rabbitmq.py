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

"""Functional test case to check RabbitMQ """
import json
import os
import tempfile
import unittest
import httplib2
import urllib
import hashlib
import time
import pika

from pprint import pprint

import tests

RABBITMQ_HOST = "10.127.52.128"

class TestRabbitMQ(tests.FunctionalTest):
    def test_001_connect(self):
	creds = pika.credentials.PlainCredentials('guest', '')
	parameters = pika.ConnectionParameters(credentials=creds,
					       host=RABBITMQ_HOST,
					       virtual_host='/')
	
