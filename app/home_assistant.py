from settings import TOPIC_MQTT_HA


class HomeAssistant:
    """
    Создаёт конфиги для устройств и отправляет на требуемый топик,
    что бы home assistant автоматически добавлял их.
    """

    topic = TOPIC_MQTT_HA
    device_class = {
        'temp': 'temperature',
        'humi': 'humidity',
        'voltage': 'voltage'
    }

    def __init__(self, object_device):
        self.object_device = object_device

    def get_config(self):
        pass

    def get_topic_temp(self):
        """
        Получает и возвращает топик на который нужно отправить конфиг для НА
        """

        pass

    def get_body_conf(self):
        """
        Получает и возвращает тело конфига.

        :return:
        """

        pass


class Temperature(HomeAssistant):
    """
    Класс для создания конфига сенсоров температуры
    """

    def get_config(self) -> dict:
        """
        :return:
        {
            'homeassistant/sensor/123456_4103/temperature/config': {
                'device_class': 'temperature',
                'name': '1 этаж. подача',
                'state_topic': 'zont/123456/temp/4103/',
                'unit_of_measurement': '°C',
                'value_template': '{{ value_json.temp }}'
            }
        }
        """

        config = {}

        return config
