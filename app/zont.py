import requests
from http import HTTPStatus

from requests import Response

from app.models import (
    Zont, Device, ControlEntityZONT, HeatingCircuit, CustomControl,
    HeatingMode, GuardZone
)
from app.settings import (
    LOGGER, URL_GET_DEVICES, BODY_GET_DEVICES, HEADERS, TOPIC_MQTT_ZONT,
    RETAIN_MQTT, URL_SET_GUARD, URL_SET_TARGET_TEMP, URL_ACTIVATE_HEATING_MODE,
    URL_TRIGGER_CUSTOM_BUTTON
)

# Кортеж названий полей устройства, которыми можно управлять
controls_name = (
    'heating_modes',
    'heating_circuits',
    'custom_controls',
    'guard_zones'
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


def get_list_state_for_mqtt(
        zont: Zont, fields_device: tuple[str, ...] = tuple()
) -> list[tuple, ...]:
    """
    Функция для подготовки данных для отправки состояний сенсоров в mqtt.
    Принимает объект класса Zont и кортеж полей класса Device
    которые нужно публиковать в mqtt.
    :return:
    [(topic, payload), ...]
    """

    list_states = []
    for device in zont.devices:
        if not fields_device:
            fields_device = tuple(device.__fields__.keys())
        topic_device = f'{TOPIC_MQTT_ZONT}/{device.id}'

        for field in fields_device:
            values = getattr(device, field)
            if type(values) is list:
                for value in values:
                    list_states.append(
                        (f'{topic_device}/{field}/{value.id}',
                         value.json(ensure_ascii=False))
                    )
            else:
                list_states.append(
                    (f'{topic_device}/{field}', values)
                )
    return list_states


def get_device_control_by_id(
        zont: Zont, device_id: int, control_id: int
) -> (tuple[Device, ControlEntityZONT] | None):
    """
    Функция для получения кортежа объектов устройства и объекта управления
    (отопительный контур, режим отопления, созданная кнопка, охранная зона)
    из переданных в неё id этих устройств.
    Если совпадения не найдено, то возвращает None.
    """

    device = get_device_by_id(zont, device_id)
    if device is None:
        return None
    for fild in controls_name:
        objs = getattr(device, fild)
        for obj in objs:
            if obj.id == control_id:
                return device, obj


def get_device_by_id(zont: Zont, device_id: int) -> Device | None:
    """
    Возвращает объект устройства по его id.
    Если устройства нет, то возвращает None.
    """

    return next(
        (device for device in zont.devices if device.id == device_id),
        None
    )


def add_log_send_command(func):
    """
    Декоратор для добавления логирования при отправке команды
    для управления контроллера.
    """
    def check_response(*args, **kwargs):
        length = len(args)
        if length == 3:
            device, control, target_state = args
        elif length == 2:
            device, control = args
        else:
            return func
        response = func(*args)
        _target_state = (
            lambda: str(target_state) if (length == 3) else 'toggle'
        )
        status = response.status_code
        if status == HTTPStatus.OK:
            LOGGER.debug(f'Успешный запрос к API zont: {status}')
            if response.json()['ok']:
                LOGGER.info(
                    f'На устройстве {device.model}-{device.name} '
                    f'Изменено состояние {control.name}: {_target_state()}'
                )
            else:
                LOGGER.error(
                    f'Ошибка контроллера {device.model}-{device.name}: '
                    f'{response.json()["error_ui"]}'
                )
        else:
            LOGGER.error(f'Ошибка запроса к API zont: {status}')

    return check_response


@add_log_send_command
def set_target_temp(
        device: Device, circuit: HeatingCircuit, target_temp: float
) -> Response:
    """
    Отправка команды на прибор для установки явно заданной
    целевой температуры в одном из отопительных контуров.
    """
    return requests.post(
        url=URL_SET_TARGET_TEMP,
        json={
            'device_id': device.id,
            'circuit_id': circuit.id,
            'target_temp': target_temp
        },
        headers=HEADERS
    )


@add_log_send_command
def toggle_custom_button(
        device: Device, control: CustomControl, target_state: bool
) -> Response:
    """Отправка на прибор команды нажатия пользовательской кнопки."""

    return requests.post(
        url=URL_TRIGGER_CUSTOM_BUTTON,
        json={
            'device_id': device.id,
            'control_id': control.id,
            'target_state': target_state
        },
        headers=HEADERS
    )


@add_log_send_command
def activate_heating_mode(
        device: Device, heating_mode: HeatingMode
) -> Response:
    """Отправка команды на прибор для активации одного из режимов отопления"""

    return requests.post(
        url=URL_ACTIVATE_HEATING_MODE,
        json={
            'device_id': device.id,
            'mode_id': heating_mode.id,
        },
        headers=HEADERS
    )


@add_log_send_command
def set_guard(device: Device, guard_zone: GuardZone, enable: bool) -> Response:
    """
    Отправка команды на прибор для постановки на охрану
    или снятие с охраны одной из зон.
    """

    return requests.post(
        url=URL_SET_GUARD,
        json={
            'device_id': device.id,
            'mode_id': guard_zone.id,
            'enable': enable
        },
        headers=HEADERS
    )
