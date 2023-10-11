import paho.mqtt.client as mqtt
import base64
MQTT_HOST = "localhost"
MQTT_PORT = 1883

# To be implemented depending on the type of connection used
class Connection:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.connect(MQTT_HOST, MQTT_PORT, 60)

    def write(self, data):
        print(f"Writing data: {data}")

        self.client.publish("sender/packet", base64.b64encode(data))
