import sys
import os
import subprocess
from tkinter import *
from tkinter import messagebox

CONFIG_FILE = "/Windex/System64/apps/optihub.cfg"

# SÜPER GÜÇLÜ ROOT KONTROLÜ: Root değilse grafiksel şifre ister ve kendini yeniden başlatır
if os.geteuid() != 0:
    # Cinnamon/Zenity şifre kutusunu tetikle
    cmd = "zenity --password --title='WindexOS // OptiHub Yetkilendirme'"
    password = subprocess.check_output(cmd, shell=True).decode().strip()
    
    if password:
        # Kodun kendi yolunu bul ve sudo ile şifreyi basarak yeniden tetikle
        script_path = os.path.abspath(__file__)
        os.execv('/usr/bin/sudo', ['sudo', '-S', 'python3', script_path])
    else:
        sys.exit(1)

class OptiHubApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WindexOS // OptiHub v1.5")
        self.root.geometry("450x620")
        self.root.configure(bg="#0a0a0c")
        self.root.resizable(False, False)

        # Başlık Bölümü
        self.title_label = Label(root, text="WINDEX OPTIHUB", font=("Helvetica", 24, "bold"), fg="#00ffcc", bg="#0a0a0c")
        self.title_label.pack(pady=20)

        self.subtitle_label = Label(root, text="WindexOS Akıllı Güç Yönetimi", font=("Helvetica", 10), fg="#777777", bg="#0a0a0c")
        self.subtitle_label.pack(pady=5)

        # Durum Gösterge Paneli
        self.status_frame = Frame(root, bg="#111115", bd=2, relief=RIDGE)
        self.status_frame.pack(pady=20, fill=X, padx=40)
        
        self.status_title = Label(self.status_frame, text="SİSTEMİN KAYITLI AKTİF MODU", font=("Helvetica", 11), fg="#aaaaaa", bg="#111115")
        self.status_title.pack(pady=5)
        
        self.status_text = Label(self.status_frame, text="NORMAL / BALANCED", font=("Helvetica", 24, "bold"), fg="#00ffcc", bg="#111115")
        self.status_text.pack(pady=10)

        # Butonlar
        self.btn_normal = Button(root, text="1. NORMAL MOD (DENGE)", font=("Helvetica", 11, "bold"), bg="#1c1c24", fg="#ffffff", activebackground="#2a2a35", activeforeground="#ffffff", bd=0, height=2, command=self.set_normal_mode)
        self.btn_normal.pack(fill=X, padx=50, pady=8)

        self.btn_boost = Button(root, text="2. BOOST MOD (HIZLI)", font=("Helvetica", 11, "bold"), bg="#0055ff", fg="#ffffff", activebackground="#3377ff", activeforeground="#ffffff", bd=0, height=2, command=self.set_boost_mode)
        self.btn_boost.pack(fill=X, padx=50, pady=8)

        self.btn_ultra = Button(root, text="3. ULTRA MOD (MAKSİMUM FOCUS)", font=("Helvetica", 11, "bold"), bg="#8800ff", fg="#ffffff", activebackground="#aa33ff", activeforeground="#ffffff", bd=0, height=2, command=self.set_ultra_mode)
        self.btn_ultra.pack(fill=X, padx=50, pady=8)

        self.btn_overclock = Button(root, text="4. THE OVERCLOCK (SÖMÜRME)", font=("Helvetica", 12, "bold"), bg="#ff0055", fg="#ffffff", activebackground="#ff3377", activeforeground="#ffffff", bd=0, height=2, command=self.set_overclock_mode)
        self.btn_overclock.pack(fill=X, padx=50, pady=20)

        self.footer = Label(root, text="WindexOS Kernel Optimization Subsystem", font=("Helvetica", 8, "italic"), fg="#444444", bg="#0a0a0c")
        self.footer.pack(side=BOTTOM, pady=15)

        # Açılışta hafızadaki modu yükle
        self.load_saved_mode()

    def save_mode(self, mode_name):
        try:
            with open(CONFIG_FILE, "w") as f:
                f.write(mode_name)
        except:
            pass

    def load_saved_mode(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    saved_mode = f.read().strip()
                
                if saved_mode == "NORMAL":
                    self.status_text.config(text="NORMAL / BALANCED", fg="#00ffcc")
                elif saved_mode == "BOOST":
                    self.status_text.config(text="BOOST / PERFORMANCE", fg="#0055ff")
                elif saved_mode == "ULTRA":
                    self.status_text.config(text="ULTRA FOCUS ACTIVE", fg="#8800ff")
                elif saved_mode == "OVERCLOCK":
                    self.status_text.config(text="THE OVERCLOCK 🔥", fg="#ff0055")
            except:
                self.status_text.config(text="NORMAL / BALANCED", fg="#00ffcc")
        else:
            self.save_mode("NORMAL")

    def execute_cmd(self, cmd):
        try:
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            return False

    def set_normal_mode(self):
        self.execute_cmd("cpupower frequency-set -g ondemand || cpufreq-set -g ondemand || cpupower frequency-set -g powersave")
        self.status_text.config(text="NORMAL / BALANCED", fg="#00ffcc")
        self.save_mode("NORMAL")
        messagebox.showinfo("OptiHub", "Sistem normal/dengeli moda çekildi.")

    def set_boost_mode(self):
        self.execute_cmd("cpupower frequency-set -g performance || cpufreq-set -g performance")
        self.status_text.config(text="BOOST / PERFORMANCE", fg="#0055ff")
        self.save_mode("BOOST")
        messagebox.showinfo("OptiHub", "Tüm CPU çekirdekleri en yüksek frekansa kilitlendi.")

    def set_ultra_mode(self):
        self.execute_cmd("cpupower frequency-set -g performance || cpufreq-set -g performance")
        self.execute_cmd("sync; echo 3 > /proc/sys/vm/drop_caches")
        self.execute_cmd("renice -n -10 -u root")
        self.status_text.config(text="ULTRA FOCUS ACTIVE", fg="#8800ff")
        self.save_mode("ULTRA")
        messagebox.showinfo("OptiHub", "Ultra Mod Aktif! RAM önbelleği temizlendi.")

    def set_overclock_mode(self):
        answer = messagebox.askyesno("TEHLİKE UYARISI", "THE OVERCLOCK modu donanım limitlerini sömürür. Devam edilsin mi?")
        if answer:
            self.execute_cmd("cpupower frequency-set -g performance || cpufreq-set -g performance")
            self.execute_cmd("sync; echo 3 > /proc/sys/vm/drop_caches")
            self.execute_cmd("sysctl -w vm.dirty_ratio=10")
            self.execute_cmd("sysctl -w vm.dirty_background_ratio=5")
            self.execute_cmd("pidof cinnamon | xargs -r renice -n -20")
            self.execute_cmd("pidof xorg | xargs -r renice -n -20")
            self.status_text.config(text="THE OVERCLOCK 🔥", fg="#ff0055")
            self.save_mode("OVERCLOCK")
            messagebox.showwarning("WindexOS", "SİSTEM CANAVAR MODUNDA!")

if __name__ == "__main__":
    root = Tk()
    app = OptiHubApp(root)
    root.mainloop()
