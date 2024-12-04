import json
import paho.mqtt.client as mqtt

class MQTTClient:
    def __init__(self, server, port, topic_sensors, topic_commands, message_handler):
        self.server = server
        self.port = port
        self.topic_sensors = topic_sensors
        self.topic_commands = topic_commands
        self.message_handler = message_handler

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def connect(self):
        """Подключается к MQTT-брокеру."""
        self.client.connect(self.server, self.port, keepalive=60)
        self.client.loop_start()

    def disconnect(self):
        self.client.disconnect()
    def on_connect(self, client, userdata, flags, rc):
        """Обработчик события подключения."""
        if rc == 0:
            print("Connected to MQTT broker!")
            # Подписка на командный топик
            self.client.subscribe(self.topic_commands)
        else:
            print(f"Failed to connect, return code {rc}")

    def on_message(self, client, userdata, message):
        """Обрабатывает полученные сообщения."""
        payload = message.payload.decode()
        print(f"Message received on {message.topic}: {payload}")
        # Вызов обработчика для обработки команд
        self.message_handler(payload)

    def publish(self, topic, data):
        """Отправляет данные на указанный топик."""
        payload = json.dumps(data)
        self.client.publish(topic, payload)
        print(f"Message sent to {topic}: {payload}")

    def subscribe(self, topic):
        """Подписывается на указанный топик."""
        self.client.subscribe(topic)

    def unsubscribe(self, topic):
        """Отписывается от указанного топика."""
        self.client.unsubscribe(topic)