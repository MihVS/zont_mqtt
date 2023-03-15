import json
import time

from app.mqtt import client_mqtt
from app.mqtt import main as main_mqtt
from app.settings import RETRY_TIME, RETAIN_MQTT
from app.zont import Zont
from configs.config_zont import DEVICES


def create_device(params: tuple) -> list:
    """
    Создаёт и возвращает список объектов устройств.
    Принимает кортеж параметров контроллера.
    """

    return [Zont(*param) for param in params]


def send_statuses(topics: dict) -> None:
    """Вспомогательная функция для отправки статусов сенсоров."""

    for topic, body in topics.items():
        client_mqtt.publish(
            topic=topic,
            payload=json.dumps(
                body,
                ensure_ascii=False
            ),
            retain=RETAIN_MQTT
        )


def read_zont_publish_mqtt(devices: list) -> None:
    """
    Считывает показания с контроллера и публикует в mqtt.
    Принимает кортеж объектов контроллеров.
    """

    while True:
        Zont.update_data()

        for device in devices:
            for sensor in Zont.available_sensors:
                send_statuses(device.get_state_topics(sensor))

        time.sleep(RETRY_TIME)


def main():

    # Запуск mqtt
    main_mqtt()

    # Запуск опроса
    read_zont_publish_mqtt(create_device(DEVICES))


if __name__ == '__main__':
    main()
