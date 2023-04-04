TEST_LIST_STATE = [
    ('zont/123456/id', 123456),
    ('zont/123456/name', 'Объект1'),
    ('zont/123456/model', 'H2000_PRO'),
    ('zont/123456/online', True),
    ('zont/123456/widget_type', 'z3k'),
    (
        'zont/123456/heating_circuits/8550',
        '{"id": 8550, "name": "1 этаж", "status": "ok", "active": false, '
        '"actual_temp": 24.6, "is_off": false, "target_temp": 24.0, '
        '"current_mode": 8389, "current_mode_name": "comfort", '
        '"target_min": -30.0, "target_max": 100.0}'
    ),
    (
        'zont/123456/heating_modes/8389',
        '{"id": 8389, "name": "Комфорт", "can_be_applied": true, '
        '"color": "#33aa66"}'
    ),
    (
        'zont/123456/sensors/0',
        '{"id": 0, "name": "Напряжение питания", "type": "voltage", '
        '"status": "ok", "value": 12.2, "unit": "В"}'
    ),
    (
        'zont/123456/sensors/8534',
        '{"id": 8534, "name": "Воздух 1 эт.", "type": "temperature", '
        '"status": "ok", "value": 24.6, "unit": "°C"}'
    ),
    (
        'zont/123456/guard_zones/9413',
        '{"id": 9413, "name": "Охрана дома", "state": "disabled", '
        '"alarm": false}'
    ),
    (
        'zont/123456/custom_controls/8507',
        '{"id": 8507, "name": {"when_active": "Свет 1 этаж включен", '
        '"when_inactive": "Свет 1 этаж выключен"}, "type": "toggle_button", '
        '"status": true}'
    )
]
