import requests
from http import HTTPStatus

from app.models import Zont, Device, HeatingMode, CustomControl, HeatingCircuit
from app.mqtt import client_mqtt
from app.settings import (
    LOGGER, URL_GET_DEVICES, BODY_GET_DEVICES, HEADERS, TOPIC_MQTT_ZONT,
    RETAIN_MQTT, URL_SET_GUARD, URL_SET_TARGET_TEMP, URL_ACTIVATE_HEATING_MODE,
    URL_TRIGGER_CUSTOM_BUTTON
)


def get_data_zont() -> str:
    """
    Делаем запрос к API ZONT https://lk.zont-online.ru/api
    :return:
    Возвращает строку ответа от API.
    """

    response = requests.post(
        url=URL_GET_DEVICES,
        json=BODY_GET_DEVICES,
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


def set_target_temp(
        device: Device, circuit: HeatingCircuit, target_temp: float
) -> None:
    """
    Отправка команды на прибор для установки явно заданной
    целевой температуры в одном из отопительных контуров.
    """

    response = requests.post(
        url=URL_SET_TARGET_TEMP,
        json={
            'device_id': device.id,
            'circuit_id': HeatingCircuit.id,
            'target_temp': target_temp
        },
        headers=HEADERS
    )
    status = response.status_code
    if status == HTTPStatus.OK:
        LOGGER.debug(f'Успешный запрос к API zont: {HTTPStatus.OK.name}')
        if response.json()['ok']:
            LOGGER.info(
                f'На устройстве {device.model}-{device.name} изменена '
                f'целевая температура контура {circuit.name} '
                f'на значение {target_temp}'
            )
        else:
            LOGGER.error(
                f'Ошибка контроллера {device.model}-{device.name}: '
                f'{response.json()["error_ui"]}'
            )
    else:
        LOGGER.error(f'Ошибка запроса к API zont: {status}')


def toggle_custom_button(
    device: Device, control: CustomControl, target_state: bool
) -> None:
    """Отправка на прибор команды нажатия пользовательской кнопки."""

    response = requests.post(
        url=URL_TRIGGER_CUSTOM_BUTTON,
        json={
            'device_id': device.id,
            'control_id': control.id,
            'target_state': target_state
        },
        headers=HEADERS
    )
    status = response.status_code
    if status == HTTPStatus.OK:
        LOGGER.debug(f'Успешный запрос к API zont: {HTTPStatus.OK.name}')
        if response.json()['ok']:
            LOGGER.info(
                f'На устройстве {device.model}-{device.name}. '
                f'Пользовательская кнопка {control.name} '
                f'переключена в значение {target_state}'
            )
        else:
            LOGGER.error(
                f'Ошибка контроллера {device.model}-{device.name}: '
                f'{response.json()["error_ui"]}'
            )
    else:
        LOGGER.error(f'Ошибка запроса к API zont: {status}')


def activate_heating_mode(device: Device, heating_mode: HeatingMode) -> None:
    """Отправка команды на прибор для активации одного из режимов отопления"""

    response = requests.post(
        url=URL_ACTIVATE_HEATING_MODE,
        json={
            'device_id': device.id,
            'mode_id': heating_mode.id,
        },
        headers=HEADERS
    )
    status = response.status_code
    if status == HTTPStatus.OK:
        LOGGER.debug(f'Успешный запрос к API zont: {HTTPStatus.OK.name}')
        if response.json()['ok']:
            LOGGER.info(
                f'На устройстве {device.model}-{device.name} активирован '
                f'режим отопления {heating_mode.name}'
            )
        else:
            LOGGER.error(
                f'Ошибка контроллера {device.model}-{device.name}: '
                f'{response.json()["error_ui"]}'
            )
    else:
        LOGGER.error(f'Ошибка запроса к API zont: {status}')
