from app.exceptions import MethodNotOverridden
from app.settings import TOPIC_MQTT_HA


class HomeAssistant:
    """
    Создаёт конфиги для устройств и отправляет на требуемый топик,
    что бы home assistant автоматически добавлял их.
    """

    def __init__(self, device):
        self.device = device
        self.config = self._get_config()

    def _get_config(self):
        raise MethodNotOverridden


class Sensor(HomeAssistant):
    """Клас для типов сущностей сенсоры"""
    
    type_entity = 'sensor'
    topic_start = f'{TOPIC_MQTT_HA}/{type_entity}'


class Temperature(Sensor):
    """
    Класс для создания конфига сенсоров температуры
    """

    class_entity = 'temperature'
    unit_of_measurement = '°C'
    topic_finish = f'{class_entity}/config'

    def _get_config(self) -> dict:
        """
        :return:
        {
            'homeassistant/sensor/123456_4103/temperature/config': {
                'device_class': 'temperature',
                'name': '1 этаж. подача',
                'state_topic': 'zont/123456/temp/4103/',
                'unit_of_measurement': '°C',
                'value_template': '{{ value_json.temp }}'
            },
            ....
        }
        """

        config = {}
        list_temp = self.device.get_state_topics(
            self.device.available_entities.temperature
        )
        for state_topic, param_temp, in list_temp.items():
            topic = (
                f'{self.topic_start}/'
                f'{str(self.device.device_id)}_{param_temp["id"]}/'
                f'{self.topic_finish}'
            )
            config[topic] = {
                'device_class': self.class_entity,
                'name': param_temp['name'],
                'state_topic': state_topic,
                'unit_of_measurement': self.unit_of_measurement,
                'value_template': '{{ value_json.temp }}'
            }

        return config
