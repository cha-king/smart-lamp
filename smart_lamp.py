from gpiozero import LED
import paho.mqtt.client as paho


DEFAULT_LAMP_PIN = 24
DEFAULT_BROKER_HOST = 'mqtt-broker.local'
DEFAULT_TOPIC_BASE = 'bedroom/lamp'


class SmartLamp:
    def __init__(self, lamp_pin, broker_host, topic_base):
        self.lamp_pin = lamp_pin
        self.broker_host = broker_host
        self.topic_base = topic_base

        self.lamp = LED(lamp_pin)
        self.lamp_state = 'off'

        self.topic_handlers = {
            self.topic_base + '/getState': self._get_state,
            self.topic_base + '/setState': self._set_state,
            self.topic_base + '/toggleState': self._toggle_state
        }

        self.mqtt_client = paho.Client()
        self.mqtt_client.on_connect = self._mqtt_on_connect
        self.mqtt_client.on_message = self._mqtt_on_message

    def _mqtt_on_connect(self, client, userdata, flags, rc):
        self.mqtt_client.subscribe(
            [(self.topic_base + '/getState', 0),
             (self.topic_base + '/setState', 0),
             (self.topic_base + '/toggleState', 0)]
        )

    def _mqtt_on_message(self, client, userdata, msg):
        handler = self.topic_handlers[msg.topic]
        handler(msg.payload.decode())

    def _get_state(self, payload):
        self._publish_state()

    def _set_state(self, payload):
        if payload == 'on':
            self.lamp.off()
            self.lamp_state = 'on'
        elif payload == 'off':
            self.lamp.on()
            self.lamp_state = 'off'

        self._publish_state()

    def _toggle_state(self, payload):
        self.lamp.toggle()
        if self.lamp_state == 'off':
            self.lamp_state = 'on'
        elif self.lamp_state == 'on':
            self.lamp_state = 'off'

        self._publish_state()

    def _publish_state(self):
        self.mqtt_client.publish(
            self.topic_base + '/state',
            payload=self.lamp_state
        )

    def start(self):
        self.mqtt_client.connect(self.broker_host)

    def loop_forever(self):
        self.mqtt_client.loop_forever()


if __name__ == '__main__':
    smart_lamp = SmartLamp(DEFAULT_LAMP_PIN, DEFAULT_BROKER_HOST,
                           DEFAULT_TOPIC_BASE)
    smart_lamp.start()
    smart_lamp.loop_forever()
