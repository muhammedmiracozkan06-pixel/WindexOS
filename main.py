import sys
import os
import json
import locale
import time
import psutil
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QHBoxLayout, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QThread, pyqtSignal
from PyQt5.QtGui import QFont

class ProcessWatcher(QThread):
    app_detected = pyqtSignal(str)

    def run(self):
        # Sadece yakalamak istediğimiz gerçek masaüstü uygulamaları
        app_map = {
            "gnome-terminal-server": "Terminal",
            "konsole": "Terminal",
            "x-terminal-emulator": "Terminal",
            "firefox": "Firefox",
            "chromium": "Chromium",
            "google-chrome": "Google Chrome",
            "nemo": "Dosya Yöneticisi",
            "vlc": "VLC Medya Oynatıcı",
            "cheese": "Kamera",
            "kamera": "Kamera",
            "sublime_text": "Sublime Text",
            "code": "VS Code"
        }
        
        # Kesinlikle engellenecek sistem kelimeleri
        blacklisted_keywords = [
            "kworker", "systemd", "migration", "ksoftirqd", "rcu_preempt", 
            "python", "agent", "daemon", "dbus", "xorg", "wayland", 
            "at-spi", "gvfs", "menu", "panel", "desktop", "mint"
        ]
        
        already_running = set()
        for proc in psutil.process_iter(['name']):
            try:
                already_running.add(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        while True:
            time.sleep(0.4) # İşlemciyi yormamak için ideal bekleme süresi
            current_processes = set()
            
            for proc in psutil.process_iter(['name']):
                try:
                    pname = proc.info['name']
                    if not pname:
                        continue
                    current_processes.add(pname)
                    
                    if pname not in already_running:
                        # Kara listede olan bir kelime içeriyorsa direkt pas geç
                        if any(kw in pname.lower() for kw in blacklisted_keywords):
                            continue
                            
                        if pname in app_map:
                            self.app_detected.emit(app_map[pname])
                        else:
                            clean_name = pname.split('.')[0].replace('-', ' ').replace('_', ' ').title()
                            # İsmi çok kısa veya sadece sayı/sembol olan sistem süreçlerini de ele
                            if len(clean_name) > 3 and not clean_name.isdigit():
                                self.app_detected.emit(clean_name)
                        
                        already_running.add(pname)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            already_running = already_running.intersection(current_processes)

class DynamicIsland(QWidget):
    def __init__(self):
        super().__init__()
        try:
            self.system_lang = locale.getlocale()[0][:2] if locale.getlocale()[0] else "en"
        except:
            self.system_lang = "en"
            
        self.initUI()
        
        self.watcher = ProcessWatcher()
        self.watcher.app_detected.connect(self.trigger_island)
        self.watcher.start()
        
    def get_localized_text(self, app_name):
        base_path = "/Windex/System64/dynamic-island/locales"
        lang_file = f"{base_path}/{self.system_lang}.json"
        
        if not os.path.exists(lang_file):
            lang_file = f"{base_path}/en.json"
            
        with open(lang_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        if self.system_lang == "tr":
            return f"{app_name} {data['opening']}"
        else:
            return f"{data['opening']} {app_name}..."

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow | Qt.X11BypassWindowManagerHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        screen = QApplication.primaryScreen().geometry()
        self.screen_width = screen.width()
        
        # Tam o istediğin şık yatay dikdörtgen boyutları
        self.start_width = 180
        self.expanded_width = 380
        self.height_size = 45
        
        self.setGeometry((self.screen_width - self.start_width) // 2, -60, self.start_width, self.height_size)
        
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(15, 0, 15, 0)
        
        self.label = QLabel("", self)
        self.label.setStyleSheet("color: #111111; font-size: 13px; font-weight: bold;")
        self.label.setFont(QFont("Ubuntu", 10))
        self.label.setAlignment(Qt.AlignCenter)
        
        self.opacity_effect = QGraphicsOpacityEffect()
        self.label.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0)
        
        layout.addWidget(self.label)
        self.setLayout(layout)
        
        # BEYAZ VE KÖŞELERİ HAFİF YUVARLATILMIŞ DİKTÖRTGEN
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border: 2px solid #dddddd;
                border-radius: 8px;
            }
        """)
        
        self.is_animating = False

    def trigger_island(self, app_name):
        if self.is_animating:
            return
        self.is_animating = True
        
        display_text = self.get_localized_text(app_name)
        self.label.setText(display_text)
        self.show()
        
        self.geo_anim = QPropertyAnimation(self, b"geometry")
        self.geo_anim.setDuration(300)
        self.geo_anim.setStartValue(QRect((self.screen_width - self.start_width) // 2, -60, self.start_width, self.height_size))
        self.geo_anim.setEndValue(QRect((self.screen_width - self.expanded_width) // 2, 8, self.expanded_width, self.height_size))
        
        self.fade_in_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_anim.setDuration(200)
        self.fade_in_anim.setStartValue(0.0)
        self.fade_in_anim.setEndValue(1.0)
        
        self.geo_anim.start()
        QTimer.singleShot(250, self.fade_in_anim.start)
        QTimer.singleShot(3000, self.shrink_island)

    def shrink_island(self):
        self.fade_out_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out_anim.setDuration(150)
        self.fade_out_anim.setStartValue(1.0)
        self.fade_out_anim.setEndValue(0.0)
        
        self.exit_anim = QPropertyAnimation(self, b"geometry")
        self.exit_anim.setDuration(250)
        self.exit_anim.setStartValue(QRect((self.screen_width - self.expanded_width) // 2, 8, self.expanded_width, self.height_size))
        self.exit_anim.setEndValue(QRect((self.screen_width - self.start_width) // 2, -60, self.start_width, self.height_size))
        
        self.fade_out_anim.start()
        QTimer.singleShot(150, self.exit_anim.start)
        self.exit_anim.finished.connect(self.on_close)

    def on_close(self):
        self.hide()
        self.is_animating = False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    island = DynamicIsland()
    sys.exit(app.exec_())
