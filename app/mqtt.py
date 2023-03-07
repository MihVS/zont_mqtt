import sys

import paho.mqtt.client as mqtt
import time

from app.settings import (
    _logger, HOST_MQTT, PORT_MQTT, USER_NAME_MQTT, PSWD_MQTT
)


mqtt.Client.connected_flag = False

return_codes = {
    0: 'Соединение успешно',
    1: 'В соединении отказано - неверная версия протокола',
    2: 'В соединении отказано - неверный идентификатор клиента',
    3: 'В соединении отказано - сервер недоступен',
    4: 'В соединении отказано - неверное имя пользователя или пароль',
    5: 'В соединении отказано - не авторизовано'
}


def wait_connect():
    """Функция для ожидания соединения с брокером"""

    count = 0
    while not mqtt.Client.connected_flag and count < 30:
        _logger.info(f'Соединяюсь с mqtt брокером {HOST_MQTT}')
        time.sleep(1)
        count += 1


def on_log(client, userdata, level, buf):
    """Обратный вызов ведения журнала логов для mqtt"""

    _logger.debug(buf)


def on_connect(client, userdata, flags, rc):
    """Функция обратного вызова при соединении с брокером mqtt."""

    if rc == 0:
        client.connected_flag = True
        _logger.debug(f'Статус connected_flag: {client.connected_flag}')
        _logger.info(f'Успешное соединение с mqtt брокером {HOST_MQTT}')
    else:
        _logger.info(
            f'Ошибка соединения с mqtt брокером {HOST_MQTT}. '
            f'{return_codes[rc]}'
        )


def on_disconnect(client, userdata, flags, rc):
    """Функция обратного вызова при разрыве соединения с брокером mqtt."""

    _logger.info(f'Соединение с broker MQTT потеряно, статус: {rc}')
    if rc == 0:
        client.connected_flag = False
        _logger.debug(f'Статус connected_flag: {client.connected_flag}')


client_mqtt = mqtt.Client('zont')

client_mqtt.on_log = on_log
client_mqtt.on_connect = on_connect
client_mqtt.on_disconnect = on_disconnect


try:
    client_mqtt.username_pw_set(username=USER_NAME_MQTT, password=PSWD_MQTT)
    client_mqtt.connect(host=HOST_MQTT, port=PORT_MQTT)
except Exception as e:
    _logger.error(f'Не удалось подключится к mqtt брокеру: {e}')
    # sys.exit(1)

client_mqtt.loop_start()

# wait_connect()
