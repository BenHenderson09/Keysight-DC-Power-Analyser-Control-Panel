import sys
import pyvisa
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QGridLayout, QDoubleSpinBox, QMessageBox, QGroupBox, QSizePolicy
)
from PyQt6.QtGui import QColor, QPalette, QFont
from PyQt6.QtCore import QTimer, Qt


GPIB_ADDRESS = "GPIB0::5::INSTR"

CHANNEL_COLORS = {
    1: "#FFF59D",  # Yellow
    2: "#A5D6A7",  # Green
    3: "#90CAF9",  # Blue
    4: "#CE93D8",  # Purple
}


class ChannelControl(QGroupBox):
    def __init__(self, instrument, channel):
        super().__init__(f"Channel {channel}")
        self.instrument = instrument
        self.channel = channel

        # Background color
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(CHANNEL_COLORS[channel]))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        # Fonts
        label_font = QFont("Arial", 14)
        input_font = QFont("Arial", 16)
        output_font = QFont("Courier New", 18, QFont.Weight.Bold)

        # Voltage input
        self.voltage_label = QLabel("Voltage:")
        self.voltage_label.setFont(label_font)
        self.voltage_input = QDoubleSpinBox()
        self.voltage_input.setRange(0, 100)
        self.voltage_input.setDecimals(3)
        self.voltage_input.setSuffix(" V")
        self.voltage_input.setFont(input_font)
        self.voltage_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Current limit input
        self.current_label = QLabel("Current Limit:")
        self.current_label.setFont(label_font)
        self.current_input = QDoubleSpinBox()
        self.current_input.setRange(0, 10)
        self.current_input.setDecimals(3)
        self.current_input.setSuffix(" A")
        self.current_input.setFont(input_font)
        self.current_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Set button
        self.set_button = QPushButton("Set")
        self.set_button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.set_button.clicked.connect(self.apply_settings)
        self.set_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Output label for measurements
        self.output_label = QLabel("Measured:\n--- V\n--- A\n\nLimit:\n--- A")
        self.output_label.setFont(output_font)
        self.output_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.output_label.setStyleSheet("background-color: white; border: 1px solid gray;")
        self.output_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Layout setup
        layout = QVBoxLayout()

        # Voltage input layout
        volt_layout = QHBoxLayout()
        volt_layout.addWidget(self.voltage_label)
        volt_layout.addWidget(self.voltage_input)
        layout.addLayout(volt_layout)

        # Current input layout
        curr_layout = QHBoxLayout()
        curr_layout.addWidget(self.current_label)
        curr_layout.addWidget(self.current_input)
        layout.addLayout(curr_layout)

        # Set button centered
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.set_button)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Measurement display (big box)
        layout.addWidget(self.output_label)

        self.setLayout(layout)

        # Timer for continuous update
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_readings)
        self.timer.start(1000)  # update every second

    def apply_settings(self):
        try:
            voltage = self.voltage_input.value()
            current = self.current_input.value()

            self.instrument.write(f"VOLT {voltage}, (@{self.channel})")
            self.instrument.write(f"CURR {current}, (@{self.channel})")
            self.update_readings()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"CH{self.channel} set error: {e}")

    def update_readings(self):
        try:
            v = float(self.instrument.query(f"MEAS:VOLT? (@{self.channel})").strip())
            c = float(self.instrument.query(f"MEAS:CURR? (@{self.channel})").strip())
            limit = float(self.instrument.query(f"CURR? (@{self.channel})").strip())

            self.output_label.setText(
                f"Measured:\n{v:7.3f} V\n{c:7.3f} A\n\nLimit:\n{limit:7.3f} A"
            )
        except Exception as e:
            self.output_label.setText(f"Read error:\n{e}")


class PowerSupplyGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ben's PSU Control Panel")

        try:
            self.rm = pyvisa.ResourceManager()
            self.instrument = self.rm.open_resource(GPIB_ADDRESS)
            self.instrument.timeout = 5000
            self.instrument.read_termination = '\n'
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Could not connect to instrument:\n{e}")
            sys.exit(1)

        layout = QGridLayout()
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]

        for i, pos in enumerate(positions, start=1):
            control = ChannelControl(self.instrument, channel=i)
            layout.addWidget(control, *pos)

        # Make the layout scalable
        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 1)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)

        self.setLayout(layout)
        self.showMaximized()


    def closeEvent(self, event):
        try:
            self.instrument.close()
        except:
            pass
        event.accept()


def main():
    app = QApplication(sys.argv)
    gui = PowerSupplyGUI()
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
