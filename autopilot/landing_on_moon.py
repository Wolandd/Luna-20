import krpc
from time import sleep
import math

def start(vessel, space_center, connection):
    vessel.control.rcs = True

    periapsisTime = connection.add_stream(getattr, vessel.orbit, 'time_to_periapsis')
    time_to_periapsis = periapsisTime()

    vessel.auto_pilot.engage()
    vessel.auto_pilot.reference_frame = vessel.orbital_reference_frame
    vessel.auto_pilot.target_direction = (0.0, -1.0, 0.0)

    while time_to_periapsis > 50:
        if time_to_periapsis > 150:
            space_center.rails_warp_factor = 5
        else:
            space_center.rails_warp_factor = 3
        time_to_periapsis = periapsisTime()
    space_center.rails_warp_factor = 0
    
    sleep(10)

    while vessel.orbit.speed > 1:
        if vessel.orbit.speed > 50:
            vessel.control.throttle = vessel.orbit.speed / 100
        else:
            vessel.control.throttle = 1
    vessel.control.throttle = 0