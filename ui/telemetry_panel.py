from PySide6.QtWidgets import QLabel, QGridLayout
from ui.card import Card

class TelemetryPanel(Card):
    def __init__(self):
        super().__init__()
        grid = QGridLayout(self)
        grid.setSpacing(14)

        self.fields = {}
        labels = ["LAT", "LON", "ALT", "BAT", "SATS", "SPEED"]

        for i, key in enumerate(labels):
            title = QLabel(key)
            value = QLabel("--")
            title.setStyleSheet("color:#6b7280; font-size:12px;")
            value.setStyleSheet("font-size:18px; font-weight:600;")

            grid.addWidget(title, i // 3 * 2, i % 3)
            grid.addWidget(value, i // 3 * 2 + 1, i % 3)

            self.fields[key.lower()] = value

    def update(self, data):
        for k, v in data.items():
            if k in self.fields:
                self.fields[k].setText(str(v))
