import krpc
from time import sleep

def start(vessel, space_center, connection):
    vessel.control.rcs = True

    periapsisTime = connection.add_stream(getattr, vessel.orbit, 'time_to_periapsis')
    time_to_periapsis = periapsisTime()

    vessel.auto_pilot.engage()
    vessel.auto_pilot.reference_frame = vessel.orbital_reference_frame
    vessel.auto_pilot.target_direction = (0.0, -1.0, 0.0)
    vessel.auto_pilot.wait()

    while time_to_periapsis > 50:
        if time_to_periapsis > 150:
            space_center.rails_warp_factor = 5
        else:
            space_center.rails_warp_factor = 3
        time_to_periapsis = periapsisTime()
    space_center.rails_warp_factor = 0
    
    sleep(10)

    # торможение на орбите
    while vessel.orbit.speed > 5:
        if vessel.orbit.speed <= 50:
            vessel.control.throttle = vessel.orbit.speed / 100
        else:
            vessel.control.throttle = 1
    vessel.control.throttle = 0

    altitudeControl = connection.add_stream(getattr, vessel.flight(), 'surface_altitude') # расстояние до поверхности

    # берем с запасом в 13к метров, с этой позиции начинаем торможение
    while altitudeControl() > vessel.flight().elevation + 13000:
        if altitudeControl() > vessel.flight().elevation + 40000:
            space_center.rails_warp_factor = 3
        else:
            space_center.rails_warp_factor = 1

        sleep(0.1)
    space_center.rails_warp_factor = 0

    vessel.auto_pilot.reference_frame = vessel.surface_velocity_reference_frame
    vessel.auto_pilot.target_direction = (0.0, -1.0, 0.0)
    vessel.auto_pilot.wait()

    # скорость относительно поверхности
    surface_velocity_Control = connection.add_stream(getattr, vessel.flight(vessel.orbit.body.reference_frame), 'speed')
    landing_final = True # флаг для перехода на последнюю ступень
    vessel.control.gear = True # посадочные опоры

    while altitudeControl() > 10:
        sleep(0.2)
        # надо будет добавить проверку на количество оставшихся ступеней, чтобы оно ненароком не перешло на то, что не надо
        if altitudeControl() <= 150 and landing_final:
            vessel.control.throttle = 0
            sleep(0.1)
            vessel.control.activate_next_stage() 
            landing_final = False
        print(f"Высота над поверхностью {altitudeControl():.2f}")
        speed = surface_velocity_Control()
        if speed > 100:
            vessel.control.throttle = 1
        elif speed > 15:
            vessel.control.throttle = speed / 100
        elif speed > 5 and altitudeControl() <= 1000:
            vessel.control.throttle += 0.01
        elif speed > 5 and altitudeControl() <= 50:
            vessel.control.throttle += 0.02
        elif speed < 2:
            vessel.control.throttle = 0
    vessel.control.throttle = 0

    print('Луна наша')