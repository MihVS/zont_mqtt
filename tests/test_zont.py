import unittest

from app.models import Zont, Device, ControlEntityZONT
from app.zont import (
    get_device_by_id, get_device_control_by_id
)


class TestZont(unittest.TestCase):
    """Тестируем функции для zont"""

    @classmethod
    def setUpClass(cls) -> None:
        """
        Подготовка прогона тестов.
        Вызывается один раз перед всеми тестами
        """
        with open('tests/test_data.json') as file:
            cls.test_data = file.read()

    def setUp(self) -> None:
        """Подготовка прогона теста. Вызывается перед каждым тестом."""
        self.zont = Zont.parse_raw(self.test_data)

    def test_get_device_control_by_id(self):
        """
        Тест функции получения объектов устройства и управления по их id
        """
        result = get_device_control_by_id(self.zont, 123456, 8595)
        self.assertIsInstance(
            result,
            tuple,
            'Функция должна возвращать кортеж.'
        )
        self.assertIsNone(
            get_device_control_by_id(self.zont, 123456, 1234),
            ('Функция не возвращает None при '
             'не корректном id объекта управления')
        )
        self.assertIsInstance(
            result[0],
            Device,
            'Функция не возвращает объект Device'
        )
        self.assertIsInstance(
            result[1],
            ControlEntityZONT,
            'Функция не возвращает объект ControlEntityZONT'
        )

    def test_get_device_by_id(self):
        """Тест функции получения объекта Device по id"""
        device = get_device_by_id(self.zont, 123456)
        self.assertIsInstance(
            device,
            Device,
            'Функция не возвращает объект девайса'
        )
        self.assertIs(
            device,
            self.zont.devices[0],
            'Функция не возвращает правильный объект девайса'
        )
        self.assertIsNone(
            get_device_by_id(self.zont, 000000),
            'Функция не возвращает None при не существующем id девайса'
        )


if __name__ == '__main__':
    unittest.main()
