#TODO
import customtkinter as ctk
from tkinter import filedialog
import whisper
import threading
import os
import sys
from datetime import datetime

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

app = ctk.CTk()
gecmis_hafizasi = {} 
islem_sayaci = 0

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

def yapay_zeka_calistir(dosya_yolu , islem_id):

    dosya_yolu = os.path.normpath(dosya_yolu)
    
    if not os.path.exists(dosya_yolu):
        lbl_dosya_adi.configure(text="Hata: Seçilen dosya diskte bulunamadı!", text_color="#f44336")
        return


    btn_sec.configure(state="disabled", text="İŞLENİYOR...", fg_color="#2d2e37")
    lbl_dosya_adi.configure(text="Yapay zeka sesi dinliyor... (Bekleyin)", text_color="#bb9af7")
    progress_bar.pack(side="left", padx=10)
    progress_bar.start()
    try:

        model = whisper.load_model("base")
        sonuc = model.transcribe(dosya_yolu, fp16=False, language="tr") 
        tam_metin = sonuc["text"].strip()
        gecmis_hafizasi[islem_id]["desifre"] = tam_metin
        txt_desifre.configure(state="normal")
        txt_desifre.delete("0.0", "end") 
        txt_desifre.insert("0.0", tam_metin)
        txt_desifre.configure(state="disabled")
        
        lbl_dosya_adi.configure(text="Deşifre başarıyla tamamlandı!", text_color="#7aa2f7")
        
    except Exception as e:

        print(f"Sistem Hatası: {e}")
        lbl_dosya_adi.configure(text="Ses işlenirken bir hata oluştu!", text_color="#f44336")
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
        
      
        gecmis_hafizasi[guncel_id] = {
            "dosya_adi": dosya_adi,
            "desifre": "İşlem devam ediyor veya metin yok...",
            "ozet": "İşlem devam ediyor veya özet yok..."
        }
        
        su_an = datetime.now().strftime("%H:%M")
        
        
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
        

        islemi_arka_planda_baslat(dosya_yolu, guncel_id)


app.geometry("800x800")
app.title("VNS: Akıllı Ses Deşifre Sistemi      ")

sidebar_frame = ctk.CTkFrame(app, width=250, corner_radius=0, fg_color="#171821", border_color="#2d2e37", border_width=1)

lbl_gecmis = ctk.CTkLabel(sidebar_frame, text="Geçmiş İşlemler", font=("Segoe UI", 16, "bold"), text_color="#bb9af7")
lbl_gecmis.pack(pady=(60, 10))

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
    text_color="#d1d4e0", 
    font=("Space Grotesk", 13, "bold"),
    
)
ana_baslik.pack(pady=13)
app.configure(fg_color="#202128")

ana_govde = ctk.CTkFrame(sag_icerik_alani, fg_color="transparent")
ana_govde.pack(fill="both", expand=True, padx=30, pady=10)

sol_panel = ctk.CTkFrame(ana_govde, fg_color="transparent")
sol_panel.pack(side="left", fill="both", expand=True, padx=10)

txt_desifre = ctk.CTkTextbox(
    sol_panel, 
    fg_color="#1a1b26", 
    border_color="#333333", 
    border_width=1, 
    text_color="#a9b1d6",
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
    fg_color="#1a1b26", 
    border_color="#333333", 
    border_width=1, 
    text_color="#a9b1d6",
    corner_radius=4,
    wrap="word",          
    font=("Segoe UI", 13 , "bold") 
)
txt_ozet.pack(fill="both", expand=True)
txt_ozet._textbox.configure(padx=15, pady=15)
txt_ozet.configure(state="disabled")

lbl_ozet_baslik = ctk.CTkLabel(sag_panel, text="YAPAY ZEKA ÖZETİ", text_color="#bb9af7", font=("Segoe UI", 12, "bold"))
lbl_ozet_baslik.pack(anchor="w", padx=5, pady=(0, 5))

alt_bar = ctk.CTkFrame(sag_icerik_alani, fg_color="#1a1b26", border_color="#2d2e37", border_width=1, height=50, corner_radius=8)
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

ornek_metin = """Simge'nin hazırlayacağı KVKK metni buraya eklenecek...

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
app.mainloop()
