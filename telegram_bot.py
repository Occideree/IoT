import telebot
import paho.mqtt.client as mqtt

# Ваш токен бота
TELEGRAM_BOT_TOKEN = "7763370927:AAE0gEQlTzppvyjayLla-HH2gibSFiyP40w"

# Настройки MQTT
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_READ_TOPIC = "iot/sprinkler/sensors"
MQTT_POST_TOPIC = "iot/sprinkler/commands"
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Список пользователей, подписанных на уведомления
subscribed_users = set()

# Функция обработки команды /start
@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.chat.id
    if user_id not in subscribed_users:
        subscribed_users.add(user_id)
        bot.send_message(user_id, "Вы подписались на уведомления о новых сообщениях MQTT.")
    else:
        bot.send_message(user_id, "Вы уже подписаны на уведомления.")

@bot.message_handler(commands=['stop'])
def stop_handler(message):
    user_id = message.chat.id
    if user_id in subscribed_users:
        subscribed_users.remove(user_id)
        bot.send_message(user_id, "Вы отписались от уведомлений.")
    else:
        bot.send_message(user_id, "Вы не подписаны на уведомления.")

# Функция обработки команды /auto
@bot.message_handler(commands=['automatic'])
def auto_handler(message):
    global mqtt_client
    try:
        mqtt_client.publish("iot/sprinkler/commands", "\"Automatic\"")
        bot.send_message(message.chat.id, "Сообщение  отправлено на MQTT-сервер.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка отправки сообщения: {e}")

@bot.message_handler(commands=['startpump'])
def auto_handler(message):
    global mqtt_client
    try:
        mqtt_client.publish("iot/sprinkler/commands", "\"StartPump\"")
        bot.send_message(message.chat.id, "Сообщение  отправлено на MQTT-сервер.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка отправки сообщения: {e}")

@bot.message_handler(commands=['stoppump'])
def auto_handler(message):
    global mqtt_client
    try:
        mqtt_client.publish("iot/sprinkler/commands", "\"StopPump\"")
        bot.send_message(message.chat.id, "Сообщение  отправлено на MQTT-сервер.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка отправки сообщения: {e}")

@bot.message_handler(commands=['manual'])
def auto_handler(message):
    global mqtt_client
    try:
        mqtt_client.publish("iot/sprinkler/commands", "\"Manual\"")
        bot.send_message(message.chat.id, "Сообщение  отправлено на MQTT-сервер.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка отправки сообщения: {e}")

# Функция обработки входящих MQTT сообщений
def on_message(client, userdata, msg):
    message = f"Новое сообщение из MQTT: {msg.payload.decode('utf-8')}"
    for user_id in subscribed_users:
        try:
            bot.send_message(user_id, message)
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

# Настройка MQTT клиента
def setup_mqtt():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.subscribe(MQTT_READ_TOPIC)
    return client

# Основной цикл
if __name__ == "__main__":
    mqtt_client = setup_mqtt()

    mqtt_client.loop_start()
    print('Mqtt подключено')
    try:
        print('Идёт поллинг')
        bot.polling()
    except KeyboardInterrupt:
        print("Завершение работы.")
        mqtt_client.loop_stop()
