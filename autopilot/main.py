import krpc
from time import sleep
import _thread as thread
import stageControl
import LEO
import flight_to_moon
import landing_on_moon

# подключаемся, выбираем цуп и ракету нашу
connection = krpc.connect("Connection")
space_center = connection.space_center
vessel = space_center.active_vessel

# в параллель запускаем контроль ступеней
thread.start_new_thread(stageControl.control, tuple([vessel]))

# и выходим на НОО
LEO.start(vessel, space_center, connection)

sleep(10)

# Гомановская траектория до Луны
flight_to_moon.start(vessel, space_center, connection)

sleep(10)

# посадка на Луну
landing_on_moon.start(vessel, space_center, connection)
