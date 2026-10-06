"""
Стили для PyQt6 приложения - тёмная тема с cyan акцентами
"""

DARK_THEME = """
/* === Основные стили === */
QMainWindow, QWidget {
    background-color: #0a0f1c;
    color: #f1f5f9;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
}

/* === Sidebar === */
#sidebar {
    background-color: #111827;
    border-right: 1px solid #1e293b;
}

#logo {
    color: #06b6d4;
    font-size: 18px;
    font-weight: bold;
    padding: 20px;
    border-bottom: 1px solid #1e293b;
}

/* === Navigation Buttons === */
QPushButton#navButton {
    background-color: transparent;
    color: #94a3b8;
    border: none;
    border-radius: 8px;
    padding: 14px 16px;
    text-align: left;
    font-size: 14px;
}

QPushButton#navButton:hover {
    background-color: #243049;
    color: #f1f5f9;
}

QPushButton#navButton:checked {
    background-color: rgba(6, 182, 212, 0.2);
    color: #22d3ee;
    border: 1px solid rgba(6, 182, 212, 0.3);
}

/* === Cards === */
QFrame#card {
    background-color: #1a2234;
    border: 1px solid #1e293b;
    border-radius: 12px;
}

QFrame#card:hover {
    border-color: #334155;
}

/* === Labels === */
QLabel#title {
    font-size: 24px;
    font-weight: bold;
    color: #f1f5f9;
}

QLabel#subtitle {
    font-size: 14px;
    color: #94a3b8;
}

QLabel#cardTitle {
    font-size: 16px;
    font-weight: 600;
    color: #f1f5f9;
}

QLabel#cardDescription {
    font-size: 13px;
    color: #94a3b8;
}

QLabel#sectionTitle {
    font-size: 14px;
    font-weight: 600;
    color: #22d3ee;
    margin-bottom: 8px;
}

/* === Text Input === */
QTextEdit, QLineEdit {
    background-color: #0d1320;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 12px;
    color: #f1f5f9;
    font-size: 14px;
}

QTextEdit:focus, QLineEdit:focus {
    border-color: #06b6d4;
}

QTextEdit::placeholder, QLineEdit::placeholder {
    color: #64748b;
}

/* === Primary Button === */
QPushButton#primaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #06b6d4, stop:1 #22d3ee);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 14px 24px;
    font-size: 14px;
    font-weight: 500;
}

QPushButton#primaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0891b2, stop:1 #06b6d4);
}

QPushButton#primaryButton:disabled {
    background-color: #334155;
    color: #64748b;
}

/* === Secondary Button === */
QPushButton#secondaryButton {
    background-color: #243049;
    color: #94a3b8;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 12px 20px;
    font-size: 14px;
}

QPushButton#secondaryButton:hover {
    background-color: #334155;
    color: #f1f5f9;
}

/* === Upload Zone === */
QFrame#uploadZone {
    background-color: #0d1320;
    border: 2px dashed #334155;
    border-radius: 12px;
    min-height: 200px;
}

QFrame#uploadZone:hover {
    border-color: #06b6d4;
    background-color: rgba(6, 182, 212, 0.05);
}

/* === Results === */
QFrame#resultsCard {
    background-color: #1a2234;
    border: 1px solid #06b6d4;
    border-radius: 12px;
}

QFrame#resultBlock {
    background-color: #111827;
    border-left: 3px solid #06b6d4;
    border-radius: 8px;
    padding: 16px;
    margin: 8px 0;
}

/* === History === */
QFrame#historyItem {
    background-color: #111827;
    border: 1px solid #1e293b;
    border-radius: 8px;
    padding: 12px;
}

QFrame#historyItem:hover {
    border-color: #334155;
}

/* === ScrollArea === */
QScrollArea {
    background-color: transparent;
    border: none;
}

QScrollBar:vertical {
    background-color: #111827;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background-color: #334155;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #475569;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* === Progress/Loading === */
QProgressBar {
    background-color: #0d1320;
    border: none;
    border-radius: 4px;
    height: 8px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #06b6d4, stop:1 #22d3ee);
    border-radius: 4px;
}

/* === Tab Widget === */
QTabWidget::pane {
    border: none;
    background-color: transparent;
}

QTabBar::tab {
    background-color: transparent;
    color: #94a3b8;
    padding: 12px 20px;
    border: none;
    border-bottom: 2px solid transparent;
}

QTabBar::tab:selected {
    color: #22d3ee;
    border-bottom: 2px solid #06b6d4;
}

QTabBar::tab:hover:!selected {
    color: #f1f5f9;
}

/* === Status === */
QLabel#statusActive {
    color: #10b981;
}

QLabel#statusError {
    color: #ef4444;
}

/* === Tooltips === */
QToolTip {
    background-color: #1a2234;
    color: #f1f5f9;
    border: 1px solid #334155;
    border-radius: 4px;
    padding: 8px;
}
"""

