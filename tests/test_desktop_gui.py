"""Offscreen regressions; all API boundaries are local fakes."""
import os
import sys
import time
from pathlib import Path

os.environ['QT_QPA_PLATFORM'] = 'offscreen'
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'desktop'))
import pytest
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication, QLabel, QMessageBox
import main as gui


@pytest.fixture(scope='module')
def app():
    return QApplication.instance() or QApplication([])


def pump(app, seconds=.3):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        app.processEvents()
        time.sleep(.001)


@pytest.fixture
def window(app, monkeypatch):
    monkeypatch.setattr(gui.api_client, 'check_health', lambda: True)
    monkeypatch.setattr(gui.api_client, 'get_history', lambda: {'items': [], 'total': 0})
    monkeypatch.setattr(gui.api_client, 'clear_history', lambda: {'success': True})
    monkeypatch.setattr(gui.MainWindow, 'show_error', lambda self, message: setattr(self, 'last_error', message))
    w = gui.MainWindow()
    pump(app, .03)
    yield w
    pump(app)
    w.close()
    pump(app, .03)


@pytest.mark.parametrize('operation', ['load_history', 'clear_history', 'check_server_connection'])
def test_slow_api_keeps_event_loop_responsive(window, app, monkeypatch, operation):
    finished = []
    def slow():
        time.sleep(.15)
        finished.append(True)
        return True if operation == 'check_server_connection' else {'success': True, 'items': [], 'total': 0}
    monkeypatch.setattr(gui.api_client, {'load_history': 'get_history', 'clear_history': 'clear_history', 'check_server_connection': 'check_health'}[operation], slow)
    monkeypatch.setattr(QMessageBox, 'question', lambda *a: QMessageBox.StandardButton.Yes)
    ticks = []
    QTimer.singleShot(10, lambda: ticks.append(not finished))
    getattr(window, operation)()
    pump(app, .25)
    assert ticks == [True], 'GUI timer must fire while the HTTP call is still pending'


def test_history_error_preserves_visible_rows(window, app, monkeypatch):
    monkeypatch.setattr(gui.api_client, 'get_history', lambda: {'items': [{'request_summary': 'saved row'}], 'total': 1})
    window.load_history()
    pump(app, .05)
    monkeypatch.setattr(gui.api_client, 'get_history', lambda: {'success': False, 'error': 'offline'})
    window.load_history()
    pump(app, .05)
    assert 'offline' in window.last_error
    assert any('saved row' in label.text() for label in window.history_widget.findChildren(QLabel))


def test_untrusted_results_are_plain_text(window, app, monkeypatch):
    attack = '<img src="local.png">'
    window.show_results({'summary': attack, 'strengths': [attack]}, 'text')
    assert all(label.textFormat() == Qt.TextFormat.PlainText for label in window.results_scroll.findChildren(QLabel) if attack in label.text())
    window.show_results({'description': attack, 'visual_style_score': 5, 'visual_style_analysis': attack}, 'image')
    assert all(label.textFormat() == Qt.TextFormat.PlainText for label in window.results_scroll.findChildren(QLabel) if attack in label.text())
    monkeypatch.setattr(gui.api_client, 'get_history', lambda: {'items': [{'request_summary': attack, 'request_type': attack, 'timestamp': attack}], 'total': 1})
    window.load_history()
    pump(app, .05)
    assert all(label.textFormat() == Qt.TextFormat.PlainText for label in window.history_widget.findChildren(QLabel))


@pytest.mark.parametrize(('typed', 'expected'), [('n8n.io', 'https://n8n.io/'), ('https://n8n.io', 'https://n8n.io/'), ('make.com/', 'https://www.make.com/en'), ('www.make.com/en/', 'https://www.make.com/en'), ('albato.ru', 'https://albato.ru/')])
def test_parser_normalizes_approved_urls(window, app, monkeypatch, typed, expected):
    sent = []
    monkeypatch.setattr(gui.api_client, 'parse_demo', lambda url: sent.append(url) or {'success': False, 'error': 'fake'})
    window.url_input.setText(typed)
    window.parse_site()
    pump(app, .05)
    assert sent == [expected]


@pytest.mark.parametrize('typed', ['https://evil.test/', 'https://n8n.io/?redirect=evil', 'https://n8n.io/other', 'http://n8n.io/', 'https://user@n8n.io/', 'https://n8n.io:443/', 'https://n8n.io/#x'])
def test_parser_rejects_other_urls_before_api(window, app, monkeypatch, typed):
    sent = []
    monkeypatch.setattr(gui.api_client, 'parse_demo', lambda url: sent.append(url) or {'success': False})
    window.url_input.setText(typed)
    window.parse_site()
    pump(app, .03)
    assert sent == []
    assert window.last_error


def test_repeated_analysis_retains_active_worker(window, app, monkeypatch):
    def slow(text):
        time.sleep(.15)
        return {'success': False, 'error': 'fake'}
    monkeypatch.setattr(gui.api_client, 'analyze_text', slow)
    window.text_input.setPlainText('Long enough input for analysis')
    window.analyze_text()
    original = window.current_worker
    window.analyze_text()
    assert window.current_worker is original


def test_repeated_history_and_close_are_safe(window, app, monkeypatch):
    calls = []
    def slow():
        calls.append(True)
        time.sleep(.15)
        return {'items': [], 'total': 0}
    monkeypatch.setattr(gui.api_client, 'get_history', slow)
    window.show()
    window.load_history()
    window.load_history()
    assert not window.close(), 'Close must defer destruction while a thread is active'
    ticks = []
    QTimer.singleShot(10, lambda: ticks.append(True))
    pump(app, .3)
    assert calls == [True]
    assert ticks == [True]
    assert not window.isVisible()


@pytest.mark.parametrize('raised', [False, True])
def test_failed_clear_preserves_history(window, app, monkeypatch, raised):
    monkeypatch.setattr(gui.api_client, 'get_history', lambda: {'items': [{'request_summary': 'saved row'}], 'total': 1})
    window.load_history()
    pump(app, .05)
    def fail():
        if raised:
            raise RuntimeError('offline')
        return {'success': False, 'error': 'offline'}
    monkeypatch.setattr(gui.api_client, 'clear_history', fail)
    monkeypatch.setattr(QMessageBox, 'question', lambda *a: QMessageBox.StandardButton.Yes)
    window.clear_history()
    pump(app, .05)
    assert window.last_error == 'offline'
    assert any('saved row' in label.text() for label in window.history_widget.findChildren(QLabel))
    assert window.clear_history_btn.isEnabled()


def test_error_dialog_is_plain_text(app, monkeypatch):
    monkeypatch.setattr(gui.api_client, 'check_health', lambda: True)
    observed = []
    monkeypatch.setattr(QMessageBox, 'exec', lambda box: observed.append((box.text(), box.textFormat())))
    w = gui.MainWindow()
    try:
        w.show_error('<img src="local.png">')
        assert observed == [('<img src="local.png">', Qt.TextFormat.PlainText)]
    finally:
        pump(app, .05)
        w.close()
