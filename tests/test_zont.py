import logging
import unittest
from unittest.mock import patch

from app.models import Zont, Device, ControlEntityZONT
from app.zont import (
    get_device_by_id, get_device_control_by_id, get_list_state_for_mqtt,
    is_correct_temperature, is_correct_activate_mode, is_correct_toggle
)
from tests.fixtures.test_data import TEST_LIST_STATE


logging.disable(logging.NOTSET)


class TestZont(unittest.TestCase):
    """Тестируем функции для zont"""

    @classmethod
    def setUpClass(cls) -> None:
        """
        Подготовка прогона тестов.
        Вызывается один раз перед всеми тестами
        """
        with open('tests/fixtures/test_data.json') as file:
            cls.test_data = file.read()

    def setUp(self) -> None:
        """Подготовка прогона теста. Вызывается перед каждым тестом."""
        self.zont = Zont.parse_raw(self.test_data)

    def test_get_device_control_by_id(self):
        """
        Тест функции получения объектов устройства и управления по их id
        """
        result = get_device_control_by_id(self.zont, 123456, 8550)
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

    def test_get_list_state_for_mqtt(self):
        """
        Тест получения списка кортежей типа (topic, payload)
        для публикации статусов в mqtt.
        """
        self.assertEqual(
            get_list_state_for_mqtt(self.zont),
            TEST_LIST_STATE,
            'Не правильно формируется список кортежей статусов'
        )
        self.assertEqual(
            get_list_state_for_mqtt(self.zont, ('online',)),
            [('zont/123456/online', True)],
            'Неправильно работает фильтр полей функции'
        )

    def test_is_correct_temperature(self):
        """Тест функции для проверки корректной температуры."""
        self.assertTrue(
            is_correct_temperature('26.3'),
            'Правильное значение температуры не проходит.'
        )
        self.assertFalse(
            is_correct_temperature('35.1'),
            'Ошибка проверки в верхнем пороге температуры.'
        )
        self.assertFalse(
            is_correct_temperature('4.9'),
            'Ошибка проверки в нижнем пороге температуры.'
        )
        self.assertFalse(
            is_correct_temperature('zont'),
            'Неправильная работа с символьным значением температуры.'
        )

    def test_is_correct_activate_mode(self):
        """
        Тест функции проверки корректность команды
        на активацию режима отопления
        """
        self.assertTrue(
            is_correct_activate_mode('activate'),
            'Правильная команда активации режима отопления не проходит.'
        )
        self.assertFalse(
            is_correct_activate_mode('zont'),
            'Неверная команда активации режима отопления не должна проходить.'
        )

    def test_is_correct_toggle(self):
        """
        Тест функции проверки корректности команды на переключение
        состояния ВКЛЮЧЕНО и ВЫКЛЮЧЕНО.
        """
        self.assertTrue(
            is_correct_toggle('on'),
            'Правильная команда на включение не проходит.'
        )
        self.assertTrue(
            is_correct_toggle('off'),
            'Правильная команда на выключение не проходит.'
        )
        self.assertTrue(
            is_correct_toggle('ON'),
            'Правильная команда в верхнем регистре не проходит.'
        )
        self.assertFalse(
            is_correct_toggle('вкл'),
            'Неправильная команда переключение состояния не должна проходить.'
        )

    # @patch('app.zont.requests.post')
    # def test_control_device_set_target_temp(self, mock_post):
    #     """
    #     Тест отправки команды для изменения заданной температуры при
    #     получении корректных данных в mqtt.
    #     """
    #


if __name__ == '__main__':
    unittest.main()
