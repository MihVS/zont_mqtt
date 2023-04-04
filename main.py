import json
import time

from app.home_assistant import Sensor, Climate
from app.models import Zont
from app.mqtt import client_mqtt, publish_state_to_mqtt
from app.mqtt import main as main_mqtt
from app.settings import RETAIN_MQTT, RETRY_TIME, CREATE_CONFIG_HA, LOGGER
from app.zont import (
    get_data_zont, get_list_state_for_mqtt
)


def publish_config_ha(zont: Zont, create_conf: bool) -> None:
    """
    Публикует конфигурации всех сущностей контроллера для автоматического
    добавления их в home assistant.
    Принимает список объектов контроллеров.
    """

    if create_conf:
        sensors = Sensor(zont)
        for topic, payload in sensors.config.items():
            client_mqtt.publish(
                topic=topic,
                payload=json.dumps(obj=payload, ensure_ascii=False),
                retain=RETAIN_MQTT
            )
        climate = Climate(zont)
        for topic, payload in climate.config.items():
            client_mqtt.publish(
                topic=topic,
                payload=json.dumps(obj=payload, ensure_ascii=False),
                retain=RETAIN_MQTT
            )


def loop_zont() -> None:
    """Запускает цикл опроса состояний контроллера и публикации в mqtt."""

    while True:
        try:
            client_mqtt.zont = Zont.parse_raw(get_data_zont())
            publish_state_to_mqtt(get_list_state_for_mqtt(client_mqtt.zont))
        except Exception as e:
            LOGGER.error(f'Произошла ошибка в цикле опроса: {e}')
        time.sleep(RETRY_TIME)


def main():

    # Запуск mqtt
    main_mqtt()

    # Публикуем конфиг в HA
    publish_config_ha(client_mqtt.zont, CREATE_CONFIG_HA)

    # Запуск опроса
    loop_zont()


if __name__ == '__main__':
    main()
