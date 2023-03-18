from pydantic import BaseModel, ValidationError


class HeatingCircuit(BaseModel):
    """Контур отопления"""

    id: int
    name: str
    status: str
    active: bool
    actual_temp: float
    is_off: bool
    target_temp: float | None
    current_mode: int | None
    target_min: float
    target_max: float


class HeatingMode(BaseModel):
    """Отопительные режимы"""

    id: int
    name: str
    can_be_applied: bool
    color: str


class Sensor(BaseModel):
    """Сенсоры"""
    id: int
    name: str
    type: str
    status: str
    value: float
    unit: str


class Zont(BaseModel):
    """Модель контроллера"""

    id: int
    name: str
    model: str
    online: bool
    widget_type: str
    heating_circuits: list[HeatingCircuit]
    heating_modes: list[HeatingMode]
    sensors: list[Sensor]


class Device(BaseModel):
    """Общий класс всех устройств"""

    devices: list[Zont]
    ok: bool


with open('../mytest/devices2.json') as f:
    fl = f.read()
    try:
        dvc = Device.parse_raw(fl)
    except ValidationError as e:
        print(e.json())
    else:
        print(dvc.devices[0].sensors[1].value)
