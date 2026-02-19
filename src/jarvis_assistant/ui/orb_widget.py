from __future__ import annotations

from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QPointF, QRectF, Qt, pyqtProperty
from PyQt6.QtGui import QColor, QPainter, QRadialGradient
from PyQt6.QtWidgets import QWidget


class OrbWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._radius = 70.0
        self.state = "idle"
        self.animation = QPropertyAnimation(self, b"radius")
        self.animation.setDuration(600)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.setMinimumSize(280, 280)

    def get_radius(self) -> float:
        return self._radius

    def set_radius(self, value: float) -> None:
        self._radius = value
        self.update()

    radius = pyqtProperty(float, get_radius, set_radius)

    def set_state(self, state: str) -> None:
        self.state = state
        targets = {
            "idle": 70.0,
            "listening": 88.0,
            "thinking": 102.0,
            "speaking": 118.0,
        }
        self.animation.stop()
        self.animation.setStartValue(self._radius)
        self.animation.setEndValue(targets.get(state, 70.0))
        self.animation.start()

    def paintEvent(self, event) -> None:  # noqa: N802
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        center = QPointF(self.width() / 2, self.height() / 2)

        base_color = {
            "idle": QColor("#3A7BFF"),
            "listening": QColor("#00D4FF"),
            "thinking": QColor("#7B61FF"),
            "speaking": QColor("#00FFA3"),
        }.get(self.state, QColor("#3A7BFF"))

        gradient = QRadialGradient(center, self._radius)
        gradient.setColorAt(0.0, QColor(255, 255, 255, 220))
        gradient.setColorAt(0.4, base_color)
        gradient.setColorAt(1.0, QColor(10, 16, 28, 40))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawEllipse(QRectF(center.x() - self._radius, center.y() - self._radius, self._radius * 2, self._radius * 2))
