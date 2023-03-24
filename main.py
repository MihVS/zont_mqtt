import sys

from pydantic import ValidationError

from app.models import Zont
from app.mqtt import main as main_mqtt
from app.zont import (
    get_data_zont, send_state_to_mqtt
)


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
        send_state_to_mqtt(zont)
        # dev_cont = get_device_control_by_id(zont, 278936, 8550)
        # set_target_temp(*dev_cont, 24.3)
        # toggle_custom_button(zont.devices[1], zont.devices[1].custom_controls[4], False)
    except ValidationError as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    main()
