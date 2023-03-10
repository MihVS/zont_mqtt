import json
import time

from app.mqtt import client_mqtt
from app.mqtt import main as main_mqtt
from app.settings import RETRY_TIME, TOPIC_MQTT_ZONT, RETAIN_MQTT
from app.zont import Zont
from configs.config_zont import DEVICES_PARAM


def create_device(params: tuple) -> list:
    """
    Создаёт и возвращает список объектов устройств.
    Принимает кортеж параметров контроллера.
    """

    return [Zont(*param) for param in params]


def create_devices_in_home_assistant():
    """
    Создаёт объекты устройств в Home Assistant
    """

    pass


def read_zont_publish_mqtt(devices: list) -> None:
    """
    Считывает показания с контроллера и публикует в mqtt.
    Принимает кортеж объектов контроллеров.
    """

    while True:
        Zont.update_data()

        for device in devices:
            topic = f'{TOPIC_MQTT_ZONT}{device.device_id}/'

            for values_temp in device.get_temperature():
                topic_temp = topic + 'temp/'
                topic_temp += str(values_temp['id'])
                client_mqtt.publish(
                    topic=topic_temp,
                    payload=json.dumps(
                        values_temp,
                        ensure_ascii=False
                    ),
                    retain=RETAIN_MQTT
                )

            client_mqtt.publish(
                topic=f'{topic}status',
                payload=json.dumps(
                    device.get_status_device(),
                    ensure_ascii=False
                ),
                retain=RETAIN_MQTT,
            )

        time.sleep(RETRY_TIME)


def main():

    # Запуск mqtt
    main_mqtt()

    # Запуск опроса
    read_zont_publish_mqtt(create_device(DEVICES_PARAM))


if __name__ == '__main__':
    main()
