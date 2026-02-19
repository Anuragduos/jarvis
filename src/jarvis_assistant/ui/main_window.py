from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .orb_widget import OrbWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("JARVIS Hybrid Assistant")
        self.resize(980, 680)
        self.setStyleSheet(
            """
            QMainWindow, QWidget { background-color: #090D17; color: #D9E7FF; }
            QTextEdit { background-color: #0F1526; border: 1px solid #1F2B45; border-radius: 8px; }
            QPushButton { background-color: #1E2F50; border: 1px solid #274070; padding: 8px; border-radius: 8px; }
            QLabel#status { color: #9AB8FF; font-size: 14px; }
            """
        )
        self._build_ui()

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)

        main_layout = QHBoxLayout(root)
        center_layout = QVBoxLayout()
        side_layout = QVBoxLayout()

        self.orb = OrbWidget()
        self.status = QLabel("Status: Idle")
        self.status.setObjectName("status")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.console = QTextEdit()
        self.console.setPlaceholderText("Command console...\nType or inspect events.")
        self.console.setMinimumHeight(180)

        state_bar = QHBoxLayout()
        for state in ("idle", "listening", "thinking", "speaking"):
            btn = QPushButton(state.title())
            btn.clicked.connect(lambda _checked=False, s=state: self._set_state(s))
            state_bar.addWidget(btn)

        center_layout.addStretch(1)
        center_layout.addWidget(self.orb, alignment=Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(self.status)
        center_layout.addLayout(state_bar)
        center_layout.addWidget(self.console)

        side_layout.addWidget(QLabel("Settings"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["offline", "online", "hybrid"])
        side_layout.addWidget(QLabel("Mode"))
        side_layout.addWidget(self.mode_combo)

        self.personality = QSlider(Qt.Orientation.Horizontal)
        self.personality.setRange(0, 100)
        self.personality.setValue(50)
        side_layout.addWidget(QLabel("Personality"))
        side_layout.addWidget(self.personality)

        self.allow_automation = QCheckBox("Enable automation")
        self.allow_automation.setChecked(True)
        side_layout.addWidget(self.allow_automation)
        side_layout.addStretch(1)

        main_layout.addLayout(center_layout, 3)
        main_layout.addLayout(side_layout, 1)

    def _set_state(self, state: str) -> None:
        self.orb.set_state(state)
        self.status.setText(f"Status: {state.title()}")
