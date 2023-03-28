import json
import sys
import time

from pydantic import ValidationError

from app.models import Zont
from app.mqtt import main as main_mqtt
from app.mqtt import client_mqtt
from app.settings import RETAIN_MQTT, CREATE_CONFIG_HA
from app.zont import (
    get_data_zont, get_list_state_for_mqtt, control_device
)
from app.home_assistant import Sensor


def publish_state_to_mqtt(state_list: list[tuple, ...]) -> None:
    """Публикует все параметры девайса в mqtt"""

    for state in state_list:
        client_mqtt.publish(*state, RETAIN_MQTT)


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


def main():

    # Запуск mqtt
    # main_mqtt()

    # Zont.update_data()

    # Публикуем конфиг в HA

    # Запуск опроса
    try:
        # zont = Zont.parse_raw(get_data_zont())
        control_device(
            client_mqtt.zont,
            'zont/278936/heating_circuits/8550/set',
            '25'
        )
        # publish_config_ha(client_mqtt.zont, CREATE_CONFIG_HA)
        # publish_state_to_mqtt(get_list_state_for_mqtt(client_mqtt.zont))
        # dev_cont = get_device_control_by_id(zont, 278936, 8550)
        # set_target_temp(*dev_cont, 24.3)
        # toggle_custom_button(zont.devices[1], zont.devices[1].custom_controls[4], False)
    except ValidationError as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    main()
    # while True:
    #     pass
