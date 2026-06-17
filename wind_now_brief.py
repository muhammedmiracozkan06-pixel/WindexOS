import sys
import os
import time
import threading
from tkinter import *

class WindNowBrief(Tk):
    def __init__(self):
        super().__init__()
        self.title("Wind Now Brief Widget")
        
        # ❖ LINUX X11 TAM UYUMLU ANDROID WIDGET MİMARİSİ
        self.overrideredirect(True)
        
        # Pencere tipini 'dock' yapıyoruz, böylece Linux bunu masaüstü bileşeni sayıyor
        try:
            self.wm_attributes("-type", "dock")
        except:
            try:
                self.tk.call('wm', 'attributes', self._w, '-type', 'splash')
            except:
                pass

        # Renk hatasını engellemek için arka plana net bir koyu renk veriyoruz
        # Android One UI temasına uygun derin gece siyahı
        BG_COLOR = "#0c0c12" 
        self.config(bg=BG_COLOR)
        
        # Ekran konumu: Sağ üst köşe
        screen_w = self.winfo_screenwidth()
        self.widget_w, self.widget_h = 340, 140
        self.geometry(f"{self.widget_w}x{self.widget_h}+{screen_w - self.widget_w - 40}+60")
        
        # Canvas arka planına da net rengimizi çakıyoruz, unknown color hatası çöp oluyor!
        self.canvas = Canvas(self, width=self.widget_w, height=self.widget_h, bg=BG_COLOR, highlightthickness=0, bd=0)
        self.canvas.pack(fill=BOTH, expand=True)
        
        # One UI / Material You tarzı oval arka plan kartı (Penceremizin içinde şık bir widget alanı)
        self.draw_rounded_rectangle(5, 5, self.widget_w-5, self.widget_h-5, radius=20, fill="#161622", outline="#00ffcc", width=1.5)

        # Yazıları tam koordinatlarıyla Canvas üzerine oturtuyoruz
        self.text_greeting = self.canvas.create_text(
            self.widget_w // 2, 45, 
            text="", font=("Helvetica", 18, "bold"), fill="#00ffcc", justify=CENTER
        )
        
        self.text_sub = self.canvas.create_text(
            self.widget_w // 2, 85, 
            text="❖ Detaylı Bilgiler ve Öneriler", font=("Helvetica", 10), fill="#888899", justify=CENTER
        )
        
        self.text_hint = self.canvas.create_text(
            self.widget_w // 2, 112, 
            text="Günün özetini görmek için tıkla", font=("Helvetica", 8, "italic"), fill="#444455", justify=CENTER
        )

        # Tıklama olayını Canvas'a bağlıyoruz
        self.canvas.bind("<Button-1>", self.open_detailed_panel)

        # Rutinler listesi
        self.rutinler = [
            {"saat": "16:00", "is": "Kod Geliştirme ve Mola Zamanı!", "triggered": False},
            {"saat": "20:00", "is": "WindexOS Akşam Güncelleme Kontrolü!", "triggered": False},
            {"saat": "23:00", "is": "Sistem Yedekleme ve Dinlenme!", "triggered": False}
        ]

        # Döngüleri Başlat
        self.update_widget()
        self.check_routines_loop()

    def draw_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        """ Canvas üzerinde pürüzsüz oval köşeli kutu çizen fonksiyon """
        points = [x1+radius, y1,
                  x1+radius, y1,
                  x2-radius, y1,
                  x2-radius, y1,
                  x2, y1,
                  x2, y1+radius,
                  x2, y1+radius,
                  x2, y2-radius,
                  x2, y2-radius,
                  x2, y2,
                  x2-radius, y2,
                  x2-radius, y2,
                  x1+radius, y2,
                  x1+radius, y2,
                  x1, y2,
                  x1, y2-radius,
                  x1, y2-radius,
                  x1, y1+radius,
                  x1, y1+radius,
                  x1, y1]
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def get_greeting(self):
        hour = int(time.strftime("%H"))
        if 5 <= hour < 12:
            return "Günaydın."
        elif 12 <= hour < 17:
            return "İyi Günler."
        elif 17 <= hour < 22:
            return "İyi Akşamlar."
        else:
            return "İyi Geceler."

    def update_widget(self):
        self.canvas.itemconfig(self.text_greeting, text=self.get_greeting())
        self.after(60000, self.update_widget)

    def check_routines_loop(self):
        current_time = time.strftime("%H:%M")
        for r in self.rutinler:
            if current_time == r["saat"] and not r["triggered"]:
                r["triggered"] = True
                threading.Thread(target=self.fire_routine_alert, args=(r["is"],)).start()
            elif current_time != r["saat"]:
                r["triggered"] = False
                
        self.after(1000, self.check_routines_loop)

    def fire_routine_alert(self, job_text):
        for _ in range(10):
            sys.stdout.write('\a')
            sys.stdout.flush()
            time.sleep(1)

        alert_win = Tk()
        alert_win.title("WindexOS Alarm")
        alert_win.geometry("400x220")
        alert_win.configure(bg="#111115")
        alert_win.attributes("-topmost", True)
        
        Label(alert_win, text="❖ WINDEXOS RUTİN ALARMI", font=("Helvetica", 14, "bold"), fg="#00ffcc", bg="#111115").pack(pady=20)
        Label(alert_win, text=job_text, font=("Helvetica", 12), fg="#ffffff", bg="#111115", wrap=350).pack(pady=10)
        
        Button(alert_win, text="Kapat", font=("Helvetica", 10, "bold"), bg="#00ffcc", fg="#111115", width=15, command=alert_win.destroy).pack(pady=15)
        alert_win.mainloop()

    def open_detailed_panel(self, event=None):
        panel = Toplevel(self)
        panel.title("Now Brief - Günlük Özet")
        panel.geometry("380x520")
        panel.configure(bg="#0c0c10")
        panel.attributes("-topmost", True)
        
        screen_w = panel.winfo_screenwidth()
        screen_h = panel.winfo_screenheight()
        panel.geometry(f"380x520+{screen_w//2 - 190}+{screen_h//2 - 260}")

        Label(panel, text=self.get_greeting().upper(), font=("Helvetica", 20, "bold"), fg="#00ffcc", bg="#0c0c10").pack(pady=(30, 5))
        Label(panel, text=time.strftime("%d.%m.%Y — %H:%M"), font=("Helvetica", 11), fg="#666677", bg="#0c0c10").pack(pady=(0, 25))
        
        card = Frame(panel, bg="#14141c", bd=1, relief=SOLID, highlightbackground="#22222b", highlightthickness=1)
        card.pack(fill=BOTH, expand=True, padx=25, pady=10)
        
        Label(card, text="⛅ HAVA DURUMU & GÜN ÖNERİLERİ", font=("Helvetica", 11, "bold"), fg="#ffffff", bg="#14141c").pack(pady=20)
        
        oneriler = [
            ("🚶 Yürüyüş Aktivitesi:", "Mükemmel [✓]"),
            ("🏡 Bahçecilik İşleri:", "İdeal [✓]"),
            ("📸 Fotoğrafçılık Çekimi:", "Çok İyi [✓]"),
            ("🏎️ Dış Mekan Gezintisi:", "Kötü [✗] (Yağış Riski)")
        ]
        
        for aktivite, durum in oneriler:
            row = Frame(card, bg="#14141c")
            row.pack(fill=X, padx=20, pady=10)
            
            lbl_akt = Label(row, text=aktivite, font=("Helvetica", 11), fg="#888899", bg="#14141c")
            lbl_akt.pack(side=LEFT)
            
            color = "#00ffcc" if "Mükemmel" in durum or "İyi" in durum or "İdeal" in durum else "#ff3333"
            lbl_dur = Label(row, text=durum, font=("Helvetica", 11, "bold"), fg=color, bg="#14141c")
            lbl_dur.pack(side=RIGHT)
            
        Button(card, text="PANELİ KAPAT", font=("Helvetica", 10, "bold"), bg="#1c1c24", fg="#00ffcc", activebackground="#00ffcc", activeforeground="#111115", width=22, height=2, command=panel.destroy).pack(pady=25)

if __name__ == "__main__":
    app = WindNowBrief()
    app.mainloop()
