#!/usr/bin/env python3
import paho.mqtt.client as client
import paho.mqtt.publish as publish
import sys
import json

params = []

# initialize parameters
for i in range(1, 4):
    params.append(sys.argv[i])

paramDict = {}
myclient = client.Client(client_id="ricsi_yolo", clean_session=True, userdata=None, transport="tcp")

class WriterNew:

    for i in range(len(params)):
        content_of_element = json.loads(params[i])
        paramDict.update(content_of_element)

    def on_connect(self, client, userdata, flags, rc):
        print("CONNACK received with code ", rc)

        if rc == 0:
            print("Connected OK ", rc)

            publish.single("controller/running", payload='{"alive":"yes"}', qos=2, hostname=paramDict['vezerles']['ip'])
            print("alive sent...")

        else:
            print("Connection failed, Returned code: ", rc)

        return rc

    def on_message(self, client, userdata, msg):
        incomingJson = str(msg.payload.decode("utf-8"))
        print("i got a message!")
        print(msg.topic + " ----- " + incomingJson)

        file_path = self.get_file_path(incomingJson)
        print("filePath:", file_path)
        record = self.get_record(file_path)
        print("record:", record)

        # send to shub
        publish.single(paramDict['sensorhub']['topic_to_send'], payload=record, qos=2, hostname=paramDict['sensorhub']['ip'])

        # send ack to vezerles
        msg_ack = ('{"path":"' + file_path + '","content":"ACK"}')

        topic_to_publish = str(paramDict['baseTopic']) + "out"
        print("topic_to_publish:", topic_to_publish)

        result = myclient.publish(topic_to_publish, payload=msg_ack, qos=1)
        print("result of ack: " + result)

    def get_file_path(self, incomingJson):
        parsed = json.loads(incomingJson)
        file_path = parsed['filePath']

        return file_path

    def get_record(self, file_path):
        try:

            with open(file_path, 'r') as file:
                record = file.read()
                file.close()
        except FileNotFoundError:
            print("File not found!")

        return record

w = WriterNew()

myclient.on_connect = w.on_connect
myclient.on_message = w.on_message

myclient.connect(paramDict['vezerles']['ip'], int(paramDict['vezerles']['port']))

topic_to_subscribe = str(paramDict['baseTopic']) + "in"
print("topic_to_subscribe:", topic_to_subscribe)

myclient.subscribe(topic_to_subscribe, qos=2)

# w.heartbeat()
myclient.loop_forever()
