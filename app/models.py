from pydantic import BaseModel


class BaseEntityZONT(BaseModel):
    """Базовая модель сущностей контроллера"""

    id: int
    name: str


class HeatingCircuit(BaseEntityZONT):
    """Контур отопления"""

    status: str
    active: bool
    actual_temp: float | None
    is_off: bool
    target_temp: float | None
    current_mode: int | None
    target_min: float | None
    target_max: float | None


class HeatingMode(BaseEntityZONT):
    """Отопительные режимы"""

    can_be_applied: bool
    color: str | None


class Sensor(BaseEntityZONT):
    """Сенсоры"""

    type: str
    status: str
    value: float
    unit: str


class GuardZone(BaseEntityZONT):
    """Охранная зона"""

    state: str
    alarm: bool


class CustomControl(BaseEntityZONT):
    """Пользовательский элемент управления"""

    name: dict
    type: str
    status: bool


class Scenario(BaseEntityZONT):
    """Сценарий"""

    pass


class Device(BaseEntityZONT):
    """Модель контроллера"""

    model: str
    online: bool
    widget_type: str
    heating_circuits: list[HeatingCircuit]
    heating_modes: list[HeatingMode]
    sensors: list[Sensor]
    guard_zones: list[GuardZone]
    custom_controls: list[CustomControl]
    scenarios: list[Scenario]


class Zont(BaseModel):
    """Общий класс всех устройств"""

    devices: list[Device]
    ok: bool


# with open('../mytest/devices2.json') as f:
#     fl = f.read()
#     try:
#         dvc = Device.parse_raw(fl)
#     except ValidationError as e:
#         print(e)
#     else:
#         print(dvc.devices[0].sensors[1].value)
