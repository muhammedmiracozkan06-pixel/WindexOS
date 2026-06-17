import sys
import json
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QColorDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

CONFIG_PATH = "/Windex/System64/personalization-service/config.json"

class PersonalizationUI(QWidget):
    def __init__(self):
        super().__init__()
        # Kod başlar başlamaz mevcut ayarları bir kez hafızaya tam alalım
        self.config = self.load_config()
        self.initUI()

    def load_config(self):
        default_config = {"enabled": True, "glow_color": "#00ffcc", "glow_border_thickness": 6, "glow_duration_ms": 3000}
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r") as f:
                    data = json.load(f)
                    # Eksik anahtar varsa varsayılanla doldur
                    for k, v in default_config.items():
                        if k not in data:
                            data[k] = v
                    return data
            except:
                return default_config
        return default_config

    def save_config(self):
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.config, f, indent=4)
        # Her kayıtta dosyaya tam yetki verelim ki diğer kullanıcılar da takılmasın
        os.system(f"chmod 777 {CONFIG_PATH} 2>/dev/null")

    def initUI(self):
        self.setWindowTitle("WindexOS Kişiselleştirme Servisi")
        self.setFixedSize(400, 250)
        self.setStyleSheet("background-color: #f8f9fa; border-radius: 10px;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(25, 25, 25, 25)
        
        title = QLabel("Edge Glow Ayarları")
        title.setFont(QFont("Ubuntu", 16, QFont.Bold))
        title.setStyleSheet("color: #212529;")
        layout.addWidget(title)
        
        # Durum Değiştirme (Aç / Kapat)
        status_layout = QHBoxLayout()
        self.status_label = QLabel()
        self.status_label.setFont(QFont("Ubuntu", 11))
        
        self.btn_toggle = QPushButton("Aç / Kapat")
        self.btn_toggle.setStyleSheet("background-color: #0d6efd; color: white; padding: 6px; border-radius: 5px; font-weight: bold;")
        self.btn_toggle.clicked.connect(self.toggle_service)
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.btn_toggle)
        layout.addLayout(status_layout)
        
        # Renk Seçimi
        color_layout = QHBoxLayout()
        color_title = QLabel("Çerçeve Rengi:")
        color_title.setFont(QFont("Ubuntu", 11))
        
        self.btn_color = QPushButton("Renk Seç")
        self.btn_color.clicked.connect(self.pick_color)
        
        color_layout.addWidget(color_title)
        color_layout.addWidget(self.btn_color)
        layout.addLayout(color_layout)
        
        # Arayüz ilk açıldığında butonların durumunu DOSYADAKİ verilere göre eşitle!
        self.update_ui_elements()
        
        self.setLayout(layout)

    def update_ui_elements(self):
        # Hafızadaki duruma göre yazıyı güncelle
        status_text = "AKTİF" if self.config["enabled"] else "KAPALI"
        self.status_label.setText(f"Özellik Durumu: {status_text}")
        
        # Hafızadaki renge göre butonun arka plan rengini sabitle
        current_color = self.config["glow_color"]
        self.btn_color.setStyleSheet(f"background-color: {current_color}; color: black; padding: 6px; border-radius: 5px; font-weight: bold; border: 1px solid #cccccc;")

    def toggle_service(self):
        # Durumu tersine çevir, hafızaya yaz ve kaydet
        self.config["enabled"] = not self.config["enabled"]
        self.save_config()
        self.update_ui_elements()

    def pick_color(self):
        # Renk paletini açarken mevcut rengi varsayılan olarak göster
        from PyQt5.QtGui import QColor
        initial_color = QColor(self.config["glow_color"])
        
        color = QColorDialog.getColor(initial_color, self, "Bir Ekran Çerçeve Rengi Seçin")
        if color.isValid():
            self.config["glow_color"] = color.name()
            self.save_config()
            self.update_ui_elements()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = PersonalizationUI()
    ui.show()
    sys.exit(app.exec_())
