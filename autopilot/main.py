import krpc
import time
import _thread as thread
import stageControl
import LEO

# подключаемся, выбираем цуп и ракету нашу
connection = krpc.connect("Connection")
space_center = connection.space_center
vessel = space_center.active_vessel

# в параллель запускаем контроль ступеней
thread.start_new_thread(stageControl.control, tuple([vessel]))

# и выходим на НЗО
LEO.start(vessel, space_center, connection)