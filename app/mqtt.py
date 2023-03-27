import sys
import time

import paho.mqtt.client as mqtt

from app.settings import (
    LOGGER, HOST_MQTT, PORT_MQTT, USER_NAME_MQTT, PSWD_MQTT, TOPIC_MQTT_ZONT
)
from app.zont import get_data_zont
from app.models import Zont

mqtt.Client.zont = Zont.parse_raw(get_data_zont())
mqtt.Client.connected_flag = False
client_mqtt = mqtt.Client('zont')

return_codes = {
    0: 'Соединение успешно',
    1: 'В соединении отказано - неверная версия протокола',
    2: 'В соединении отказано - неверный идентификатор клиента',
    3: 'В соединении отказано - сервер недоступен',
    4: 'В соединении отказано - неверное имя пользователя или пароль',
    5: 'В соединении отказано - не авторизовано'
}


def wait_connect(client):
    """Функция для ожидания соединения с брокером"""

    count = 0
    while not client.connected_flag and count < 7:
        LOGGER.info(f'Соединяюсь с mqtt брокером {HOST_MQTT}')
        time.sleep(5)
        count += 1


def on_log(client, userdata, level, buf):
    """Обратный вызов ведения журнала логов для mqtt"""

    LOGGER.debug(buf)


def on_connect(client, userdata, flags, rc):
    """Функция обратного вызова при соединении с брокером mqtt."""

    if rc == 0:
        client.connected_flag = True
        LOGGER.debug(f'Статус connected_flag: {client.connected_flag}')
        LOGGER.info(f'Успешное соединение с mqtt брокером {HOST_MQTT}')
        client.subscribe(f'{TOPIC_MQTT_ZONT}/+/+/+/set/#')
    else:
        LOGGER.info(
            f'Ошибка соединения с mqtt брокером {HOST_MQTT}. '
            f'{return_codes[rc]}'
        )


def on_disconnect(client, userdata, flags, rc=0):
    """Функция обратного вызова при разрыве соединения с брокером mqtt."""

    LOGGER.info(f'Соединение с broker MQTT потеряно, статус: {rc}')
    if rc == 0:
        client.connected_flag = False
        LOGGER.debug(f'Статус connected_flag: {client.connected_flag}')


# def on_publish(client, userdata, mid):
#     """Функция обратного вызова при публикации сообщения"""
#
#     _logger.debug(f'Публикация сообщения. mid={mid}')


def on_message(client, userdata, msg):
    """
    Функция обратного вызова сообщений у подписанных топиков.

    msg.topic топик на который пришло сообщение.
    msg.payload тело сообщения.
    """

    LOGGER.debug(
        f'С топика {msg.topic} '
        f'принято сообщение: {msg.payload.decode("utf-8")}'
    )



def main():
    client_mqtt.on_log = on_log
    client_mqtt.on_connect = on_connect
    client_mqtt.on_disconnect = on_disconnect
    # client_mqtt.on_publish = on_publish
    client_mqtt.on_message = on_message

    client_mqtt.loop_start()

    try:
        client_mqtt.username_pw_set(
            username=USER_NAME_MQTT,
            password=PSWD_MQTT
        )
        client_mqtt.connect(host=HOST_MQTT, port=PORT_MQTT)
        wait_connect(client_mqtt)
    except Exception as e:
        LOGGER.error(f'MQTT брокер не доступен. {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
