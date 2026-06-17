import os
import sys
from tkinter import *

FLAG_FILE = "/Windex/System64/apps/.update_done"

# Güncelleme başarılı bayrağı yoksa bu ekran hiç açılmasın
if not os.path.exists(FLAG_FILE):
    sys.exit(0)

with open(FLAG_FILE, "r") as f:
    update_name = f.read().strip()

# 📂 MASAÜSTÜNDE GÜNCELLEME DİZİNİ VE DOSYASI OLUŞTURMA
# Not: WindexOS'te aktif kullanıcı adını bulup masaüstü yolunu yakalıyoruz
try:
    # Eğer windexos kullanıcısı ise direkt yolu hedefle, yoksa mevcut ev dizinine bak
    home_dir = os.path.expanduser("~")
    desktop_path = os.path.join(home_dir, "Masaüstü")
    
    # Eğer sistem dili İngilizce ise 'Desktop' klasörünü de kontrol et
    if not os.path.exists(desktop_path):
        desktop_path = os.path.join(home_dir, "Desktop")
        
    update_folder = os.path.join(desktop_path, "Güncellendi")
    
    # Klasörü oluştur
    os.makedirs(update_folder, exist_ok=True)
    
    # İçine bilgilendirme txt dosyası yaz
    changelog_path = os.path.join(update_folder, "Değişiklikler.txt")
    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write(f"=========================================\n")
        f.write(f"     WINDEXOS GÜNCELLEME RAPORU          \n")
        f.write(f"=========================================\n\n")
        f.write(f"Uygulanan Paket: {update_name}\n")
        f.write(f"Durum: Başarılı [✓]\n\n")
        f.write(f"Neler Değişti?:\n")
        f.write(f"- Çekirdek optimizasyonları (OptiHub entegrasyonu) güncellendi.\n")
        f.write(f"- Güvenlik yamaları ve APT sistem bağımlılıkları onarıldı.\n")
        f.write(f"- Sistem kararlılığı artırıldı.\n\n")
        f.write(f"WindexOS'i tercih ettiğiniz için teşekkür ederiz.\n")
        
    # Dosya izinlerini normal kullanıcı okuyabilsin diye serbest bırak
    os.chmod(update_folder, 0o777)
    os.chmod(changelog_path, 0o666)
except Exception as e:
    # Masaüstü klasörü oluşturulurken hata çıkarsa arka planda logla ama sistemi çökertme
    with open("/var/log/windex_update.log", "a") as log_f:
        log_f.write(f"[WelcomeError] Masaüstü klasörü oluşturulamadı: {str(e)}\n")

# 🖥️ GRAFİKSEL KARŞILAMA EKRANI (TKINTER)
root = Tk()
root.title("WindexOS // Güncelleme Başarılı")
root.attributes("-fullscreen", True)
root.configure(bg="#0a0a0c")

# Başlık (Güncelleme Adı)
title_label = Label(root, text=update_name.upper(), font=("Helvetica", 28, "bold"), fg="#00ffcc", bg="#0a0a0c")
title_label.pack(expand=True, pady=(150, 0))

# Değişiklik Uygulandı Alt Metni
info_label = Label(root, text="Sisteminiz güncelendi ve değişiklikler uygulandı.\nMasaüstünüze 'Güncellendi' rapor dizini bırakıldı.", font=("Helvetica", 16), fg="#ffffff", bg="#0a0a0c")
info_label.pack(expand=True, pady=(0, 50))

def close_welcome():
    # Bayrağı kaldır ki bir sonraki bootta bir daha açılmasın
    try:
        os.remove(FLAG_FILE)
    except:
        pass
    root.destroy()
    sys.exit(0)

# Tamam Butonu
btn_ok = Button(root, text="TAMAM", font=("Helvetica", 14, "bold"), bg="#1c1c24", fg="#00ffcc", activebackground="#00ffcc", activeforeground="#0a0a0c", bd=2, relief=SOLID, width=20, height=2, command=close_welcome)
btn_ok.pack(expand=True, pady=(0, 150))

root.mainloop()
