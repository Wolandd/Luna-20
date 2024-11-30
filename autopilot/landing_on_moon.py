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
    while altitudeControl() > vessel.flight().elevation + 10000:
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
    stage_check = vessel.control.current_stage # проверка ступени, нужно, чтобы при посадки перейти на последнюю в случае чего
    vessel.control.gear = True # посадочные опоры

    while altitudeControl() > 10:
        vessel.auto_pilot.target_direction = (0.0, -1.0, 0.0)
        vessel.auto_pilot.wait()
        sleep(0.2)
        if altitudeControl() <= 150 and stage_check == 3:
            vessel.control.throttle = 0
            sleep(0.1)
            vessel.control.activate_next_stage() 
            stage_check = vessel.control.current_stage
        print(f"Высота над поверхностью: {altitudeControl():.2f}")
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
    vessel.control.brakes = True # торможение (группа действий для опор)

    print('Луна наша')
    sleep(10)

def drilling(vessel, space_center, connection):
    drill = vessel.parts.resource_harvesters[0]
    print("Опускаем бур")
    drill.deployed = True
    sleep(5)
    print("Получаем образец грунта")
    drill.active = True
    sleep(20)
    print("Выключаем")
    drill.active = False
    sleep(0.5)
    print("Складываем бур")
    drill.deployed = False
    sleep(10)
