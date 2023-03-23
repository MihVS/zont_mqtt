import unittest
from app.models import Zont, Device
from app.zont import get_device_by_id

with open('tests/test_data.json') as f:
    fl = f.read()


class TestZont(unittest.TestCase):
    """Тестируем функции для zont"""

    def setUp(self) -> None:
        """Подготовка прогона теста. Вызывается перед каждым тестом."""
        self.zont = Zont.parse_raw(fl)

    def test_get_device_by_id_is_obj(self):
        """Тест функции get_device_by_id получения объекта Device по id"""
        self.assertIs(
            get_device_by_id(self.zont, 123456),
            self.zont.devices[0],
            'Функция get_device_by_id не возвращает правильный объект девайса'
        )

    def test_get_device_by_id_is_none(self):
        """Тест функции get_device_by_id при не существующем id device"""
        device = get_device_by_id(self.zont, 000000)
        self.assertIsNone(
            device,
            ('Функция get_device_by_id не возвращает None '
             'при не существующем id')
        )
