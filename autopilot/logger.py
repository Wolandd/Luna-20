import logging
import os
import time
import threading

class RocketLogger:
    def __init__(self, vessel, space_center, log_filename_base="rocket_log"):
        self.vessel = vessel
        self.space_center = space_center
        self.log_filename_base = log_filename_base
        self.logger = None
        self.log_file_path = None
        self.logging_thread = None
        self.stop_event = threading.Event()
        self.initial_fuel_mass = None
        self.start_time = None
        self.create_new_log()

    def create_new_log(self):
        if self.logger:
            self.logger.info("Переключаюсь на новый лог-файл...")
            handlers = self.logger.handlers[:]
            for handler in handlers:
                self.logger.removeHandler(handler)
                handler.close()

        i = 1
        log_filename = f"{self.log_filename_base}_{i}.txt"
        while os.path.exists(log_filename):
            i += 1
            log_filename = f"{self.log_filename_base}_{i}.txt"
        self.log_file_path = log_filename
        self.logger = logging.getLogger(f"{self.log_filename_base}_{i}")
        self.logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(self.log_file_path)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(file_handler)
        self.initial_fuel_mass = self.get_rocket_data()[2]  # запоминаем начальную массу топлива для текущего лога
        self.start_time = time.time()
        self.logger.info(f"Начало логирования в файл: {self.log_file_path}")


    def start_logging(self):
        self.logging_thread = threading.Thread(target=self._log_data)
        self.logging_thread.daemon = True
        self.logging_thread.start()

    def _log_data(self):
        while not self.stop_event.is_set():
            speed, specific_impulse, current_fuel_mass = self.get_rocket_data()
            fuel_mass_spent = self.initial_fuel_mass - current_fuel_mass
            engine_runtime = time.time() - self.start_time
            log_message = f"Скорость: {speed:.2f} м/с, Удельный импульс: {specific_impulse:.2f} с, " \
                            f"Затрачено топлива: {fuel_mass_spent:.2f} кг, Время: {engine_runtime:.2f} сек"
            self.logger.info(log_message)
            time.sleep(10)

    def stop_logging(self):
        self.stop_event.set()
        if self.logging_thread:
            self.logging_thread.join()
            self.logger.info("Логирование остановлено.")

    def switch(self):
        self.create_new_log()

    def get_rocket_data(self):
        speed = self.vessel.orbit.speed
        specific_impulse = self.vessel.parts.engines[0].specific_impulse
        fuel_mass = self.vessel.mass - self.vessel.dry_mass
        return speed, specific_impulse, fuel_mass
