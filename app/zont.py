from http import HTTPStatus
from collections import namedtuple

import requests

from app.exceptions import (
    RequestAPIZONTError, ResponseAPIZONTError, TypeSensorError
)
from app.settings import (
    BODY_REQUEST_DEVICES, URL_REQUEST_DEVICES, HEADERS, TOPIC_MQTT_ZONT,
    _logger
)


Entity = namedtuple('Entity',
                    'status '
                    'temperature '
                    'humidity'
                    )


class Zont:
    """
    Класс для экземпляра контроллера ZONT.
    Для получения данных датчиков и управления устройствами.
    """

    param_devices = []

    available_entities = Entity(
        'status',
        'temp',
        'humi'
    )

    def __init__(self, name: str, device_id: int, model: str):
        self.name = name
        self.device_id = device_id
        self.model = model
        _logger.debug(f'Создан объект контроллера с id = {self.device_id}')

    def __str__(self):
        return f'{self.name} - {self.model} - {self.device_id}'

    def get_status_device(self) -> dict:
        """
        Получает все статусы и показания контроллера

        :return:
        {
            'id': 123456
            'online': True,
            'voltage': 12.2,
            'name': 'Вятка'
        }
        """

        status = {}
        param_device = self._get_param_devices()
        try:
            status['id'] = self.device_id
            status['online'] = param_device['online']
            status['voltage'] = param_device['io']['voltage']
            status['name'] = self.name
            _logger.debug(f'Статус контроллера(id={self.device_id}): {status}')
        except (KeyError, IndexError):
            raise ResponseAPIZONTError(
                'API zont-online не соответствует ожидаемому'
            )
        return status

    def get_state_topics(self, type_entity: str) -> dict:
        """
        Создаёт словарь где ключ топик, а значение параметры датчика.
        Принимает тип датчика в виде строки:
            датчик температуры: 'temp'
            датчик влажности: 'humi'
            релейный выход: 'switch'

        :return:
        {
            'zont/123456/temp/4103/': {
                'name': 'Гараж воздух',
                'type': 'digital',
                'id': 4103,
                'temp': 23.1,
                'sensor_ok': True
            },
            ...
        }
        """

        topics_and_states = {}
        topic = f'{TOPIC_MQTT_ZONT}/{self.device_id}/{type_entity}'
        match type_entity:
            case self.available_entities.temperature:
                get_params = self.get_temperature
            case self.available_entities.status:
                return {topic: self.get_status_device()}
            case self.available_entities.humidity:
                return {}
            case _:
                _logger.error(f'Неизвестный тип сенсора: {type_entity}')
                raise TypeSensorError('Такого типа сенсора не существует!')
        for value in get_params():
            topic_sens = f'{topic}/{str(value["id"])}'
            topics_and_states[topic_sens] = value
        _logger.debug(
            f'Топики и значения успешно сформированы для сенсоров'
            f' типа: {type_entity}'
        )
        return topics_and_states

    def get_temperature(self) -> list[dict]:
        """
        Получает показания всех подключенных датчиков температуры.

        :return:
        [
            {
                'name': 'Гараж воздух',
                'type': 'digital',
                'id': 4103,
                'temp': 23.1,
                'sensor_ok': True
            },
            {
                ...
            }
        ]
        """

        all_temp = []
        param_device = self._get_param_devices()
        sensors_temp = self._scan_sensor_temp(param_device)
        values_temp = {}

        for temp in sensors_temp:
            values_temp['temp'] = param_device[
                'io']['z3k-state'][str(temp['id'])]['curr_temp']
            values_temp['sensor_ok'] = param_device[
                'io']['z3k-state'][str(temp['id'])]['sensor_ok']
            all_temp.append(temp | values_temp)

        _logger.debug(
            f'Показания температуры считаны из списка всех датчиков устройства'
            f' id = {self.device_id}'
        )
        return all_temp

    def _scan_sensor_temp(self, param_device: dict) -> list[dict]:
        """
        Сканирует все подключенные датчики температуры к контроллеру.

        :return:
        [
            {'id': 4103, 'name': 'Гараж воздух', 'type': 'digital'},
            {...},
            ...
        ]
        """

        sensors_temp = []

        try:
            for sensor in param_device[
                'z3k_config'
            ][
                'wired_temperature_sensors'
            ]:
                sensors_temp.append(
                    {
                        'id': sensor['id'],
                        'name': sensor['name'],
                        'type': 'digital'
                    }
                )
        except KeyError:
            _logger.debug(
                f'Контроллер(id={self.device_id}) не поддерживает '
                f'цифровые датчики температуры'
            )

        try:
            for sensor in param_device[
                'z3k_config'
            ][
                'analog_temperature_sensors'
            ]:
                sensors_temp.append(
                    {
                        'id': sensor['id'],
                        'name': sensor['name'],
                        'type': 'analog'
                    }
                )
        except KeyError:
            _logger.debug(
                f'Контроллер(id={self.device_id}) не поддерживает '
                f'аналоговые датчики температуры'
            )

        return sensors_temp

    def _get_param_devices(self) -> dict:
        """
        Получает словарь параметров конкретного объекта.

        :return: Словарь со всеми параметрами и показаниями устройства.
        """

        for param_device in self.param_devices:
            if param_device['id'] == self.device_id:
                return param_device
        _logger.error(f'Устройства с id = {self.device_id} не существует')
        return {}

    @staticmethod
    def _check_response(response) -> None:
        """Проверяет ответ на ошибки записывает в лог и вызывает исключения"""
        status_code = response.status_code
        _logger.debug(f'Код запроса к API zont: {status_code}')

        if status_code != HTTPStatus.OK:
            error_from_json = response.json()['error_ui']
            _logger.error(f'API zont: {error_from_json}')
            raise RequestAPIZONTError(f'Код запроса {status_code}, '
                                      f'ошибка: {error_from_json}')

    @classmethod
    def update_data(cls) -> None:
        """Обновляем текущие данные контроллера."""

        response = requests.post(
            url=URL_REQUEST_DEVICES,
            json=BODY_REQUEST_DEVICES,
            headers=HEADERS
        )
        cls._check_response(response)
        try:
            cls.param_devices = response.json()['devices']
            _logger.debug('Состояние датчиков контроллеров обновлено')
        except (KeyError, IOError):
            raise ResponseAPIZONTError(
                'API zont-online не соответствует ожидаемому'
            )
