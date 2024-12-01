import krpc
from time import sleep


def launchFromMoon(vessel):
    vessel.control.rcs = True
    v2 =  807.08 # вторая космическая скорость Луны (Муны, взято с доков по ксп)
    
    vessel.auto_pilot.engage()
    vessel.auto_pilot.reference_frame = vessel.orbital_reference_frame
    vessel.auto_pilot.target_heading = 0

    vessel.control.brakes = False

    print('Взлетаем')

    while vessel.orbit.speed < v2:
        if vessel.orbit.speed / v2 > 0.8:
            vessel.control.throttle = 0.5
        else:
            vessel.control.throttle = 1
    vessel.control.throttle = 0

    vessel.control.gear = False
    vessel.auto_pilot.disengage()
    sleep(10)

def orbitCorrection(vessel, space_center, connection):
    deceleration_height = 45000
    apoapsisTime = connection.add_stream(getattr, vessel.orbit, 'time_to_apoapsis')
    periapsisControl = connection.add_stream(getattr, vessel.orbit, 'periapsis_altitude')

    time_to_apoapsis = apoapsisTime()

    while time_to_apoapsis > 600:
        space_center.rails_warp_factor = 5
        time_to_apoapsis = apoapsisTime()
    
    space_center.rails_warp_factor = 0

    vessel.auto_pilot.engage()
    vessel.auto_pilot.reference_frame = vessel.orbital_reference_frame
    vessel.auto_pilot.target_direction = (0.0, -1.0, 0.0)
    vessel.auto_pilot.wait()

    while periapsisControl() > deceleration_height:
        if periapsisControl() > deceleration_height * 2:
            vessel.control.throttle += 0.001
        else:
            if vessel.control.throttle > 0.02:
                vessel.control.throttle -= 0.01
    vessel.control.throttle = 0
    vessel.auto_pilot.disengage()
    sleep(10)

def orbitDeceleration(vessel, space_center, connection):
    vessel.auto_pilot.engage()
    vessel.auto_pilot.reference_frame = vessel.orbital_reference_frame
    altitudeControl = connection.add_stream(getattr, vessel.flight(), 'surface_altitude')

    while altitudeControl() > 150000:
        sleep(0.2)
        if altitudeControl() < 1_000_000:
            space_center.rails_warp_factor = 2
        else: 
            space_center.rails_warp_factor = 5
    space_center.rails_warp_factor = 0

    vessel.auto_pilot.target_direction = (0.0, -1.0, 0.0)

    vessel.control.solar_panels = False
    vessel.control.antennas = False 
    vessel.control.lights = False
    vessel.control.radiators = True

def landing(vessel, connection):
    vessel.auto_pilot.target_direction = (0.0, -1.0, 0.0)
    vessel.auto_pilot.wait()
    apoapsisControl = connection.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
    altitudeControl = connection.add_stream(getattr, vessel.flight(), 'surface_altitude')

    while apoapsisControl() > 70000:
        if altitudeControl() < 100000:
            vessel.control.throttle = 1
    vessel.control.throttle = 0

    while altitudeControl() > 100:
        sleep(0.5)
        print(f'Высота над поверхностью: {altitudeControl():.2f}')
        if altitudeControl() < 30000:
            vessel.control.gear = True
            vessel.control.parachutes = True
            vessel.control.rcs = False
    
    vessel.auto_pilot.disengage()
    print('Успешное приземление')
