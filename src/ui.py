# -*- coding: utf-8 -*-
import customtkinter as ctk
from tkinter import filedialog
import threading
import os
import sys
import io
import database # Melih'in modülü

# Çıkışı UTF-8 yapma
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class VNSApp(ctk.CTk):
    def __init__(self, engine):
        super().__init__()
        
        # Engine'i main.py'dan alıyoruz
        self.vns_motoru = engine
        self.sidebar_acik = False
        
        self.geometry("850x800")
        self.title("VNS: Akıllı Ses Deşifre Sistemi")
        self.configure(fg_color=("#f1f5f9", "#202128"))

        self.arayuzu_olustur()
        self.kvkk_ekranini_olustur()
        self.gecmisi_veritabanindan_yukle()

    def arayuzu_olustur(self):
        # --- YAN MENÜ (SIDEBAR) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color=("#f8fafc", "#171821"), border_color=("#cbd5e1", "#2d2e37"), border_width=1)
        
        lbl_gecmis = ctk.CTkLabel(self.sidebar_frame, text="Geçmiş İşlemler", font=("Segoe UI", 16, "bold"), text_color="#bb9af7")
        lbl_gecmis.pack(pady=(60, 10))

        self.arama_kutusu = ctk.CTkEntry(self.sidebar_frame, placeholder_text="🔍 Geçmişte Ara...", border_color="#333333", fg_color="#1a1b26")
        self.arama_kutusu.pack(fill="x", padx=10, pady=(0, 10))
        self.arama_kutusu.bind("<KeyRelease>", self.gecmisi_filtrele)

        self.liste_gecmis = ctk.CTkScrollableFrame(self.sidebar_frame, fg_color="transparent")
        self.liste_gecmis.pack(fill="both", expand=True, padx=10, pady=(0, 20))

        # --- SAĞ İÇERİK ALANI ---
        self.sag_icerik_alani = ctk.CTkFrame(self, fg_color="transparent")
        self.sag_icerik_alani.pack(side="left", fill="both", expand=True)

        self.btn_menu = ctk.CTkButton(self, text="☰", width=40, height=40, font=("Segoe UI", 24), fg_color="transparent", hover_color="#2d2e37", text_color="#a9b1d6", command=self.menuyu_ac_kapat)
        self.btn_menu.place(x=10, y=10)

        ana_baslik = ctk.CTkLabel(self.sag_icerik_alani, text="VNS SES ANALİZ SİSTEMİ", text_color=("#000000", "#d1d4e0"), font=("Space Grotesk", 13, "bold"))
        ana_baslik.pack(pady=13)

        self.switch_tema = ctk.CTkSwitch(self.sag_icerik_alani, text="🌞 Aydınlık", command=self.tema_degistir, progress_color="#bb9af7", font=("Segoe UI", 12, "bold"))
        self.switch_tema.pack(anchor="ne", padx=20, pady=(10, 0))

        ana_govde = ctk.CTkFrame(self.sag_icerik_alani, fg_color="transparent")
        ana_govde.pack(fill="both", expand=True, padx=30, pady=10)

        # --- SOL PANEL (DEŞİFRE) ---
        sol_panel = ctk.CTkFrame(ana_govde, fg_color="transparent")
        sol_panel.pack(side="left", fill="both", expand=True, padx=10)
        
        lbl_desifre_baslik = ctk.CTkLabel(sol_panel, text="DEŞİFRE METNİ", text_color="#bb9af7", font=("Segoe UI", 12, "bold"))
        lbl_desifre_baslik.pack(anchor="w", padx=5, pady=(0, 5)) 

        self.txt_desifre = ctk.CTkTextbox(sol_panel, fg_color=("#ffffff", "#1a1b26"), border_color=("#cbd5e1", "#333333"), border_width=1, text_color=("#1e293b", "#a9b1d6"), corner_radius=4, wrap="word", font=("Segoe UI", 13 , "bold"))
        self.txt_desifre.pack(fill="both", expand=True)
        self.txt_desifre.configure(state="disabled")

        # --- SAĞ PANEL (ÖZET) ---
        sag_panel = ctk.CTkFrame(ana_govde, fg_color="transparent")
        sag_panel.pack(side="left", fill="both", expand=True, padx=10)
        
        lbl_ozet_baslik = ctk.CTkLabel(sag_panel, text="YAPAY ZEKA ÖZETİ", text_color="#bb9af7", font=("Segoe UI", 12, "bold"))
        lbl_ozet_baslik.pack(anchor="w", padx=5, pady=(0, 5))

        self.txt_ozet = ctk.CTkTextbox(sag_panel, fg_color=("#ffffff", "#1a1b26"), border_color=("#cbd5e1", "#333333"), border_width=1, text_color=("#1e293b", "#a9b1d6"), corner_radius=4, wrap="word", font=("Segoe UI", 13 , "bold"))
        self.txt_ozet.pack(fill="both", expand=True)
        self.txt_ozet.configure(state="disabled")

        # --- ALT BAR ---
        alt_bar = ctk.CTkFrame(self.sag_icerik_alani, fg_color=("#ffffff", "#1a1b26"), border_color=("#cbd5e1", "#2d2e37"), border_width=1, height=50, corner_radius=8)
        alt_bar.pack(fill="x", padx=40, pady=(10, 30))

        self.lbl_dosya_adi = ctk.CTkLabel(alt_bar, text="bir ses dosyası seçin...", text_color="#565f89", font=("Segoe UI", 11, "italic"))
        self.lbl_dosya_adi.pack(side="left", padx=20)

        self.progress_bar = ctk.CTkProgressBar(alt_bar, width=150, mode="indeterminate", fg_color="#2d2e37", progress_color="#bb9af7")
        self.progress_bar.set(0)

        self.btn_sec = ctk.CTkButton(alt_bar, text="DOSYA SEÇ", width=90, height=30, corner_radius=6, fg_color="#7aa2f7", hover_color="#3d59a1", text_color="#1a1b26", font=("Segoe UI", 11, "bold"), command=self.dosya_secici, state="disabled")
        self.btn_sec.pack(side="right", padx=10)

        self.btn_kaydet = ctk.CTkButton(alt_bar, text="KAYDET", width=90, height=30, corner_radius=6, fg_color="#bb9af7", hover_color="#9d7cd8", text_color="#1a1b26", font=("Segoe UI", 11, "bold"), command=self.metni_disa_aktar)
        self.btn_kaydet.pack(side="right", padx=(0, 10))

    def kvkk_ekranini_olustur(self):
        self.kvkk_kutu = ctk.CTkFrame(self, fg_color="#1a1b26", border_color="#f7768e", border_width=2, corner_radius=15)
        lbl_baslik = ctk.CTkLabel(self.kvkk_kutu, text="⚠️ KVKK AYDINLATMA METNİ", font=("Segoe UI", 16, "bold"), text_color="#f7768e")
        lbl_baslik.pack(pady=(20, 10))

        txt_kvkk = ctk.CTkTextbox(self.kvkk_kutu, width=400, height=200, fg_color="#2d2e37", text_color="#a9b1d6", corner_radius=6, wrap="word")
        txt_kvkk.pack(padx=20, pady=10)
        
        metin = "VNS – Veri Gizliliği...\n\nSes dosyalarınız lokal olarak işlenir, internete aktarılmaz. Sadece metin özetleme için Groq API kullanılır. Devam ederek kabul etmiş sayılırsınız."
        txt_kvkk.insert("0.0", metin)
        txt_kvkk.configure(state="disabled") 

        btn_alani = ctk.CTkFrame(self.kvkk_kutu, fg_color="transparent")
        btn_alani.pack(pady=(10, 20), fill="x", padx=20)

        btn_reddet = ctk.CTkButton(btn_alani, text="Kabul Etmiyorum", width=120, height=35, fg_color="#f44336", hover_color="#c62828", font=("Segoe UI", 12, "bold"), command=self.quit)
        btn_reddet.pack(side="left", padx=10)

        btn_onay = ctk.CTkButton(btn_alani, text="OKUDUM, ONAYLIYORUM", width=220, height=35, fg_color="#bb9af7", hover_color="#9d7cd8", text_color="#1a1b26", font=("Segoe UI", 12, "bold"), command=self.kabul_et)
        btn_onay.pack(side="right", padx=10)
        
        self.kvkk_kutu.place(relx=0.5, rely=0.5, anchor="center")

    # --- ETKİLEŞİM VE Lojik FONKSİYONLARI ---
    def kabul_et(self):
        self.kvkk_kutu.destroy()                     
        self.btn_sec.configure(state="normal")      
        self.lbl_dosya_adi.configure(text="Sistem hazır. Bir ses dosyası seçebilirsiniz...", text_color="#7aa2f7")

    def menuyu_ac_kapat(self):
        if self.sidebar_acik:
            self.sidebar_frame.pack_forget() 
            self.sidebar_acik = False
        else:
            self.sidebar_frame.pack(side="left", fill="y", before=self.sag_icerik_alani) 
            self.sidebar_acik = True

    def tema_degistir(self):
        if self.switch_tema.get() == 1:
            ctk.set_appearance_mode("light")
            self.switch_tema.configure(text="🌙 Karanlık Tema")
        else:
            ctk.set_appearance_mode("dark")
            self.switch_tema.configure(text="🌞 Aydınlık Tema")

    def dosya_secici(self):
        dosya_yolu = filedialog.askopenfilename(title="Ses Dosyası Seçin", filetypes=[("Ses Dosyaları", "*.mp3 *.wav")])
        if dosya_yolu:
            dosya_adi = os.path.basename(dosya_yolu)
            self.lbl_dosya_adi.configure(text=f"İşleniyor: {dosya_adi}", text_color="#7aa2f7")
            threading.Thread(target=self.yapay_zeka_calistir, args=(dosya_yolu, dosya_adi)).start()

    def yapay_zeka_calistir(self, dosya_yolu, dosya_adi):
        self.btn_sec.configure(state="disabled", text="İŞLENİYOR...", fg_color="#2d2e37")
        self.progress_bar.pack(side="left", padx=10)
        self.progress_bar.start()

        try:
            self.lbl_dosya_adi.configure(text="1/2: Yapay zeka sesi dinliyor... (Bekleyin)", text_color="#bb9af7")
            tam_metin = self.vns_motoru.transcribe_audio(dosya_yolu) 
            
            self.metin_kutusuna_yaz(self.txt_desifre, tam_metin)
            
            self.lbl_dosya_adi.configure(text="2/2: Metin özetleniyor... Llama 3 devrede!", text_color="#f7768e")
            ozet_metni = self.vns_motoru.analyze_text(tam_metin)
            
            self.metin_kutusuna_yaz(self.txt_ozet, ozet_metni)
            
            # Veritabanına kaydet
            database.add_record(dosya_adi, tam_metin, ozet_metni)
            self.after(0, self.gecmisi_veritabanindan_yukle) # Listeyi güncelle
            
            self.lbl_dosya_adi.configure(text="İşlem başarıyla tamamlandı!", text_color="#7aa2f7")

        except Exception as e:
            self.lbl_dosya_adi.configure(text="İşlem sırasında bir hata oluştu!", text_color="#f44336")
            
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.btn_sec.configure(state="normal", text="DOSYA SEÇ", fg_color="#7aa2f7")

    def metin_kutusuna_yaz(self, kutu, metin):
        kutu.configure(state="normal")
        kutu.delete("0.0", "end") 
        kutu.insert("0.0", metin)
        kutu.configure(state="disabled")

    def gecmisi_veritabanindan_yukle(self):
        # Arayüzdeki eski butonları temizle
        for widget in self.liste_gecmis.winfo_children():
            widget.destroy()
            
        kayitlar = database.get_all_records()
        for kayit in kayitlar:
            # kayit = (id, dosya_adi, metin, ozet, tarih)
            kayit_id, dosya_adi, tarih = kayit[0], kayit[1], kayit[4]
            saat = tarih.split(" ")[1][:5] # Sadece saati al (HH:MM)
            
            btn_kayit = ctk.CTkButton(self.liste_gecmis, text=f"▶ [{saat}] {dosya_adi}", anchor="w", fg_color="#2d2e37", hover_color="#3d59a1", text_color="#a9b1d6", command=lambda id=kayit_id: self.gecmis_detaya_git(id))
            btn_kayit.pack(fill="x", pady=5)

    def gecmis_detaya_git(self, kayit_id):
        kayit = database.get_record_by_id(kayit_id)
        if kayit:
            self.metin_kutusuna_yaz(self.txt_desifre, kayit[2])
            self.metin_kutusuna_yaz(self.txt_ozet, kayit[3])
            self.lbl_dosya_adi.configure(text=f"Geçmiş Gösteriliyor: {kayit[1]}", text_color="#bb9af7")

    def gecmisi_filtrele(self, event):
        aranan = self.arama_kutusu.get().lower()
        for widget in self.liste_gecmis.winfo_children():
            widget.destroy()
            
        kayitlar = database.search_records(aranan)
        for kayit in kayitlar:
            btn_kayit = ctk.CTkButton(self.liste_gecmis, text=f"▶ {kayit[1]}", anchor="w", fg_color="#2d2e37", hover_color="#3d59a1", text_color="#a9b1d6", command=lambda id=kayit[0]: self.gecmis_detaya_git(id))
            btn_kayit.pack(fill="x", pady=5)

    def metni_disa_aktar(self):
        desifre_metni = self.txt_desifre.get("0.0", "end").strip()
        ozet_metni = self.txt_ozet.get("0.0", "end").strip()
        
        if not desifre_metni:
            return
            
        kayit_yolu = filedialog.asksaveasfilename(title="Metni Kaydet", defaultextension=".txt", filetypes=[("Metin Belgesi", "*.txt")])
        if kayit_yolu:
            with open(kayit_yolu, "w", encoding="utf-8") as dosya:
                dosya.write("--- VNS SES ANALİZ RAPORU ---\n\n--- DEŞİFRE METNİ ---\n" + desifre_metni + "\n\n--- YAPAY ZEKA ÖZETİ ---\n" + ozet_metni)
            self.lbl_dosya_adi.configure(text="Dosya başarıyla kaydedildi!", text_color="#bb9af7")