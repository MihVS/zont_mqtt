class HomeAssistant:
    """Создаёт объекты девайсов в HA"""

    def __init__(self, name, state_topic):
        self.name = name
        self.state_topic = state_topic


