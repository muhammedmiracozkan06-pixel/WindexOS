import os
import sys
import requests
import subprocess
import threading
from tkinter import *
from tkinter import ttk, messagebox

VERSION_FILE = "/Windex/System64/apps/version.txt"
REPO_URL = "https://raw.githubusercontent.com/muhammedmiracozkan06-pixel/WindexUpdate/main"
DOWNLOAD_DIR = "/tmp/windex_update"
FLAG_FILE = "/Windex/System64/apps/.update_done"

if os.geteuid() != 0:
    print("[-] Hata: Güncelleme yöneticisi root yetkisi gerektirir!")
    sys.exit(1)

def get_current_version():
    """ Yereldeki sürüm dosyasını okur, dosya yoksa 1.0.0 olarak oluşturur """
    if not os.path.exists(VERSION_FILE):
        os.makedirs(os.path.dirname(VERSION_FILE), exist_ok=True)
        with open(VERSION_FILE, "w") as f:
            f.write("1.0.0")
        return "1.0.0"
    with open(VERSION_FILE, "r") as f:
        return f.read().strip()

def save_new_version(version_str):
    """ Güncelleme bitince yeni sürümü dosyaya kaydeder """
    with open(VERSION_FILE, "w") as f:
        f.write(version_str.strip())

def parse_version(v_str):
    try: 
        return [int(x) for x in v_str.strip().replace("\n", "").split('.')]
    except: 
        return [0,0,0]

