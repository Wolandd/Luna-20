import krpc
from time import sleep


def control(vessel):
    sleep(3)

    while True:
        resources = vessel.resources_in_decouple_stage(
            vessel.control.current_stage - 1, False
        )

        solid_fuel = resources.amount("SolidFuel")
        liquid_fuel = resources.amount("LiquidFuel")

        if solid_fuel == 0 and liquid_fuel == 0:
            vessel.control.activate_next_stage()
            print("Stage decoupled!")

        sleep(0.25)
