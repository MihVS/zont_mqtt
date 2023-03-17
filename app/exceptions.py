class RequestAPIZONTError(Exception):
    """Ошибка запроса к сервису zont-online.ru/api"""
    pass


class ResponseAPIZONTError(Exception):
    """Ответ от API zont отличается от ожидаемого"""
    pass


class ENVError(Exception):
    """Ошибка доступности переменных окружения"""
    pass


class TypeSensorError(Exception):
    """Не верный тип сенсора"""
    pass


class MethodNotOverridden(Exception):
    """Не переопределён обязательный метод класса родителя"""
    pass
