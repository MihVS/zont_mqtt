from settings import TOPIC_MQTT_HA


class HomeAssistant:
    """
    Создаёт конфиги для устройств и отправляет на требуемый топик,
    что бы home assistant автоматически добавлял их.
    """

    topic = TOPIC_MQTT_HA

    def __init__(self, name, state_topic):
        self.name = name
        self.state_topic = state_topic

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


class ConfTemperature(HomeAssistant):
    """

    """

    pass
