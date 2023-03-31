import logging.config
import os
from configs.config_log import LOGGER_CONFIG

from dotenv import load_dotenv

load_dotenv()

logging.config.dictConfig(LOGGER_CONFIG)
LOGGER = logging.getLogger('script_logger')

RETRY_TIME = 60
CONNECT_COUNT_MQTT = 30
HOST_MQTT = os.getenv('HOSTMQTT')
PORT_MQTT = int(os.getenv('PORTMQTT'))
CLIENT_MQTT = 'zont'
USER_NAME_MQTT = os.getenv('USERNAMEMQTT')
PSWD_MQTT = os.getenv('PSWDMQTT')
TOPIC_MQTT_ZONT = 'zont'
TOPIC_MQTT_HA = 'homeassistant'
CREATE_CONFIG_HA = True
RETAIN_MQTT = True

HEADERS = {
        'X-ZONT-Token': os.getenv('XZONTTOKEN'),
        'X-ZONT-Client': os.getenv('XZONTCLIENT'),
        'Content-Type': 'application/json'
    }

URL_GET_DEVICES = 'https://lk.zont-online.ru/api/widget/v2/get_devices'
BODY_GET_DEVICES = {}
URL_SET_TARGET_TEMP = 'https://lk.zont-online.ru/api/widget/v2/set_target_temp'
URL_SET_GUARD = 'https://lk.zont-online.ru/api/widget/v2/set_guard'
URL_ACTIVATE_HEATING_MODE = (
    'https://lk.zont-online.ru/api/widget/v2/activate_heating_mode'
)
URL_TRIGGER_CUSTOM_BUTTON = (
    'https://lk.zont-online.ru/api/widget/v2/trigger_custom_button'
)
