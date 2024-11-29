import krpc
from time import sleep

def start(vessel, space_center, connection):
    vessel.control.rcs = True
    orbit_height = 80000
    ascent_profile = 0.5 
    # константу восхождения берем 0.5 для опережения при построении орбиты, а так можно и 0.25, роли не играет

    vessel.control.throttle = 1 # запуск движков

    # чекаем наш апоцентр
    apoapsisControl = connection.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')

    # подключаем пилотирование и наклоняемся на 90 градусов
    vessel.auto_pilot.engage()
    vessel.auto_pilot.target_heading = 90

    # пока апоцентр меньше желаемой высоты орбиты, газуем
    while apoapsisControl() < orbit_height:
        # считаем угол, на который нужно нацелиться
        target_pitch = 90 - ((90/(orbit_height**ascent_profile))*(apoapsisControl()**ascent_profile))
        print(f'\nНакреняяемся на {target_pitch}')
        print(f'Апоцентр {apoapsisControl()}\n')

        # накреняем
        vessel.auto_pilot.target_pitch = target_pitch

        sleep(0.1)

    vessel.control.throttle = 0
    apoapsisTime = connection.add_stream(getattr, vessel.orbit, 'time_to_apoapsis')
    
    # чекаем наш перицентр
    periapsisControl = connection.add_stream(getattr, vessel.orbit, 'periapsis_altitude')
    
    # ускорение времени по приближению к апоцентру
    while(apoapsisTime() > 22):
        if(apoapsisTime() > 60):
            space_center.rails_warp_factor = 4
        else:
            space_center.rails_warp_factor = 0

        sleep(0.5)

    vessel.control.throttle = 0.5
    last_UT = space_center.ut
    last_time_to_apoapsis = apoapsisTime()
    while(periapsisControl() < orbit_height):
        sleep(0.2)
        time_to_apoapsis = apoapsisTime()
        UT = space_center.ut
        delta = (time_to_apoapsis - last_time_to_apoapsis) / (UT - last_UT)

        print("Время до апоцентра:", delta)

        # если перелетаем, то подгазовываем
        if delta < -0.3:
            vessel.control.throttle += 0.03
        elif delta < -0.1:
            vessel.control.throttle += 0.01
        # если апоцентр убегает, то притормаживаем
        if delta > 0.2:
            vessel.control.throttle -= 0.03
        elif delta > 0:
            vessel.control.throttle -= 0.01

        last_time_to_apoapsis = time_to_apoapsis
        last_UT = UT

    vessel.control.throttle = 0
    print("Апоцентр: ", apoapsisControl())
    print("Перицентр: ", periapsisControl())
    print("Орбита построена\n")
