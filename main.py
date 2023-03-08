import threading
import time

from app.mqtt import client_mqtt
from app.zont import Zont
from app.settings import RETRY_TIME
from configs.config_zont import DEVICES_PARAM


def create_device(params: tuple) -> list:
    """
    Создаёт и возвращает список объектов устройств.
    Принимает кортеж параметров контроллера.
    """

    return [Zont(*param) for param in params]


def read_zont_publish_mqtt(devices):
    """
    Считывает показания с контроллера и публикует в mqtt.
    Принимает кортеж объектов контроллеров.
    """

    while True:
        Zont.update_data()

        for device in devices:
            print(device.get_temperature())

        time.sleep(RETRY_TIME)


def main():
    thr = threading.Thread(
        target=read_zont_publish_mqtt,
        args=create_device(DEVICES_PARAM),
        daemon=True
    )
    thr.start()


if __name__ == '__main__':
    main()
