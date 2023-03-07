class RequestAPIZONTError(Exception):
    """Ошибка запроса к сервису zont-online.ru/api"""
    pass


class ResponseAPIZONTError(Exception):
    """Ответ от API zont отличается от ожидаемого"""
    pass


class ENVError(Exception):
    """Ошибка доступности переменных окружения"""
    pass
