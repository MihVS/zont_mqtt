from app.zont import Zont


h = Zont(name='Единение', device_id=278936, model='H2000_PRO')
h.update_data()
h.get_temperature()

if __name__ == '__main__':
    pass
