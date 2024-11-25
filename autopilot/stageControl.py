import krpc
from time import sleep


def control(vessel):
    sleep(3)

    while True:
        # подгружаем инфу о ресурсах
        resources = vessel.resources_in_decouple_stage(
            vessel.control.current_stage - 1, False
        ) 

        solid_fuel = resources.amount("SolidFuel") # ТТ
        liquid_fuel = resources.amount("LiquidFuel") # ЖТ

        # если вдруг топливо кончается, то переходим к следующей ступени
        if solid_fuel == 0 and liquid_fuel == 0:
            print("Переход на следующую ступень")
            vessel.control.activate_next_stage()

        sleep(0.25)
