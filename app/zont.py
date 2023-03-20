import requests
from http import HTTPStatus

from app.models import Zont
from app.mqtt import client_mqtt
from app.settings import (
    LOGGER, URL_REQUEST_DEVICES, BODY_REQUEST_DEVICES, HEADERS,
    TOPIC_MQTT_ZONT, RETAIN_MQTT
)


def get_data_zont() -> str:
    """
    Делаем запрос к API ZONT https://lk.zont-online.ru/api
    :return:
    Возвращает строку ответа от API.
    """

    response = requests.post(
        url=URL_REQUEST_DEVICES,
        json=BODY_REQUEST_DEVICES,
        headers=HEADERS
    )
    status = response.status_code
    if status == HTTPStatus.OK:
        LOGGER.debug(f'Успешный запрос к API zont: {HTTPStatus.OK.name}')
    else:
        LOGGER.error(f'Ошибка запроса к API zont: {status}')

    return response.text


def send_state_to_mqtt(
        zont: Zont, fields_device: tuple[str, ...] = tuple()
) -> None:
    """
    Функция для отправки состояний сенсоров в mqtt.
    Принимает объект класса Zont и кортеж полей класса Device
    которые нужно публиковать в mqtt.
    """

    for device in zont.devices:
        if not fields_device:
            fields_device = tuple(device.__fields__.keys())
        topic_device = f'{TOPIC_MQTT_ZONT}/{device.id}'

        for field in fields_device:
            values = getattr(device, field)
            if type(values) is list:
                for value in values:
                    payload = value.json()
                    client_mqtt.publish(
                        topic=f'{topic_device}/{field}/{value.id}',
                        payload=payload,
                        retain=RETAIN_MQTT
                    )
            else:
                client_mqtt.publish(
                    topic=f'{topic_device}/{field}',
                    payload=values,
                    retain=RETAIN_MQTT
                )


