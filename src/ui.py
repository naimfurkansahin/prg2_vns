#TODO
import customtkinter as ctk
from tkinter import filedialog
import whisper
import threading
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from engine import VNSEngine
import json

mevcut_dizin = os.path.dirname(os.path.abspath(__file__))
os.chdir(mevcut_dizin)
print("\n--- KLASÖRDEKİ GERÇEK DOSYALAR ---")
print(os.listdir(mevcut_dizin))
print("----------------------------------\n")
os.environ["PATH"] = mevcut_dizin + os.pathsep + os.environ["PATH"]


if not os.path.exists("ffmpeg.exe"):
    print("\n" + "="*50)
    print("KRİTİK HATA: ffmpeg.exe bu klasörde BULUNAMADI!")
    print("="*50 + "\n")

load_dotenv()
API_KEY = os.environ.get("GROQ_API_KEY")

if API_KEY:
    vns_motoru = VNSEngine(groq_api_key=API_KEY)
else:
    print("HATA: .env dosyasında API anahtarı bulunamadı!")

app = ctk.CTk()
gecmis_hafizasi = {} 
islem_sayaci = 0


HAFIZA_DOSYASI = "vns_gecmis.json"

def hafizayi_diske_kaydet():
    
    try:
        with open(HAFIZA_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(gecmis_hafizasi, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Hafıza kaydedilemedi: {e}")

def hafizayi_diskten_yukle():
    
    global gecmis_hafizasi, islem_sayaci
    if os.path.exists(HAFIZA_DOSYASI):
        try:
            with open(HAFIZA_DOSYASI, "r", encoding="utf-8") as f:
                yuklenen_veri = json.load(f)
                
              
                gecmis_hafizasi = {int(k): v for k, v in yuklenen_veri.items()}
                
                if gecmis_hafizasi:
                    islem_sayaci = max(gecmis_hafizasi.keys()) 
                    
                   
                    for islem_id, kayit in gecmis_hafizasi.items():
                        dosya_adi = kayit.get("dosya_adi", "Bilinmeyen Dosya")
                        
                        saat_bilgisi = kayit.get("saat", "")
                        buton_metni = f"▶ [{saat_bilgisi}] {dosya_adi}" if saat_bilgisi else f"▶ {dosya_adi}"
                        
                        btn_kayit = ctk.CTkButton(
                            liste_gecmis,
                            text=buton_metni,
                            anchor="w",
                            fg_color="#2d2e37",
                            hover_color="#3d59a1",
                            text_color="#a9b1d6",
                            command=lambda id=islem_id: gecmis_detaya_git(id)
                        )
                        btn_kayit.pack(fill="x", pady=5)
        except Exception as e:
            print(f"Hafıza yüklenirken hata: {e}")

def gecmis_detaya_git(islem_id):
    
    kayit = gecmis_hafizasi[islem_id]
    
    
    txt_desifre.configure(state="normal")
    txt_ozet.configure(state="normal")
    txt_desifre.delete("0.0", "end")
    txt_ozet.delete("0.0", "end")
    
    
    txt_desifre.insert("0.0", kayit["desifre"])
    txt_ozet.insert("0.0", kayit["ozet"])
    
   
    txt_desifre.configure(state="disabled")
    txt_ozet.configure(state="disabled")
    
    lbl_dosya_adi.configure(text=f"Geçmiş Gösteriliyor: {kayit['dosya_adi']}", text_color="#bb9af7")

def gecmisi_filtrele(*args):
    aranan = arama_kutusu.get().lower()
    
    
    for widget in liste_gecmis.winfo_children():
        widget.destroy()
    
    
    for islem_id, kayit in gecmis_hafizasi.items():
        dosya_adi = kayit.get("dosya_adi", "Bilinmeyen Dosya")
        
    if aranan in dosya_adi.lower(): 
            saat_bilgisi = kayit.get("saat", "")
            buton_metni = f"▶ [{saat_bilgisi}] {dosya_adi}" if saat_bilgisi else f"▶ {dosya_adi}"
            
            btn_kayit = ctk.CTkButton(
                liste_gecmis, text=buton_metni, anchor="w",
                fg_color="#2d2e37", hover_color="#3d59a1", text_color="#a9b1d6",
                command=lambda id=islem_id: gecmis_detaya_git(id)
            )
            btn_kayit.pack(fill="x", pady=5)

def yapay_zeka_calistir(dosya_yolu, islem_id):
    dosya_yolu = os.path.normpath(dosya_yolu)
    
    if not os.path.exists(dosya_yolu):
        lbl_dosya_adi.configure(text="Hata: Seçilen dosya diskte bulunamadı!", text_color="#f44336")
        return

    btn_sec.configure(state="disabled", text="İŞLENİYOR...", fg_color="#2d2e37")
    progress_bar.pack(side="left", padx=10)
    progress_bar.start()

    try:
      
        lbl_dosya_adi.configure(text="1/2: Yapay zeka sesi dinliyor... (Bekleyin)", text_color="#bb9af7")
        
        tam_metin = vns_motoru.transcribe_audio(dosya_yolu) 
        gecmis_hafizasi[islem_id]["desifre"] = tam_metin 
        
        txt_desifre.configure(state="normal")
        txt_desifre.delete("0.0", "end") 
        txt_desifre.insert("0.0", tam_metin)
        txt_desifre.configure(state="disabled")
        
       
        lbl_dosya_adi.configure(text="2/2: Metin özetleniyor... Llama 3 devrede!", text_color="#f7768e")
        
        ozet_metni = vns_motoru.analyze_text(tam_metin)
        gecmis_hafizasi[islem_id]["ozet"] = ozet_metni 
        
        txt_ozet.configure(state="normal")
        txt_ozet.delete("0.0", "end")
        txt_ozet.insert("0.0", ozet_metni)
        txt_ozet.configure(state="disabled")
        
        lbl_dosya_adi.configure(text="İşlem başarıyla tamamlandı!", text_color="#7aa2f7")
        
       
        hafizayi_diske_kaydet()

    except Exception as e:
        print(f"Sistem Hatası: {e}")
        lbl_dosya_adi.configure(text="İşlem sırasında bir hata oluştu!", text_color="#f44336")
        
    
    progress_bar.stop()
    progress_bar.set(0)
    progress_bar.pack_forget()
    btn_sec.configure(state="normal", text="DOSYA SEÇ", fg_color="#7aa2f7")


def islemi_arka_planda_baslat(dosya_yolu , islem_id):
    thread = threading.Thread(target=yapay_zeka_calistir, args=(dosya_yolu,islem_id))
    thread.start()

def metni_kaydet():
   
    txt_desifre.configure(state="normal")
    txt_ozet.configure(state="normal")
    
    desifre_metni = txt_desifre.get("0.0", "end").strip()
    ozet_metni = txt_ozet.get("0.0", "end").strip()
    

    txt_desifre.configure(state="disabled")
    txt_ozet.configure(state="disabled")
    
  
    if not desifre_metni and not ozet_metni:
        lbl_dosya_adi.configure(text="Uyarı: Kaydedilecek metin yok!", text_color="#f44336")
        return

   
    kayit_yolu = filedialog.asksaveasfilename(
        title="Metni Kaydet",
        defaultextension=".txt",
        filetypes=[("Metin Belgesi", "*.txt")]
    )
    
    if kayit_yolu:
        try:
            with open(kayit_yolu, "w", encoding="utf-8") as dosya:
                dosya.write("--- VNS SES ANALİZ RAPORU ---\n\n")
                dosya.write("--- DEŞİFRE METNİ ---\n")
                dosya.write(desifre_metni + "\n\n")
                dosya.write("--- YAPAY ZEKA ÖZETİ ---\n")
                dosya.write(ozet_metni + "\n")
            
            lbl_dosya_adi.configure(text="Dosya başarıyla kaydedildi!", text_color="#bb9af7")
        except Exception as e:
            lbl_dosya_adi.configure(text="Kayıt sırasında hata oluştu!", text_color="#f44336")

def tema_degistir():
    if switch_tema.get() == 1:
        ctk.set_appearance_mode("light")
        switch_tema.configure(text="🌙 Karanlık Tema")
    else:
        ctk.set_appearance_mode("dark")
        switch_tema.configure(text="🌞 Aydınlık Tema")
def dosya_secici():
    
    dosya_yolu = filedialog.askopenfilename(
        title="Ses Dosyası Seçin",
        filetypes=[("Ses Dosyaları", "*.mp3 *.wav")]
    )
    
    if dosya_yolu:
        dosya_adi = dosya_yolu.split("/")[-1]
        lbl_dosya_adi.configure(text=f"Dosya: {dosya_adi}", text_color="#7aa2f7")
        
        
        
        global islem_sayaci
        islem_sayaci += 1
        guncel_id = islem_sayaci
        
        su_an = datetime.now().strftime("%H:%M")

        gecmis_hafizasi[guncel_id] = {
            "dosya_adi": dosya_adi,
            "saat": su_an,
            "desifre": "İşlem devam ediyor veya metin yok...",
            "ozet": "İşlem devam ediyor veya özet yok..."
        }
        
        
        
        btn_kayit = ctk.CTkButton(
            liste_gecmis,
            text=f"▶ [{su_an}] {dosya_adi}",
            anchor="w",                  
            fg_color="#2d2e37",          
            hover_color="#3d59a1",     
            text_color="#a9b1d6",
            command=lambda id=guncel_id: gecmis_detaya_git(id) 
        )
        btn_kayit.pack(fill="x", pady=5) 
        hafizayi_diske_kaydet()
        

        islemi_arka_planda_baslat(dosya_yolu, guncel_id)


app.geometry("800x800")
app.title("VNS: Akıllı Ses Deşifre Sistemi      ")

sidebar_frame = ctk.CTkFrame(app, width=250, corner_radius=0, fg_color=("#f8fafc", "#171821"), border_color=("#cbd5e1", "#2d2e37"), border_width=1)

lbl_gecmis = ctk.CTkLabel(sidebar_frame, text="Geçmiş İşlemler", font=("Segoe UI", 16, "bold"), text_color="#bb9af7")
lbl_gecmis.pack(pady=(60, 10))

arama_kutusu = ctk.CTkEntry(sidebar_frame, placeholder_text="🔍 Geçmişte Ara...", border_color="#333333", fg_color="#1a1b26")
arama_kutusu.pack(fill="x", padx=10, pady=(0, 10))
arama_kutusu.bind("<KeyRelease>", gecmisi_filtrele)

liste_gecmis = ctk.CTkScrollableFrame(sidebar_frame, fg_color="transparent")
liste_gecmis.pack(fill="both", expand=True, padx=10, pady=(0, 20))

sag_icerik_alani = ctk.CTkFrame(app, fg_color="transparent")
sag_icerik_alani.pack(side="left", fill="both", expand=True)

sidebar_acik = False
def menuyu_ac_kapat():
    global sidebar_acik
    if sidebar_acik:
     
        sidebar_frame.pack_forget() 
        sidebar_acik = False
    else:
      
        sidebar_frame.pack(side="left", fill="y", before=sag_icerik_alani) 
        sidebar_acik = True


btn_menu = ctk.CTkButton(
    app, 
    text="☰", 
    width=40, 
    height=40, 
    font=("Segoe UI", 24), 
    fg_color="transparent",      
    hover_color="#2d2e37",       
    text_color="#a9b1d6",
    command=menuyu_ac_kapat       
)
btn_menu.place(x=10, y=10)

ana_baslik = ctk.CTkLabel(
    sag_icerik_alani, 
    text="VNS SES ANALİZ SİSTEMİ", 
    text_color=("#000000", "#d1d4e0"),
    font=("Space Grotesk", 13, "bold"),
    
)

switch_tema = ctk.CTkSwitch(
    sag_icerik_alani, text="🌞 Aydınlık", 
    command=tema_degistir, progress_color="#bb9af7", 
    font=("Segoe UI", 12, "bold")
)
switch_tema.pack(anchor="ne", padx=20, pady=(10, 0))

ana_baslik.pack(pady=13)
app.configure(fg_color=("#f1f5f9", "#202128"))

ana_govde = ctk.CTkFrame(sag_icerik_alani, fg_color="transparent")
ana_govde.pack(fill="both", expand=True, padx=30, pady=10)

sol_panel = ctk.CTkFrame(ana_govde, fg_color="transparent")
sol_panel.pack(side="left", fill="both", expand=True, padx=10)

txt_desifre = ctk.CTkTextbox(
    sol_panel, 
    fg_color=("#ffffff", "#1a1b26"), 
    border_color=("#cbd5e1", "#333333"), 
    border_width=1, 
    text_color=("#1e293b", "#a9b1d6"),
    corner_radius=4,
    wrap="word",          
    font=("Segoe UI", 13 , "bold") 
)
txt_desifre.pack(fill="both", expand=True)
txt_desifre._textbox.configure(padx=15, pady=15)
txt_desifre.configure(state="disabled")

lbl_desifre_baslik = ctk.CTkLabel(sol_panel, text="DEŞİFRE METNİ", text_color="#bb9af7", font=("Segoe UI", 12, "bold"))
lbl_desifre_baslik.pack(anchor="w", padx=5, pady=(0, 5)) 

sag_panel = ctk.CTkFrame(ana_govde, fg_color="transparent")
sag_panel.pack(side="left", fill="both", expand=True, padx=10)

txt_ozet = ctk.CTkTextbox(
    sag_panel, 
    fg_color=("#ffffff", "#1a1b26"),       
    border_color=("#cbd5e1", "#333333"),   
    border_width=1, 
    text_color=("#1e293b", "#a9b1d6"),    
    corner_radius=4,
    wrap="word",          
    font=("Segoe UI", 13 , "bold")
)
txt_ozet.pack(fill="both", expand=True)
txt_ozet._textbox.configure(padx=15, pady=15)
txt_ozet.configure(state="disabled")

lbl_ozet_baslik = ctk.CTkLabel(sag_panel, text="YAPAY ZEKA ÖZETİ", text_color="#bb9af7", font=("Segoe UI", 12, "bold"))
lbl_ozet_baslik.pack(anchor="w", padx=5, pady=(0, 5))

alt_bar = ctk.CTkFrame(sag_icerik_alani, fg_color=("#ffffff", "#1a1b26"), border_color=("#cbd5e1", "#2d2e37"), border_width=1, height=50, corner_radius=8)
alt_bar.pack(fill="x", padx=40, pady=(10, 30))

lbl_dosya_adi = ctk.CTkLabel(alt_bar, text="bir ses dosyası seçin...", text_color="#565f89", font=("Segoe UI", 11, "italic"))
lbl_dosya_adi.pack(side="left", padx=20)

progress_bar = ctk.CTkProgressBar(alt_bar, width=150, mode="indeterminate", fg_color="#2d2e37", progress_color="#bb9af7")
progress_bar.set(0)

btn_sec = ctk.CTkButton(
    alt_bar, text="DOSYA SEÇ", width=90, height=30, corner_radius=6,
    fg_color="#7aa2f7", hover_color="#3d59a1", text_color="#1a1b26", font=("Segoe UI", 11, "bold"),
    command=dosya_secici,
    state="disabled"
)
btn_sec.pack(side="right", padx=10)

btn_kaydet = ctk.CTkButton(
    alt_bar, text="KAYDET", width=90, height=30, corner_radius=6,
    fg_color="#bb9af7", hover_color="#9d7cd8", text_color="#1a1b26", font=("Segoe UI", 11, "bold"),
    command=metni_kaydet
)
btn_kaydet.pack(side="right", padx=(0, 10))

kvkk_kutu = ctk.CTkFrame(app, fg_color="#1a1b26", border_color="#f7768e", border_width=2, corner_radius=15)

lbl_baslik = ctk.CTkLabel(kvkk_kutu, text="⚠️ KVKK AYDINLATMA METNİ", font=("Segoe UI", 16, "bold"), text_color="#f7768e")
lbl_baslik.pack(pady=(20, 10))

txt_kvkk = ctk.CTkTextbox(kvkk_kutu, width=400, height=200, fg_color="#2d2e37", text_color="#a9b1d6", corner_radius=6, wrap="word")
txt_kvkk.pack(padx=20, pady=10)

ornek_metin = """VNS – Veri Gizliliği ve Kullanıcı Bilgilendirmesi

VNS, gizlilik odaklı bir çalışma prensibiyle tasarlanmıştır. Ses dosyalarınızın deşifre işlemi tamamen yerel makinenizde (Faster-Whisper) gerçekleştirilir ve ses verileriniz asla internete aktarılmaz.

Analiz ve özetleme aşamasında ise sadece oluşturulan metin içeriği, güvenli bir API (Groq) üzerinden Llama 3 modeline iletilir. Bu süreçte hiçbir kişisel veri veya ses dosyası bulut sunucularına gönderilmemektedir. Devam ederek bu işlem sürecini ve veri gizliliği politikasını kabul etmiş sayılırsınız.

Lütfen uygulamayı kullanabilmek için kişisel verilerinizin işlenmesine dair aydınlatma metnini okuyup onaylayınız. 

Sistemimiz ses dosyalarınızı deşifre etmek ve özetlemek amacıyla işlemektedir."""

txt_kvkk.insert("0.0", ornek_metin)
txt_kvkk.configure(state="disabled") 

def kabul_et():
    kvkk_kutu.destroy()                     
    btn_sec.configure(state="normal")      
    lbl_dosya_adi.configure(text="Sistem hazır. Bir ses dosyası seçebilirsiniz...", text_color="#7aa2f7")

def reddet():
    app.quit() 

btn_alani = ctk.CTkFrame(kvkk_kutu, fg_color="transparent")
btn_alani.pack(pady=(10, 20), fill="x", padx=20)

btn_reddet = ctk.CTkButton(
    btn_alani, text="Kabul Etmiyorum", width=120, height=35,
    fg_color="#f44336", hover_color="#c62828", font=("Segoe UI", 12, "bold"),
    command=reddet
)
btn_reddet.pack(side="left", padx=10)

btn_onay = ctk.CTkButton(
    btn_alani, text="OKUDUM, ONAYLIYORUM", width=220, height=35,
    fg_color="#bb9af7", hover_color="#9d7cd8", text_color="#1a1b26", font=("Segoe UI", 12, "bold"),
    command=kabul_et
)
btn_onay.pack(side="right", padx=10)
kvkk_kutu.place(relx=0.5, rely=0.5, anchor="center")
hafizayi_diskten_yukle()
app.mainloop()