class UpdateProgressWindow:
    def __init__(self, target_version):
        self.target_version = target_version
        self.root = Tk()
        self.root.title("WindexOS System Update")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="#000000")
        self.root.config(cursor="none")

        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        self.icon_path = os.path.join(DOWNLOAD_DIR, "icon.png")
        
        try:
            r = requests.get(f"{REPO_URL}/icon.png", timeout=5)
            with open(self.icon_path, "wb") as f: 
                f.write(r.content)
            self.img = PhotoImage(file=self.icon_path)
            self.img_label = Label(self.root, image=self.img, bg="#000000")
            self.img_label.pack(expand=True, pady=(100, 0))
        except:
            self.img_label = Label(self.root, text="WINDEX OS", font=("Helvetica", 36, "bold"), fg="#00ffcc", bg="#000000")
            self.img_label.pack(expand=True, pady=(200, 0))

        self.status_label = Label(self.root, text="Güncelleme hazırlanıyor... %0", font=("Helvetica", 16), fg="#ffffff", bg="#000000")
        self.status_label.pack(expand=True, pady=(0, 20))

        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure("Windex.Horizontal.TProgressbar", background="#00ffcc", troughcolor="#111115", thickness=8, borderwidth=0)
        
        self.progress = ttk.Progressbar(self.root, style="Windex.Horizontal.TProgressbar", orient=HORIZONTAL, length=450, mode='determinate')
        self.progress.pack(expand=True, pady=(0, 200))

        threading.Thread(target=self.run_update_process).start()
        self.root.mainloop()

    def update_ui(self, text, val):
        self.status_label.config(text=text)
        self.progress['value'] = val
        self.root.update()

    def run_update_process(self):
        try:
            self.update_ui("Güncelleme paketleri GitHub üzerinden çekiliyor... %15", 15)
            deb_url = f"{REPO_URL}/update.deb"
            local_deb = os.path.join(DOWNLOAD_DIR, "update.deb")
            
            r = requests.get(deb_url, timeout=15)
            with open(local_deb, "wb") as f: 
                f.write(r.content)
            
            self.update_ui("WindexOS çekirdek paketleri sisteme işleniyor... %35", 35)
            subprocess.run(f"sudo dpkg -i {local_deb}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            self.update_ui("Sistem depoları senkronize ediliyor (apt update)... %55", 55)
            subprocess.run("sudo apt update", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            self.update_ui("Sistem bileşenleri ve bağımlılıklar yükseltiliyor (apt upgrade)... %75", 75)
            subprocess.run("sudo apt upgrade -y", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            self.update_ui("Kesintiye uğramış paket yapılandırmaları onarılıyor... %85", 85)
            subprocess.run("sudo dpkg --configure -a", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            self.update_ui("Eksik sistem kütüphaneleri tamamlanıyor... %95", 95)
            subprocess.run("sudo apt install -f -y", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            self.update_ui("WindexOS başarıyla güncellendi! Yeniden başlatılıyor... %100", 100)
            
            # 🔥 YENİ SÜRÜMÜ DOSYAYA YAZIYORUZ
            save_new_version(self.target_version)
            
            with open(FLAG_FILE, "w") as f:
                f.write(f"WindexOS v{self.target_version} Güncellemesi")
            
            subprocess.run("rm -rf " + DOWNLOAD_DIR, shell=True)
            subprocess.run("sudo reboot", shell=True)

        except Exception as e:
            self.root.config(cursor="arrow")
            messagebox.showerror("Update Error", f"Güncelleme adımlarında hata oluştu: {str(e)}")
            self.root.destroy()


def show_ask_dialog(current_ver, target_ver):
    ask_root = Tk()
    ask_root.title("WindexOS Update Manager")
    
    w, h = 400, 180
    ws, hs = ask_root.winfo_screenwidth(), ask_root.winfo_screenheight()
    x, y = (ws/2) - (w/2), (hs/2) - (h/2)
    ask_root.geometry(f'{w}x{h}+{int(x)}+{int(y)}')
    ask_root.configure(bg="#111115")
    ask_root.resizable(False, False)

    Label(ask_root, text="YENİ GÜNCELLEME MEVCUT!", font=("Helvetica", 14, "bold"), fg="#00ffcc", bg="#111115").pack(pady=(20, 10))
    Label(ask_root, text=f"v{current_ver} -> v{target_ver} sürümüne yükseltilsin mi?", font=("Helvetica", 11), fg="#ffffff", bg="#111115").pack(pady=(0, 20))

    user_choice = {"update": False}

    def on_yes():
        user_choice["update"] = True
        ask_root.destroy()

    def on_no():
        ask_root.destroy()

    btn_frame = Frame(ask_root, bg="#111115")
    btn_frame.pack()

    Button(btn_frame, text="Şimdi Güncelle", font=("Helvetica", 10, "bold"), bg="#00ffcc", fg="#111115", width=14, command=on_yes).pack(side=LEFT, padx=10)
    Button(btn_frame, text="Sonra Hatırlat", font=("Helvetica", 10), bg="#22222b", fg="#ffffff", width=14, command=on_no).pack(side=RIGHT, padx=10)

    ask_root.mainloop()
    return user_choice["update"]


if __name__ == "__main__":
    print("[*] GitHub üzerinden sürüm kontrol ediliyor...")
    try:
        response = requests.get(f"{REPO_URL}/Packages.txt", timeout=7)
        
        if response.status_code == 200 and response.text.strip():
            target_ver = response.text.strip()
            current_ver = get_current_version()
            
            current_v = parse_version(current_ver)
            remote_v = parse_version(target_ver)
            
            if remote_v > current_v:
                print(f"[+] Yeni sürüm bulundu: v{target_ver}. Kullanıcı onayı bekleniyor...")
                wants_update = show_ask_dialog(current_ver, target_ver)
                if wants_update:
                    UpdateProgressWindow(target_ver)
                else:
                    print("[-] Kullanıcı güncellemeyi erteledi.")
            else:
                print(f"[-] Sisteminiz zaten güncel (Mevcut: v{current_ver} / GitHub: v{target_ver}).")
        else:
            print(f"[-] Sürüm bilgisi okunamadı. HTTP Durumu: {response.status_code}")
    except Exception as e:
        print(f"[-] Sunucu bağlantı hatası: {str(e)}")
