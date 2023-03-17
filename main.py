import json
import time

from app.home_assistant import Temperature
from app.mqtt import client_mqtt
from app.mqtt import main as main_mqtt
from app.settings import RETRY_TIME, RETAIN_MQTT, CREATE_CONFIG_HA, _logger
from app.zont import Zont
from configs.config_zont import PARAMDEVICES


def create_device(params: tuple) -> list[Zont]:
    """
    Создаёт и возвращает список объектов устройств.
    Принимает кортеж параметров контроллера.
    """

    return [Zont(*param) for param in params]


def send_statuses(topics: dict, retain) -> None:
    """Вспомогательная функция для отправки статусов сенсоров."""

    for topic, body in topics.items():
        client_mqtt.publish(
            topic=topic,
            payload=json.dumps(
                body,
                ensure_ascii=False
            ),
            retain=retain
        )


def read_zont_publish_mqtt(devices: list[Zont]) -> None:
    """
    Считывает показания с контроллера и публикует в mqtt.
    Принимает список объектов контроллеров.
    """

    while True:
        try:
            Zont.update_data()

            for device in devices:
                for entity in Zont.available_entities:
                    send_statuses(
                        device.get_state_topics(entity),
                        RETAIN_MQTT
                    )
        except Exception as e:
            _logger.error(f'Произошла ошибка опроса контроллера: {e}')

        time.sleep(RETRY_TIME)


def publish_config_ha(devices: list[Zont], create_conf: bool) -> None:
    """
    Публикует конфигурации всех сущностей контроллера для автоматического
    добавления их в home assistant.
    Принимает список объектов контроллеров.
    """

    if create_conf:
        for device in devices:
            temps = Temperature(device)
            send_statuses(temps.config, False)


def main():

    # Запуск mqtt
    main_mqtt()

    list_devices = create_device(params=PARAMDEVICES)
    Zont.update_data()

    # Публикуем конфиг в HA
    publish_config_ha(devices=list_devices, create_conf=CREATE_CONFIG_HA)

    # Запуск опроса
    read_zont_publish_mqtt(devices=list_devices)


if __name__ == '__main__':
    main()
