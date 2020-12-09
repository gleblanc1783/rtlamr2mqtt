import os
import sys
import json

import paho.mqtt.client as mqtt

# Create MQTT Client
client = mqtt.Client("rtlamr2mqtt") # Default name, can easily be changed

if not os.environ.get("MQTT_HOST"):
    print ("[*] Error, please specify MQTT_HOST.")
    sys.exit(1)

if not os.environ.get("MQTT_TOPIC"):
    print ("[*] Error, please specify MQTT_TOPIC.")
    sys.exit(1)

client.connect(os.environ.get("MQTT_HOST"))
client.loop_start()

# Once you've determined your list of IDs you need to monitor, you can specify them here
IDS_TO_MONITOR = []

LAST = {}

if __name__ == "__main__":
    try:
        while True:
            for line in iter(sys.stdin.readline, ''):
                try:
                    resp = json.loads(line.rstrip())
                except Exception as e:
                    print ("[*] Error, invalid JSON from rtlasm, did you specify JSON output format?")
                id = resp.get("Message").get("EndpointID")
                if id in IDS_TO_MONITOR:
                    if id in LAST:
                        diff = resp.get("Message").get("Consumption") - LAST[id]
                        LAST[id] = resp.get("Message").get("Consumption")
                        print ("{0} used {1} dcW".format(id, diff))
                        diffo = { "diff": diff }
                        if diff != 0:
                            c = client.publish(os.environ.get("MQTT_TOPIC"), json.dumps(diffo))
                    else:
                        LAST[id] = resp.get("Message").get("Consumption")
                        print ("{0} began {1} dcW".format(id, resp.get("Message").get("Consumption")))
    except KeyboardInterrupt:
        print ("[*] Keyboard interrupt.")
        sys.exit(0)