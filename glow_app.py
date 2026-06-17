import sys
import os
import json
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
from PyQt5.QtWidgets import QApplication, QWidget, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QPen

def load_config():
    path = "/Windex/System64/personalization-service/config.json"
    try:
        with open(path, "r") as f: return json.load(f)
    except:
        return {"enabled": True, "glow_color": "#00ffcc", "glow_border_thickness": 6, "glow_duration_ms": 3000}

# DBus üzerinden Sadece Sistem Bildirimlerini İzleyen Akıllı İşçi
class NotificationWatcher(QThread):
    trigger_glow = pyqtSignal()

    def run(self):
        DBusGMainLoop(set_as_default=True)
        bus = dbus.SessionBus()
        
        # Linux Bildirim Sistemine bağlan
        bus.add_signal_receiver(
            self.notification_handler,
            signal_name="Notify",
            dbus_interface="org.freedesktop.Notifications"
        )
        
        loop = GLib.MainLoop()
        loop.run()

    def notification_handler(self, *args, **kwargs):
        # Bir bildirim tetiklendiği an sinyali UI tarafına gönder
        config = load_config()
        if config.get("enabled", True):
            self.trigger_glow.emit()

class EdgeGlowWidget(QWidget):
    def __init__(self):
        super().__init__()
        # X11Bypass ve WindowStaysOnTop sayesinde ışık her şeyin (paneller dahil) en üstünde görünür
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow | Qt.X11BypassWindowManagerHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Ekranın tamamını kapla
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(0, 0, screen.width(), screen.height())
        
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0)
        
        # Bildirim dinleyiciyi başlat
        self.watcher = NotificationWatcher()
        self.watcher.trigger_glow.connect(self.start_glow)
        self.watcher.start()

    def paintEvent(self, event):
        config = load_config()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Kenarlık kalınlığı ve rengi ayarı
        pen = QPen(QColor(config["glow_color"]), config["glow_border_thickness"])
        painter.setPen(pen)
        
        # Ekranın en dış çerçevesine tam oturan çizim
        painter.drawRect(0, 0, self.width(), self.height())

    def start_glow(self):
        config = load_config()
        if not config.get("enabled", True): return
        
        self.show()
        self.raise_() # En üste fırla
        
        # Pürüzsüz parlama animasyonu
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(300)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.start()
        
        QTimer.singleShot(config["glow_duration_ms"] - 400, self.stop_glow)

    def stop_glow(self):
        self.anim_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim_out.setDuration(400)
        self.anim_out.setStartValue(1.0)
        self.anim_out.setEndValue(0.0)
        self.anim_out.finished.connect(self.hide)
        self.anim_out.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    glow = EdgeGlowWidget()
    sys.exit(app.exec_())
