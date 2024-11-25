import krpc
import time
import _thread as thread
import stageControl
import LEO

connection = krpc.connect("Connection")
space_center = connection.space_center
vessel = space_center.active_vessel

thread.start_new_thread(stageControl.control, tuple([vessel]))

LEO.start(vessel, space_center, connection, 0.5)