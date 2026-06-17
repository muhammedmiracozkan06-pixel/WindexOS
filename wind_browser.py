import sys
import os
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLineEdit, QPushButton, QMenu, QFileDialog, QMessageBox)
from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QAction, QIcon

class WindBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wind Browser v1.0")
        self.setGeometry(100, 100, 1200, 800)
        
        # Ana Pencere Düzeni
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Üst Araç Çubuğu (Toolbar)
        self.toolbar = QWidget()
        self.toolbar.setStyleSheet("background-color: #111115; padding: 5px; border-bottom: 1px solid #00ffcc;")
        self.toolbar_layout = QHBoxLayout(self.toolbar)
        self.toolbar_layout.setContentsMargins(5, 2, 5, 2)

        # 1. SOL TIK MENÜ BUTONU (Zırt Pırt Menü)
        self.menu_btn = QPushButton("☰ Wind")
        self.menu_btn.setStyleSheet("""
            QPushButton {
                background-color: #1c1c24; color: #00ffcc; font-weight: bold;
                border: 1px solid #00ffcc; border-radius: 4px; padding: 5px 12px;
            }
            QPushButton:hover { background-color: #00ffcc; color: #111115; }
        """)
        # Sol tıklandığında menüyü açması için bağladık
        self.menu_btn.clicked.connect(self.show_left_click_menu)
        self.toolbar_layout.addWidget(self.menu_btn)

        # Navigasyon Butonları
        self.back_btn = QPushButton("◀")
        self.back_btn.setStyleSheet("color: #ffffff; background: transparent; font-size: 14px; border: none;")
        self.toolbar_layout.addWidget(self.back_btn)

        self.forward_btn = QPushButton("▶")
        self.forward_btn.setStyleSheet("color: #ffffff; background: transparent; font-size: 14px; border: none;")
        self.toolbar_layout.addWidget(self.forward_btn)

        self.reload_btn = QPushButton("⟳")
        self.reload_btn.setStyleSheet("color: #ffffff; background: transparent; font-size: 16px; border: none;")
        self.toolbar_layout.addWidget(self.reload_btn)

        # URL / ARAMA ÇUBUĞU
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Web adresi yazın veya Google'da arayın...")
        self.url_bar.setStyleSheet("""
            QLineEdit {
                background-color: #1c1c24; color: #ffffff;
                border: 1px solid #333344; border-radius: 4px;
                padding: 6px; font-size: 13px; selection-background-color: #00ffcc;
            }
            QLineEdit:focus { border: 1px solid #00ffcc; }
        """)
        self.toolbar_layout.addWidget(self.url_bar)

        self.layout.addWidget(self.toolbar)

        # WEB MOTORU (WEBVIEW)
        self.browser = QWebEngineView()
        self.layout.addWidget(self.browser)

        # BUTON SİNYALLERİ
        self.back_btn.clicked.connect(self.browser.back)
        self.forward_btn.clicked.connect(self.browser.forward)
        self.reload_btn.clicked.connect(self.browser.reload)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.browser.urlChanged.connect(self.update_url_bar)

        # İNDİRME YÖNETİCİSİ ENTEGRASYONU
        self.browser.page().profile().downloadRequested.connect(self.handle_download)

        # Varsayılan olarak Google Ana Sayfası ile başla
        self.browser.setUrl(QUrl("https://www.google.com"))

    def navigate_to_url(self):
        """ URL çubuğuna yazılan metni işler: Linkse gider, değilse Google'da arar """
        text = self.url_bar.text().strip()
        
        if not text:
            return

        # Basit bir domain kontrolü (Nokta varsa ve boşluk yoksa URL kabul et)
        if "." in text and " " not in text:
            if not text.startswith("http://") and not text.startswith("https://"):
                text = "https://" + text
            self.browser.setUrl(QUrl(text))
        else:
            # Kelime ise direkt akıllı Google aramasına fırlat
            search_url = f"https://www.google.com/search?q={text}"
            self.browser.setUrl(QUrl(search_url))

    def update_url_bar(self, q):
        """ Sayfa değiştikçe URL çubuğunu günceller """
        self.url_bar.setText(q.toString())

    def show_left_click_menu(self):
        """ Sol tıklandığında açılan fütüristik Wind Menüsü """
        left_menu = QMenu(self)
        left_menu.setStyleSheet("""
            QMenu { background-color: #1c1c24; color: #ffffff; border: 1px solid #00ffcc; }
            QMenu::item { padding: 8px 25px; }
            QMenu::item:selected { background-color: #00ffcc; color: #111115; }
        """)

        home_action = QAction("🏠 Ana Sayfa (Google)", self)
        home_action.triggered.connect(lambda: self.browser.setUrl(QUrl("https://www.google.com")))
        left_menu.addAction(home_action)

        downloads_action = QAction("📥 İndirilenler Klasörü", self)
        downloads_action.triggered.connect(self.open_downloads_folder)
        left_menu.addAction(downloads_action)

        left_menu.addSeparator()

        about_action = QAction("ℹ Wind Browser Hakkında", self)
        about_action.triggered.connect(self.show_about)
        left_menu.addAction(about_action)

        exit_action = QAction("❌ Çıkış", self)
        exit_action.triggered.connect(self.close)
        left_menu.addAction(exit_action)

        # Menüyü tam butonun altına konumlandırıp patlatıyoruz
        left_menu.exec(self.menu_btn.mapToGlobal(self.menu_btn.rect().bottomLeft()))

    def handle_download(self, download_item: QWebEngineDownloadRequest):
        """ Dosya indirme tetiklendiğinde çalışan güvenli indirme sistemi """
        # Kullanıcıya dosyayı nereye kaydetmek istediğini sor
        suggested_path = download_item.suggestedFileName()
        home_downloads = os.path.expanduser("~/İndirilenler")
        if not os.path.exists(home_downloads):
            home_downloads = os.path.expanduser("~/Downloads")
            
        default_path = os.path.join(home_downloads, suggested_path)
        
        file_path, _ = QFileDialog.getSaveFileName(self, "Dosyayı Kaydet", default_path)
        
        if file_path:
            download_item.setDownloadDirectory(os.path.dirname(file_path))
            download_item.setDownloadFileName(os.path.basename(file_path))
            download_item.accept()
            QMessageBox.information(self, "İndirme Başladı", f"{suggested_path} indiriliyor...")

    def open_downloads_folder(self):
        """ Kullanıcının indirme dizinini dosya yöneticisinde açar """
        home_downloads = os.path.expanduser("~/İndirilenler")
        if not os.path.exists(home_downloads):
            home_downloads = os.path.expanduser("~/Downloads")
        os.system(f"xdg-open {home_downloads} &")

    def show_about(self):
        QMessageBox.about(self, "Wind Browser", "WindexOS Dağıtımı İçin Geliştirilmiş\nAşırı Hafif ve Güçlü Web Tarayıcı v1.0")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    browser = WindBrowser()
    browser.show()
    sys.exit(app.exec())
