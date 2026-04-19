#TODO
import customtkinter as ctk
from tkinter import filedialog
import whisper
import threading
import os
import sys

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

def yapay_zeka_calistir(dosya_yolu):

    dosya_yolu = os.path.normpath(dosya_yolu)
    
    if not os.path.exists(dosya_yolu):
        lbl_dosya_adi.configure(text="Hata: Seçilen dosya diskte bulunamadı!", text_color="#f44336")
        return


    btn_sec.configure(state="disabled", text="İŞLENİYOR...", fg_color="#2d2e37")
    lbl_dosya_adi.configure(text="Yapay zeka sesi dinliyor... (Bekleyin)", text_color="#bb9af7")
    
    try:

        model = whisper.load_model("base")
        
        sonuc = model.transcribe(dosya_yolu, fp16=False, language="tr") 
        
        tam_metin = sonuc["text"].strip()
        txt_desifre.delete("0.0", "end") 
        txt_desifre.insert("0.0", tam_metin)
        
        lbl_dosya_adi.configure(text="Deşifre başarıyla tamamlandı!", text_color="#7aa2f7")
        
    except Exception as e:

        print(f"Sistem Hatası: {e}")
        lbl_dosya_adi.configure(text="Ses işlenirken bir hata oluştu!", text_color="#f44336")

    btn_sec.configure(state="normal", text="DOSYA SEÇ", fg_color="#7aa2f7")



def islemi_arka_planda_baslat(dosya_yolu):
    thread = threading.Thread(target=yapay_zeka_calistir, args=(dosya_yolu,))
    thread.start()

def dosya_secici():
    
    dosya_yolu = filedialog.askopenfilename(
        title="Ses Dosyası Seçin",
        filetypes=[("Ses Dosyaları", "*.mp3 *.wav")]
    )
    
    if dosya_yolu:
        dosya_adi = dosya_yolu.split("/")[-1]
        lbl_dosya_adi.configure(text=f"Dosya: {dosya_adi}", text_color="#7aa2f7")
        
        try:
            lbl_desifre_placeholder.destroy()
            lbl_ozet_placeholder.destroy()
        except:
            pass
            
        islemi_arka_planda_baslat(dosya_yolu)

app.geometry("800x800")
app.title("VNS: Akıllı Ses Deşifre Sistemi      ")
ana_baslik = ctk.CTkLabel(
    app, 
    text="VNS SES ANALİZ SİSTEMİ", 
    text_color="#d1d4e0", 
    font=("Space Grotesk", 13, "bold"),
    
)
ana_baslik.pack(pady=13)
app.configure(fg_color="#202128")

ana_govde = ctk.CTkFrame(app, fg_color="transparent")
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
    font=("Segoe UI", 13) 
)
txt_desifre.pack(fill="both", expand=True)
txt_desifre._textbox.configure(padx=15, pady=15)

lbl_desifre_placeholder = ctk.CTkLabel(txt_desifre, text="ses deşifre metni", text_color="#454b68", font=("Segoe UI", 11, "italic"))
lbl_desifre_placeholder.place(x=10, y=5) 

sag_panel = ctk.CTkFrame(ana_govde, fg_color="transparent")
sag_panel.pack(side="left", fill="both", expand=True, padx=10)

txt_ozet = ctk.CTkTextbox(
    sag_panel, 
    fg_color="#1a1b26", 
    border_color="#333333", 
    border_width=1, 
    text_color="#a9b1d6",
    corner_radius=4
)
txt_ozet.pack(fill="both", expand=True)

lbl_ozet_placeholder = ctk.CTkLabel(txt_ozet, text="yapay zeka özeti", text_color="#454b68", font=("Segoe UI", 11, "italic"))
lbl_ozet_placeholder.place(x=10, y=5)

alt_bar = ctk.CTkFrame(app, fg_color="#1a1b26", border_color="#2d2e37", border_width=1, height=50, corner_radius=8)
alt_bar.pack(fill="x", padx=40, pady=(10, 30))

lbl_dosya_adi = ctk.CTkLabel(alt_bar, text="bir ses dosyası seçin...", text_color="#565f89", font=("Segoe UI", 11, "italic"))
lbl_dosya_adi.pack(side="left", padx=20)

btn_sec = ctk.CTkButton(
    alt_bar, text="DOSYA SEÇ", width=90, height=30, corner_radius=6,
    fg_color="#7aa2f7", hover_color="#3d59a1", text_color="#1a1b26", font=("Segoe UI", 11, "bold"),
    command=dosya_secici
)
btn_sec.pack(side="right", padx=10)
app.mainloop()
