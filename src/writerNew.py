#!/usr/bin/env python3
import paho.mqtt.client as client
import paho.mqtt.publish as publish
import sys
import json
import os

if os.path.exists('writer.log'):
    os.remove('writer.log')

if os.path.exists('writer-err.log'):
    os.remove('writer-err.log')

log = open('writer.log', 'a+')
log_err = open('writer-err.log', 'a+')

sys.stdout = log
sys.stderr = log_err

params = []

# initialize parameters

# aliveTopic
# topicToSubscribe
# topicToPublish
# vezerles
# sensorhub
for i in range(1, 6):
    params.append(sys.argv[i])

paramDict = {}
myclient = client.Client(client_id="ricsi_yolo", clean_session=True, userdata=None, transport="tcp")

for i in range(len(params)):
        content_of_element = json.loads(params[i])
        paramDict.update(content_of_element)

class WriterNew:

    def on_connect(self, client, userdata, flags, rc):
        print("CONNACK received with code ", rc)

        if rc == 0:
            print("Connected OK ", rc)

            publish.single(str(paramDict['topicAlive']), payload='{"module":"writer"}', qos=2, hostname=paramDict['vezerles']['ip'])
           # print("alive sent...")

        else:
            print("Connection failed, Returned code: ", rc)

        return rc

    def on_message(self, client, userdata, msg):
        # format of incoming message: {"id":42342,"data":[24,32,53....]}
        incomingJson = str(msg.payload.decode("utf-8"))
        print("i got a message!")
        print(msg.topic + " ----- " + incomingJson)

        # parsing json - for now, I "send" this to SensorHUB
        parsed = self.parse_message(incomingJson)
        payload = parsed['data']

        # send to shub
        publish.single(paramDict['sensorhub']['topic_to_send'],
                       payload=payload, qos=2, hostname=paramDict['sensorhub']['ip'])

        # send ack to vezerles
        id = parsed['id']
        msg_ack = '{"id":' + '"' + str(id) + '"}'

        result = myclient.publish(
            paramDict['topicToPublish'], payload=msg_ack, qos=2)
        print("result of sending: " + result)

    def parse_message(self, incomingJson):
        parsed = {}
        content_of_element = json.loads(incomingJson)

        # parsed = json.loads(incomingJson)
        parsed.update(content_of_element)

        # print parsed
        print(parsed)

        return parsed


w = WriterNew()

myclient.on_connect = w.on_connect
myclient.on_message = w.on_message

myclient.connect(paramDict['vezerles']['ip'], int(paramDict['vezerles']['port']))
print('alive sent...')

topic_to_subscribe = str(paramDict['topicToSubscribe'])
print("topic_to_subscribe:", topic_to_subscribe)

myclient.subscribe(topic_to_subscribe, qos=2)

myclient.loop_forever()
