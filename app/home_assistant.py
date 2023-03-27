import json

from app.exceptions import MethodNotOverridden
from app.settings import TOPIC_MQTT_HA, TOPIC_MQTT_ZONT
from app.models import Zont
from app.zont import get_list_state_for_mqtt


class HomeAssistant:
    """
    Создаёт конфиги для устройств и отправляет на требуемый топик,
    что бы home assistant автоматически добавлял их.
    """

    def __init__(self, zont: Zont):
        self.zont = zont
        self.config = self._get_config()

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
                # 'enabled_by_default': True,
                'json_attributes_topic': state_topic,
                'unique_id': (f'{id_device}_{data["id"]}_'
                              f'{data["type"]}_{TOPIC_MQTT_ZONT}'),
                'availability': [
                    {
                        'topic': f'{TOPIC_MQTT_ZONT}/{id_device}/online',
                        'payload_available': 'True',
                        'payload_not_available': 'False'
                    }
                ]
            }

        return config
