import krpc
from time import sleep
import _thread as thread
import stageControl
import LEO
import flight_to_moon
import landing_on_moon
import back_to_home

# подключаемся, выбираем цуп и ракету нашу
connection = krpc.connect("Connection")
space_center = connection.space_center
vessel = space_center.active_vessel

# в параллель запускаем контроль ступеней
thread.start_new_thread(stageControl.control, tuple([vessel]))

# и выходим на НОО
LEO.start(vessel, space_center, connection)

# Гомановская траектория до Луны
flight_to_moon.start(vessel, space_center, connection)

# посадка на Луну
landing_on_moon.start(vessel, space_center, connection)

# забор образца грунта
landing_on_moon.drilling(vessel, space_center, connection)

# взлет с Луны
back_to_home.launchFromMoon(vessel)

# корректировка орбиты, чтобы перицентр находился на уровне атмосферы
back_to_home.orbitCorrection(vessel, space_center, connection)

# торможение об орбиту
back_to_home.orbitDeceleration(vessel, space_center, connection)

# приземление
back_to_home.landing(vessel, connection)