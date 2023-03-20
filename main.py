import json
import sys
import time
from http import HTTPStatus
from pydantic import ValidationError

from app.models import Zont
from app.zont import get_data_zont, send_state_to_mqtt

from app.home_assistant import Temperature
from app.mqtt import client_mqtt
from app.mqtt import main as main_mqtt
from app.settings import (
    RETRY_TIME, RETAIN_MQTT, HEADERS, BODY_REQUEST_DEVICES,
    URL_REQUEST_DEVICES,
)




# def send_statuses(topics: dict, retain) -> None:
#     """Вспомогательная функция для отправки статусов сенсоров."""
#
#     for topic, body in topics.items():
#         client_mqtt.publish(
#             topic=topic,
#             payload=json.dumps(
#                 body,
#                 ensure_ascii=False
#             ),
#             retain=retain
#         )
#
#
# def read_zont_publish_mqtt(devices: list[Zont]) -> None:
#     """
#     Считывает показания с контроллера и публикует в mqtt.
#     Принимает список объектов контроллеров.
#     """
#
#     while True:
#         try:
#             Zont.update_data()
#
#             for device in devices:
#                 for entity in Zont.available_entities:
#                     send_statuses(
#                         device.get_state_topics(entity),
#                         RETAIN_MQTT
#                     )
#         except Exception as e:
#             _logger.error(f'Произошла ошибка опроса контроллера: {e}')
#
#         time.sleep(RETRY_TIME)


# def publish_config_ha(devices: list[Zont], create_conf: bool) -> None:
#     """
#     Публикует конфигурации всех сущностей контроллера для автоматического
#     добавления их в home assistant.
#     Принимает список объектов контроллеров.
#     """
#
#     if create_conf:
#         for device in devices:
#             temps = Temperature(device)
#             send_statuses(temps.config, False)


def main():

    # Запуск mqtt
    main_mqtt()

    # Zont.update_data()

    # Публикуем конфиг в HA

    # Запуск опроса
    try:
        zont = Zont.parse_raw(get_data_zont())
        print(zont.devices[1])
        send_state_to_mqtt(zont)

    except ValidationError as e:
        print(e)
        sys.exit(1)

    send_state_to_mqtt(zont, ('sensors',))


if __name__ == '__main__':
    main()
