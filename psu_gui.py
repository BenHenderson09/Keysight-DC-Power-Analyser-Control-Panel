import sys
import pyvisa
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QGridLayout, QDoubleSpinBox, QMessageBox, QGroupBox
)
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import QTimer


GPIB_ADDRESS = "GPIB0::5::INSTR"

# Channel-specific background colors
CHANNEL_COLORS = {
    1: "#FFF59D",  # Yellow
    2: "#A5D6A7",  # Green
    3: "#90CAF9",  # Blue
    4: "#CE93D8",  # Purple
}


class ChannelControl(QGroupBox):
    """Control block for one channel."""

    def __init__(self, instrument, channel):
        super().__init__(f"Channel {channel}")
        self.instrument = instrument
        self.channel = channel

        # Background color
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(CHANNEL_COLORS[channel]))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        # Input controls
        self.voltage_input = QDoubleSpinBox()
        self.voltage_input.setRange(0, 100)
        self.voltage_input.setDecimals(3)
        self.voltage_input.setSuffix(" V")

        self.current_input = QDoubleSpinBox()
        self.current_input.setRange(0, 10)
        self.current_input.setDecimals(3)
        self.current_input.setSuffix(" A")

        self.set_button = QPushButton("Set")
        self.set_button.clicked.connect(self.apply_settings)

        self.output_label = QLabel("Measured: --- V, --- A\nLimit: --- A")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Voltage:"))
        layout.addWidget(self.voltage_input)
        layout.addWidget(QLabel("Current Limit:"))
        layout.addWidget(self.current_input)
        layout.addWidget(self.set_button)
        layout.addWidget(self.output_label)
        self.setLayout(layout)

        # Timer for continuous readings
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_readings)
        self.timer.start(1000)  # Update every second

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
                f"Measured: {v:.3f} V, {c:.3f} A\nLimit: {limit:.3f} A"
            )
        except Exception as e:
            self.output_label.setText(f"Read error: {e}")


class PowerSupplyGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Keysight Power Supply - 4 Channel Monitor")

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

        self.setLayout(layout)

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
