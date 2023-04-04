import json

from app.exceptions import MethodNotOverridden
from app.models import Zont
from app.settings import TOPIC_MQTT_HA, TOPIC_MQTT_ZONT
from app.zont import get_list_state_for_mqtt, get_min_max_values_temp


class HomeAssistant:
    """
    Создаёт конфиги для устройств и отправляет на требуемый топик,
    что бы home assistant автоматически добавлял их.
    """

    def __init__(self, zont: Zont):
        self.zont = zont
        self.config: dict = self._get_config()

    def _get_config(self):
        raise MethodNotOverridden


class Sensor(HomeAssistant):
    """Клас для типов сущностей сенсоры"""

    type_entity = 'sensor'
    topic_start = f'{TOPIC_MQTT_HA}/{type_entity}'

    def _get_config(self) -> dict:
        """
        {
            'homeassistant/sensor/123456_4103/temperature/config': {
                'device_class': 'temperature',
                'name': '1 этаж. подача',
                'state_topic': 'zont/123456/temp/4103/',
                'unit_of_measurement': '°C',
                'value_template': '{{ value_json.temp }}',
                'json_attributes_topic': 'zont/123456/temp/4103/',
                'unique_id': '278936_4103_temperature_zont'
                'availability': [
                    {
                        'topic': 'zont/123456/online',
                        'payload_available': 'True',
                        'payload_not_available': 'False'
                    }
                ]
            ....
        }
        """

        config = {}
        list_state = get_list_state_for_mqtt(self.zont, ('sensors',))
        for state_topic, state in list_state:
            data: dict = json.loads(state)
            id_device = state_topic.split('/')[1]
            topic = (f'{self.topic_start}/'
                     f'{id_device}_{data["id"]}/'
                     f'{data["type"]}/config')
            config[topic] = {
                'device_class': data['type'],
                'name': data['name'],
                'state_topic': state_topic,
                'unit_of_measurement': data['unit'],
                'value_template': '{{ value_json.value }}',
                'json_attributes_topic': state_topic,
                'unique_id': (f'{id_device}_{data["id"]}_'
                              f'{data["type"]}_{TOPIC_MQTT_ZONT}'),
                'availability': [
                    {
                        'topic': (
                            f'{TOPIC_MQTT_ZONT}/{id_device}/sensors/'
                            f'{data["id"]}'
                        ),
                        'value_template': '{{ value_json.status }}',
                        'payload_available': 'ok',
                        'payload_not_available': 'failure'
                    }
                ]
            }

        return config


class Climate(HomeAssistant):
    """Класс для климата."""

    type_entity = 'climate'
    topic_start = f'{TOPIC_MQTT_HA}/{type_entity}'

    def _get_config(self) -> dict:
        """
        {
            'homeassistant/climate/123456_8550/climate/config': {
                'name': '1 этаж'
                'availability': [
                    {
                        'topic': 'zont/123456/heating_circuits/8550',
                        'value_template': '{{ value_json.status }}'
                        'payload_available': 'ok',
                        'payload_not_available': 'failure'
                    }
                ],
                'unique_id': '"123456_8550_climate_zont"'
                'mode_state_topic': 'zont/123456/heating_circuits/8550',
                'mode_state_template': (
                    '{% if value_json.is_off %} off '
                    '{% else %} heat {% endif %}'
                ),
                'mode': ['off', 'heat'],
                'preset_mode_command_topic': (
                    'zont/123456/heating_circuits/8550'
                    ),
                'preset_mode_command_topic': (
                    'zont/123456/heating_circuits/8550/mode/set'
                    ),
                'preset_modes': ['comfort', 'eco'],
                'action_topic': 'zont/123456/heating_circuits/8550',
                'action_template': (
                    '{% if value_json.active %} heating '
                    '{% else %} idle {% endif %}'
                ),
                'value_template': '{{ value_json.actual_temp }}'
                'temperature_state_topic': 'zont/123456/heating_circuits/8550',
                'temperature_state_template': '{{ value_json.target_temp }}',
                'current_temperature_topic': (
                    'zont/123456/heating_circuits/8550'
                ),
                'current_temperature_template': (
                    'zont/123456/heating_circuits/8550'
                ),
                'json_attributes_topic': 'zont/123456/heating_circuits/8550',
                'json_attributes_template': '{{ value_json }}',
                'temperature_command_topic': (
                    'zont/123456/heating_circuits/8550/set'
                ),
                'temp_step': 0.1,
                'min_temp': 10,
                'max_temp': 35
            }
            ....
        }
        """

        config = {}
        list_state = get_list_state_for_mqtt(self.zont, ('heating_circuits',))
        for state_topic, state in list_state:
            data: dict = json.loads(state)
            id_device = state_topic.split('/')[1]
            min_temp, max_temp = get_min_max_values_temp(data['name'])
            topic = (f'{self.topic_start}/'
                     f'{id_device}_{data["id"]}/'
                     f'{self.type_entity}/config')
            config[topic] = {
                'name': data['name'],
                'availability': [
                    {
                        'topic': (
                            f'{TOPIC_MQTT_ZONT}/{id_device}/heating_circuits/'
                            f'{data["id"]}'
                        ),
                        'value_template': '{{ value_json.status }}',
                        'payload_available': 'ok',
                        'payload_not_available': 'failure'
                    }
                ],
                'unique_id': (f'{id_device}_{data["id"]}_'
                              f'{self.type_entity}_{TOPIC_MQTT_ZONT}'),
                'mode_state_topic': state_topic,
                'mode_state_template': (
                    '{% if value_json.is_off %} off '
                    '{% else %} heat {% endif %}'
                ),
                'modes': ['off', 'heat'],
                'preset_mode_state_topic': state_topic,
                'preset_mode_command_topic': f'{state_topic}/mode/set',
                'preset_mode_value_template': (
                    '{{ value_json.current_mode_name }}'
                ),
                'preset_modes': ['comfort', 'eco'],
                'action_topic': state_topic,
                'action_template': (
                    '{% if value_json.active %} heating '
                    '{% else %} idle {% endif %}'
                ),
                'value_template': '{{ value_json.actual_temp }}',
                'temperature_state_topic': state_topic,
                'temperature_state_template': '{{ value_json.target_temp }}',
                'current_temperature_topic': state_topic,
                'current_temperature_template': '{{ value_json.actual_temp }}',
                'temperature_command_topic': f'{state_topic}/set',
                'temp_step': 0.1,
                'min_temp': min_temp,
                'max_temp': max_temp
            }
        return config
