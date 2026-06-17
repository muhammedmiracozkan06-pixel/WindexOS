import sys
import os
import time
import random
from tkinter import *

class WindexAOD:
    def __init__(self):
        self.root = Tk()
        self.root.title("WindexOS Always On Display")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="#000000")
        
        # Fare imlecini tamamen gizle
        self.root.config(cursor="none")

        # Kapsayıcı Frame (Burn-in koruması için bunu hareket ettireceğiz)
        self.aod_frame = Frame(self.root, bg="#000000")
        self.aod_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

        # Fütüristik Dijital Saat
        self.time_label = Label(self.aod_frame, text="00:00:00", font=("Helvetica", 68, "bold"), fg="#00ffcc", bg="#000000")
        self.time_label.pack()

        # Tarih Etiketi
        self.date_label = Label(self.aod_frame, text="15.06.2026", font=("Helvetica", 16), fg="#888899", bg="#000000")
        self.date_label.pack(pady=(15, 5))

        # WindexOS Amblemi (Tracking hatası vermemesi için araları boşluklu normal font yaptık)
        self.logo_label = Label(self.aod_frame, text="❖  W I N D E X O S  S Y S T E M  C O R E", font=("Helvetica", 9), fg="#444455", bg="#000000")
        self.logo_label.pack(pady=(25, 0))

        # Çıkış Tetikleyicileri (Fare oynarsa veya tuşa basılırsa kapanır)
        self.root.bind("<Motion>", self.exit_aod)
        self.root.bind("<Key>", self.exit_aod)
        self.root.bind("<Button-1>", self.exit_aod)

        # Döngüleri Başlat
        self.update_time_and_date()
        self.anti_burn_in_loop()
        
        self.root.mainloop()

    def update_time_and_date(self):
        """ Saati ve tarihi anlık günceller """
        current_time = time.strftime("%H:%M:%S")
        current_date = time.strftime("%d.%m.%Y") 
        
        self.time_label.config(text=current_time)
        self.date_label.config(text=current_date)
        
        # Her 1 saniyede bir saati güncelle
        self.root.after(1000, self.update_time_and_date)

    def anti_burn_in_loop(self):
        """ Ekran yanmasını önlemek için widget'ların yerini hafifçe değiştirir """
        # Merkezden hafif sapmalar hesapla
        dx = random.randint(-40, 40) / 1000
        dy = random.randint(-40, 40) / 1000
        
        self.aod_frame.place(relx=0.5 + dx, rely=0.5 + dy, anchor=CENTER)
        
        # Her 5 dakikada bir konumu kaydır
        self.root.after(300000, self.anti_burn_in_loop)

    def exit_aod(self, event=None):
        """ Kullanıcı ekrana dokunduğu an AOD modundan çıkar """
        self.root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    AOD = WindexAOD()
