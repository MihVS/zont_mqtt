import threading
import time

from app.mqtt import client_mqtt
from app.mqtt import main as main_mqtt
from app.zont import Zont
from app.settings import RETRY_TIME, TOPIC_MQTT_ZONT
from configs.config_zont import DEVICES_PARAM


def create_device(params: tuple) -> list:
    """
    Создаёт и возвращает список объектов устройств.
    Принимает кортеж параметров контроллера.
    """

    return [Zont(*param) for param in params]


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
                topic_temp += str(values_temp.pop('id'))
                client_mqtt.publish(
                    topic=topic_temp,
                    payload=str(values_temp),
                    retain=False
                )



        time.sleep(RETRY_TIME)


def main():

    # Запуск mqtt
    main_mqtt()

    # Запуск потока опроса контроллера
    thr = threading.Thread(
        target=read_zont_publish_mqtt,
        args=[create_device(DEVICES_PARAM)],
        daemon=True
    )
    thr.start()


if __name__ == '__main__':
    main()
    while True:
        pass
