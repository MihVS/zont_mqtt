import logging.config
import os
from configs.config_log import LOGGER_CONFIG

from dotenv import load_dotenv

load_dotenv()

logging.config.dictConfig(LOGGER_CONFIG)
_logger = logging.getLogger('script_logger')

RETRY_TIME = 60
CONNECT_COUNT_MQTT = 30
HOST_MQTT = os.getenv('HOSTMQTT')
PORT_MQTT = int(os.getenv('PORTMQTT'))
CLIENT_MQTT = 'zont'
USER_NAME_MQTT = os.getenv('USERNAMEMQTT')
PSWD_MQTT = os.getenv('PSWDMQTT')

HEADERS = {
        'X-ZONT-Token': os.getenv('XZONTTOKEN'),
        'X-ZONT-Client': os.getenv('XZONTCLIENT'),
        'Content-Type': 'application/json'
    }

URL_REQUEST_DEVICES = 'https://zont-online.ru/api/devices'
BODY_REQUEST_DEVICES = {'load_io': True}

