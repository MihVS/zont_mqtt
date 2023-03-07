from typing import NamedTuple


class Device(NamedTuple):
    name: str
    id: int
    model: str


# Поменяйте name, id, model на свои.
# И измените название файла на config_zont.py
DEVICES = (
    Device(name='Вятка', id=123456, model='H2000_PRO'),
)
