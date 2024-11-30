import krpc
from time import sleep
import math

def start(vessel, space_center, connection):
    vessel.control.rcs = True

    # раскрываем солнечные панели, антены и свет
    vessel.control.solar_panels = True
    vessel.control.antennas = True 
    vessel.control.lights = True

    moon = space_center.bodies["Mun"]
    moon_orbit = moon.orbit
    moon_radius = moon_orbit.radius

    target_semi_major_axis = moon_orbit.semi_major_axis # большая полуось орбиты Луны (половина длины большой оси эллипса орбиты)
    hohmann_semi_major_axis = target_semi_major_axis / 2 # большая полуось орбиты для Гомановской траектории
    optimal_phase_angle_rad = 2 * math.pi * (1 / (2 * (target_semi_major_axis ** 3 / hohmann_semi_major_axis ** 3) ** (1 / 2))) # оптимальный фазовый угол (по законам Кеплера) в радианах
    optimal_phase_angle_deg = 180 - optimal_phase_angle_rad * 180 / math.pi # то же самое, но в градусах

    vessel.auto_pilot.engage()
    vessel.auto_pilot.reference_frame = vessel.orbital_reference_frame
    vessel.auto_pilot.target_direction = (0.0, 1.0, 0.0) # направляем ракету по движению

    previous_phase_angle_deg = 0
    phase_angle_decreasing = False
    space_center.rails_warp_factor = 0

    while True:
        current_time = space_center.ut
        moon_position = moon_orbit.position_at(current_time, moon.reference_frame)
        vessel_position = vessel.orbit.position_at(current_time, moon.reference_frame)
        vessel_radius = vessel.orbit.radius

        distance = math.dist(moon_position, vessel_position) # расстояние до Луны

        # вычисляем текущий фазовый угол, обрабатываем ошибку из acos
        try:
            current_phase_angle_rad = math.acos((moon_radius**2 + vessel_radius**2 - distance**2) / (2 * moon_radius * vessel_radius))
            current_phase_angle_deg = current_phase_angle_rad * 180 / math.pi
        except ValueError:
            print("Ошибка, считать не получается\n")
            sleep(1)
            continue

        phase_angle_decreasing = previous_phase_angle_deg - current_phase_angle_deg > 0 # проверяем, уменьшается ли фазовый угол

        phase_angle_difference = abs(current_phase_angle_deg - optimal_phase_angle_deg)
        if phase_angle_difference <= 1 and phase_angle_decreasing:
            break  # если разница между углами мала
        elif phase_angle_difference > 20 and phase_angle_decreasing:
            space_center.rails_warp_factor = 2 # если угол уменьшается, но разнциа маленькая, то ускоряем
        elif not phase_angle_decreasing:
            space_center.rails_warp_factor = 4 # если угол не уменьшается, то сильно ускоряем
        else:
            space_center.rails_warp_factor = 0


        print(f"Фазовый угол: {current_phase_angle_deg:.2f}, Необходимый: {optimal_phase_angle_deg:.2f}")

        previous_phase_angle_deg = current_phase_angle_deg
        sleep(1)

    print("Угол есть, газуем\n")
    space_center.rails_warp_factor = 0

    r1 = vessel.orbit.radius # радиус начальной орбиты
    r2 = moon_radius # целевой радиус орбиты
    rd = r2 / r1 # отношение радиусов
    v1 = vessel.orbit.speed # начальная орбитальная скорость
    delta_velocity = v1*(((2 * rd) / (rd + 1))**0.5 - 1) # ускорение дельта v для перехода на эллиптическую траекторию
    delta_deceleration = (v1 / (rd**0.5)) * (1 - (2 / (rd + 1))**0.5) # ускорение торможения для перехода на окололунную орбиту
    print(v1 - delta_deceleration)
    
    print(v1, rd, delta_velocity)
    while vessel.orbit.speed < (v1 + delta_velocity):
        if vessel.orbit.speed / (v1 + delta_velocity) > 0.97:
            vessel.control.throttle = 0.5
        else:
            vessel.control.throttle = 1
    vessel.control.throttle = 0

    print('Летим к Луне\n')

    periapsisTime = connection.add_stream(getattr, vessel.orbit, 'time_to_periapsis')

    time_to_periapsis = periapsisTime()

    while time_to_periapsis > 600:
        space_center.rails_warp_factor = 5
        time_to_periapsis = periapsisTime()
    
    space_center.rails_warp_factor = 0
    vessel.auto_pilot.target_direction = (0.0, -1.0, 0.0) # направляем ракету против движения

    v = vessel.orbit.speed
    while vessel.orbit.speed > (v - delta_deceleration):
        if vessel.orbit.speed / (v - delta_deceleration) > 0.97:
            vessel.control.throttle = 0.5
        else:
            vessel.control.throttle = 1
    vessel.control.throttle = 0
    vessel.auto_pilot.disengage()

    print('Орбита у Луны построена\n')
    sleep(10)