import logging
import unittest
from unittest.mock import patch

from app.models import Zont, Device, ControlEntityZONT
from app.zont import (
    get_device_by_id, get_device_control_by_id, get_list_state_for_mqtt,
    is_correct_temperature, is_correct_activate_mode, is_correct_toggle,
    control_device, get_min_max_values_temp, get_current_mode_name
)
from tests.fixtures.test_data import TEST_LIST_STATE

logging.disable(logging.CRITICAL)


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
        Тест функции получения объектов устройства и управления по их id.
        """
        result = get_device_control_by_id(self.zont, 123456, 8550)
        self.assertIsInstance(
            result,
            tuple,
            'Функция должна возвращать кортеж при цифровых значениях id'
        )
        self.assertIsInstance(
            get_device_control_by_id(self.zont, '123456', '8550'),
            tuple,
            'Функция должна возвращать кортеж при строковых значениях id'
        )
        self.assertIsNone(
            get_device_control_by_id(self.zont, '123456', 'xxxx'),
            ('Функция не возвращает None при '
             'не корректном id объекта управления')
        )
        self.assertIsNone(
            get_device_control_by_id(self.zont, 'xxxxxx', '8550'),
            ('Функция не возвращает None при '
             'не корректном id объекта управления')
        )
        self.assertIsNone(
            get_device_control_by_id(self.zont, 123456, 1234),
            ('Функция не возвращает None при '
             'не корректном id объекта управления')
        )
        self.assertIsNone(
            get_device_control_by_id(self.zont, 654321, 8550),
            ('Функция не возвращает None при '
             'не корректном id устройства')
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

    def test_get_min_max_values_temp(self):
        """
        Тест функции получения макс и мин температур по названию контура.
        """
        self.assertEqual(
            get_min_max_values_temp('Тёплый пол'),
            (15, 50),
            'Контур тёплого пола не распознан'
        )
        self.assertEqual(
            get_min_max_values_temp('ПОЛ'),
            (15, 50),
            'Контур тёплого пола не распознан'
        )
        self.assertEqual(
            get_min_max_values_temp('ГОРЯЧАЯ ВОДА'),
            (5, 75),
            'Контур ГВС не распознан'
        )
        self.assertEqual(
            get_min_max_values_temp('ГВС газ'),
            (5, 75),
            'Контур ГВС не распознан'
        )
        self.assertEqual(
            get_min_max_values_temp('1 этаж'),
            (5, 35),
            'Контур ГВС не распознан'
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

    @patch('app.zont.get_data_zont')
    @patch('app.mqtt.publish_state_to_mqtt')
    @patch('app.zont.set_target_temp')
    def test_control_device_set_target_temp(
            self, mock_set_target_temp,
            mock_publish_state_to_mqtt,
            mock_get_data_zont
    ):
        """
        Тест отправки команды для изменения заданной температуры при
        получении корректных данных в mqtt.
        """
        mock_get_data_zont.return_value = self.test_data
        control_device(
            self.zont,
            'zont/123456/heating_circuits/8550/set',
            '25.5',
            mock_publish_state_to_mqtt
        )
        mock_set_target_temp.assert_called()

    @patch('app.zont.get_data_zont')
    @patch('app.mqtt.publish_state_to_mqtt')
    @patch('app.zont.activate_heating_mode')
    def test_control_device_activate_heating_mode(
            self, mock_activate_heating_mode,
            mock_publish_state_to_mqtt,
            mock_get_data_zont
    ):
        """
        Тест активации режима отопления при получении корректных данных в mqtt.
        """
        mock_get_data_zont.return_value = self.test_data
        control_device(
            self.zont,
            'zont/123456/heating_modes/8389/set',
            'activate',
            mock_publish_state_to_mqtt
        )
        mock_activate_heating_mode.assert_called()

    @patch('app.zont.get_data_zont')
    @patch('app.mqtt.publish_state_to_mqtt')
    @patch('app.zont.toggle_custom_button')
    def test_control_torn_on_custom_button(
            self, mock_toggle_custom_button,
            mock_publish_state_to_mqtt,
            mock_get_data_zont
    ):
        """
        Тест включения кнопки при получении корректных данных в mqtt.
        """
        mock_get_data_zont.return_value = self.test_data
        control_device(
            self.zont,
            'zont/123456/custom_controls/8507/set',
            'on',
            mock_publish_state_to_mqtt
        )
        mock_toggle_custom_button.assert_called()

    @patch('app.zont.get_data_zont')
    @patch('app.mqtt.publish_state_to_mqtt')
    @patch('app.zont.toggle_custom_button')
    def test_control_torn_off_custom_button(
            self, mock_toggle_custom_button,
            mock_publish_state_to_mqtt,
            mock_get_data_zont
    ):
        """
        Тест выключения кнопки при получении корректных данных в mqtt.
        """
        mock_get_data_zont.return_value = self.test_data
        control_device(
            self.zont,
            'zont/123456/custom_controls/8507/set',
            'off',
            mock_publish_state_to_mqtt
        )
        mock_toggle_custom_button.assert_called()

    @patch('app.zont.get_data_zont')
    @patch('app.mqtt.publish_state_to_mqtt')
    @patch('app.zont.set_guard')
    def test_control_torn_on_guard(
            self, mock_set_guard,
            mock_publish_state_to_mqtt,
            mock_get_data_zont
    ):
        """
        Тест включения охраны при получении корректных данных в mqtt.
        """
        mock_get_data_zont.return_value = self.test_data
        control_device(
            self.zont,
            'zont/123456/guard_zones/9413/set',
            'on',
            mock_publish_state_to_mqtt
        )
        mock_set_guard.assert_called()

    @patch('app.zont.get_data_zont')
    @patch('app.mqtt.publish_state_to_mqtt')
    @patch('app.zont.set_guard')
    def test_control_torn_off_guard(
            self, mock_set_guard,
            mock_publish_state_to_mqtt,
            mock_get_data_zont
    ):
        """
        Тест выключения охраны при получении корректных данных в mqtt.
        """
        mock_get_data_zont.return_value = self.test_data
        control_device(
            self.zont,
            'zont/123456/guard_zones/9413/set',
            'off',
            mock_publish_state_to_mqtt
        )
        mock_set_guard.assert_called()

    @patch('app.zont.get_data_zont')
    @patch('app.mqtt.publish_state_to_mqtt')
    @patch('app.zont.set_guard')
    def test_control_device_bad_control_name(
            self, mock_set_guard,
            mock_publish_state_to_mqtt,
            mock_get_data_zont
    ):
        """
        Тест функции управления устройством при получении
        некорректного имени управляемого объекта в mqtt.
        """
        mock_get_data_zont.return_value = self.test_data
        control_device(
            self.zont,
            'zont/123456/xxxxxx/9413/set',
            'on',
            mock_publish_state_to_mqtt
        )
        mock_set_guard.assert_not_called()

    @patch('app.zont.get_data_zont')
    @patch('app.mqtt.publish_state_to_mqtt')
    @patch('app.zont.set_guard')
    def test_control_device_bad_root_topic(
            self, mock_set_guard,
            mock_publish_state_to_mqtt,
            mock_get_data_zont
    ):
        """
        Тест функции управления устройством при получении
        некорректного root топика в mqtt.
        """
        mock_get_data_zont.return_value = self.test_data
        control_device(
            self.zont,
            'xxxx/123456/guard_zones/9413/set',
            'on',
            mock_publish_state_to_mqtt
        )
        mock_set_guard.assert_not_called()

    @patch('app.zont.get_data_zont')
    @patch('app.mqtt.publish_state_to_mqtt')
    @patch('app.zont.set_guard')
    def test_control_device_bad_finish_topic(
            self, mock_set_guard,
            mock_publish_state_to_mqtt,
            mock_get_data_zont
    ):
        """
        Тест функции управления устройством при получении
        некорректного окончания топика в mqtt.
        """
        mock_get_data_zont.return_value = self.test_data
        control_device(
            self.zont,
            'zont/123456/guard_zones/9413/set/xxx',
            'on',
            mock_publish_state_to_mqtt
        )
        mock_set_guard.assert_not_called()

    def test_get_current_mode_name(self):
        """Тест получения вид отопительного режима из названия"""
        self.assertEqual(
            get_current_mode_name('Комфорт'),
            'comfort',
            'Не правильное извлечение вида отопительного режима из имени'
        )
        self.assertEqual(
            get_current_mode_name('Эконом'),
            'eco',
            'Не правильное извлечение вида отопительного режима из имени'
        )
        self.assertIsNone(
            get_current_mode_name('Чиллл'),
            'Не возвращается None при неизвестном имени'
        )


if __name__ == '__main__':
    unittest.main()
