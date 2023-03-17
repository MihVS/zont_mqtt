from typing import NamedTuple


class Device(NamedTuple):
    name: str
    id: int
    model: str


# Поменяйте name, id, model на свои.
# Измените название файла на config_zont.py
PARAMDEVICES = (
    Device(name='Вятка', id=123456, model='H2000_PRO'),
)
