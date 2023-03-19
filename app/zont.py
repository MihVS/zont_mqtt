from pydantic import BaseModel, ValidationError


class BaseEntityZONT(BaseModel):
    """Базовая модель сущностей контроллера"""

    id: int
    name: str


class HeatingCircuit(BaseEntityZONT):
    """Контур отопления"""

    status: str
    active: bool
    actual_temp: float
    is_off: bool
    target_temp: float | None
    current_mode: int | None
    target_min: float
    target_max: float


class HeatingMode(BaseEntityZONT):
    """Отопительные режимы"""

    can_be_applied: bool
    color: str


class Sensor(BaseEntityZONT):
    """Сенсоры"""

    type: str
    status: str
    value: float
    unit: str


class PLC(BaseEntityZONT):
    """Модель контроллера"""

    model: str
    online: bool
    widget_type: str
    heating_circuits: list[HeatingCircuit]
    heating_modes: list[HeatingMode]
    sensors: list[Sensor]


class Zont(BaseModel):
    """Общий класс всех устройств"""

    devices: list[PLC]
    ok: bool


# with open('../mytest/devices2.json') as f:
#     fl = f.read()
#     try:
#         dvc = Device.parse_raw(fl)
#     except ValidationError as e:
#         print(e)
#     else:
#         print(dvc.devices[0].sensors[1].value)
