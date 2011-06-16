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
import pika
import tests

from tests.config import get_config
RABBITMQ_HOST = get_config("rabbitmq/host")


class TestRabbitMQ(tests.FunctionalTest):
    def test_001_connect(self):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue="compute",
                              durable=True,
                              exclusive=False,
                              auto_delete=False)
        messages = 0

        def _on_message(channel, method, header, body):
            global messages

            print "Message:"
            print "\t%r" % method
            print "\t%r" % header
            print "\t%r" % body
            channel.basic_ack(method.delivery_tag)

            messages += 1
            if messages > 10:
                channel.stop_consuming()
        channel.basic_consume(_on_message, queue="compute")
        channel.start_consuming()
