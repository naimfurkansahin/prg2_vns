#TODO
import customtkinter as ctk

app = ctk.CTk()
app.geometry("800x800")
app.title("VNS: Akıllı Ses Deşifre Sistemi      ")
ana_baslik = ctk.CTkLabel(
    app, 
    text="VNS SES ANALİZ SİSTEMİ", 
    text_color="#708090", 
    font=("Consolas", 15, "bold"),
    width=600,
    
    anchor="center"
)
ana_baslik.pack(pady=15)
app.mainloop()