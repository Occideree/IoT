import json
import time
import random
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QRadioButton, QWidget, QSlider, QSpinBox
from mqtt_part import MQTTClient  # Убедитесь, что этот файл доступен и содержит корректную логику
from utils import resource_path
class IoTDeviceSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Устройство полива")
        self.setGeometry(100, 100, 400, 550)

        # Основные переменные
        self.soil_moisture = 50.0  # Уровень влажности почвы (в %)
        self.pump_state = False  # Состояние насоса
        self.mode = "Manual"  # Режим работы ("Manual" или "Automatic")
        self.update_interval = 10000  # Интервал обновления датчиков (мс)
        self.last_update_time = time.time()  # Последнее обновление времени
        self.moisture_trend = -0.2  # Тренд изменения влажности

        # Настройка MQTT
        self.mqtt_client = MQTTClient(
            server="test.mosquitto.org",
            port=1883,
            topic_sensors="iot/sprinkler/sensors",
            topic_commands="iot/sprinkler/commands",
            message_handler=self.handle_MQTT_message
        )
        self.mqtt_client.connect()

        # Таймер для обновления датчиков
        self.sensor_timer = QTimer()
        self.sensor_timer.timeout.connect(self.update_sensors)
        self.sensor_timer.start(100)

        # Таймер для работы насоса
        self.pump_timer = QTimer()


        # Графический интерфейс
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Метка состояния влажности
        self.moisture_label = QLabel(f"Влажность почвы: {self.soil_moisture:.1f}%")
        layout.addWidget(self.moisture_label, alignment=Qt.AlignCenter)

        # Слайдер для ручного управления влажностью
        self.moisture_slider = QSlider(Qt.Horizontal)
        self.moisture_slider.setMinimum(0)
        self.moisture_slider.setMaximum(1000)
        self.moisture_slider.setValue(int(self.soil_moisture * 10))
        self.moisture_slider.valueChanged.connect(self.manual_adjust_moisture)
        layout.addWidget(self.moisture_slider)

        # Кнопка включения/выключения насоса
        self.pump_button = QPushButton("Включить полив")
        self.pump_button.clicked.connect(self.toggle_pump)
        layout.addWidget(self.pump_button, alignment=Qt.AlignCenter)

        # Иконка насоса
        self.pump_icon_label = QLabel()
        self.update_pump_icon()
        layout.addWidget(self.pump_icon_label, alignment=Qt.AlignCenter)

        # Переключатели режимов
        self.manual_mode_button = QRadioButton("Ручной режим")
        self.manual_mode_button.setChecked(True)
        self.manual_mode_button.toggled.connect(self.set_manual_mode)
        layout.addWidget(self.manual_mode_button)

        self.auto_mode_button = QRadioButton("Автоматический режим")
        self.auto_mode_button.toggled.connect(self.set_auto_mode)
        layout.addWidget(self.auto_mode_button)

        # Настройка интервала обновления
        self.interval_label = QLabel("Время передачи данных(мс):")
        layout.addWidget(self.interval_label, alignment=Qt.AlignCenter)

        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setMinimum(500)
        self.interval_spinbox.setMaximum(10000)
        self.interval_spinbox.setValue(self.update_interval)
        self.interval_spinbox.valueChanged.connect(self.set_update_interval)
        layout.addWidget(self.interval_spinbox, alignment=Qt.AlignCenter)

        # Центральный виджет
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def update_sensors(self):
        """Обновляет состояние датчиков."""
        current_time = time.time()
        elapsed_time = (current_time - self.last_update_time) * 1000  # Время с последнего обновления в мс

        if elapsed_time >= self.update_interval:
            if self.pump_state:
                # Когда насос включен, увеличиваем влажность
                moisture_increase = (self.update_interval / 1000) * 2  # Дельта увеличения влажности
                self.soil_moisture += moisture_increase
                self.soil_moisture = min(self.soil_moisture, 100)  # Ограничиваем максимум 100%
            else:
                # Когда насос выключен, уменьшаем влажность
                self.soil_moisture += self.moisture_trend * (elapsed_time / 1000) + random.uniform(-0.05, 0.05)
                self.soil_moisture = max(0, min(self.soil_moisture, 100))  # Ограничиваем диапазон 0-100

            self.last_update_time = current_time

            # Обновляем отображение влажности и слайдер
            self.moisture_label.setText(f"Влажность почвы: {self.soil_moisture:.1f}%")
            self.moisture_slider.setValue(int(self.soil_moisture * 10))

            if self.mode == "Automatic" and not self.pump_state and self.soil_moisture < 30:
                self.start_pump()

            # Публикуем данные в MQTT
            sensor_data = {
                "soil_moisture": self.soil_moisture,
                "pump_state": self.pump_state,
                "mode": self.mode
            }
            self.mqtt_client.publish(self.mqtt_client.topic_sensors, sensor_data)

    def toggle_pump(self):
        """Включает/выключает насос вручную."""
        if self.mode == "Manual":
            if not self.pump_state:
                print(1)
                self.start_pump()
            else:
                self.stop_pump()

    def manual_adjust_moisture(self):
        """Регулирует влажность с помощью слайдера."""
        self.soil_moisture = self.moisture_slider.value() / 10
        self.moisture_label.setText(f"Влажность почвы: {self.soil_moisture:.1f}%")

    def set_manual_mode(self, command=""):
        """Устанавливает ручной режим."""
        if self.manual_mode_button.isChecked():
            self.mode = "Manual"
            self.stop_pump()
        if command == "Manual":
            self.mode = "Manual"
            self.stop_pump()
            self.manual_mode_button.setChecked(True)

    def set_auto_mode(self, command = ""):
        """Устанавливает автоматический режим."""
        if self.auto_mode_button.isChecked():
            self.mode = "Automatic"
        if command == "Automatic":
            self.auto_mode_button.setChecked(True)
            self.mode = "Automatic"

    def start_pump(self):
        """Запускает насос."""
        if not self.pump_state:
            self.pump_state = True
            self.update_pump_icon()
            self.pump_button.setText("Выключить полив")
            self.pump_timer.start(self.update_interval)
            print(2)


    def stop_pump(self):
        """Останавливает насос."""
        if self.pump_state:
            self.pump_state = False
            self.update_pump_icon()
            self.pump_button.setText("Включить полив")
            self.pump_timer.stop()



    def set_update_interval(self):
        """Устанавливает интервал обновления данных."""
        self.update_interval = self.interval_spinbox.value()
        self.sensor_timer.setInterval(self.update_interval)
        if self.pump_state:
            self.pump_timer.setInterval(self.update_interval)

    def update_pump_icon(self):
        """Обновляет иконку насоса."""
        if self.pump_state:
            pixmap = QPixmap(resource_path("images/drop.png"))  # Капелька
        else:
            pixmap = QPixmap(resource_path("images/drop_crossed.png")) # Перечёркнутая капелька
        self.pump_icon_label.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio))

    def handle_MQTT_message(self, command):
        """Обрабатывает команды, полученные через MQTT."""

        if command == "\"Manual\"":
            self.set_manual_mode(command="Manual")
        elif command == "\"Automatic\"":
            self.set_auto_mode(command="Automatic")
        elif command == "\"StartPump\"" :
            if self.mode=="Automatic":
                self.mqtt_client.publish("iot/sprinkler/commands", "The command cannot be executed, the watering mode is set to auto")
                return
            self.toggle_pump()
        elif command == "\"StopPump\"":
            if self.mode=="Automatic":
                self.mqtt_client.publish("iot/sprinkler/commands", "The command cannot be executed, the watering mode is set to auto")
                return
            self.toggle_pump()

if __name__ == "__main__":
    app = QApplication([])

    simulator = IoTDeviceSimulator()
    simulator.show()
    app.exec_()
