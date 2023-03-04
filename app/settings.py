import logging.config
from log.config_log import LOGGER_CONFIG

from dotenv import load_dotenv

load_dotenv()

logging.config.dictConfig(LOGGER_CONFIG)
_logger = logging.getLogger('script_logger')


RETRY_TIME = 60
