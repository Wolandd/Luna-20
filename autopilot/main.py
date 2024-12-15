import krpc
import stageControl
import LEO
import flight_to_moon
import landing_on_moon
import back_to_home
import threading
from logger import RocketLogger

# подключаемся, выбираем цуп и ракету нашу
connection = krpc.connect("Connection")
space_center = connection.space_center
vessel = space_center.active_vessel

# в параллель запускаем контроль ступеней и логгер
thread = threading.Thread(target=stageControl.control, args=(vessel,))
thread.daemon = True
thread.start()
rocket_logger = RocketLogger(vessel, space_center)
rocket_logger.start_logging()

# и выходим на НОО
LEO.start(vessel, space_center, connection)
rocket_logger.switch()

# Гомановская траектория до Луны
flight_to_moon.start(vessel, space_center, connection)
rocket_logger.switch()

# посадка на Луну
landing_on_moon.start(vessel, space_center, connection)

# забор образца грунта
landing_on_moon.drilling(vessel, space_center, connection)
rocket_logger.switch()

# взлет с Луны
back_to_home.launchFromMoon(vessel)
rocket_logger.switch()

# корректировка орбиты, чтобы перицентр находился на уровне атмосферы
back_to_home.orbitCorrection(vessel, space_center, connection)

# торможение об орбиту
back_to_home.orbitDeceleration(vessel, space_center, connection)

# приземление
back_to_home.landing(vessel, connection)

connection.close()