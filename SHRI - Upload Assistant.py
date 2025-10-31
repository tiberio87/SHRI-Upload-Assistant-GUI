import os
import subprocess
import shutil
import json
import re
import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter as tk

# === Tooltip ===
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 30
        y = self.widget.winfo_rooty() + 20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify="left", background="#333333", foreground="white", relief="solid", borderwidth=1, font=("Arial", 12))
        label.pack(ipadx=6, ipady=3)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

# === Dialog personalizzati ===
class CTkYesNoDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x180")
        self.resizable(False, False)
        self.result = False

        ctk.CTkLabel(self, text=message, wraplength=350).pack(pady=(30, 20))
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Sì", command=self.yes).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="No", command=self.no).pack(side="right", padx=10)

        self.grab_set()
        self.wait_window()

    def yes(self):
        self.result = True
        self.destroy()

    def no(self):
        self.result = False
        self.destroy()

# === CREAZIONE CONFIGURAZIONE ===
CONFIG_FILE = "config.txt"
selected_path = ""

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Upload Assistant GUI")
app.geometry("600x800")
app.resizable(True, True)

status_label = ctk.CTkLabel(app, text="", text_color="green")
status_label.pack(pady=10)

progress_bar = ctk.CTkProgressBar(app, width=400)
progress_bar.set(0)
progress_bar.pack(pady=(10, 0))
progress_bar.pack_forget()

# === FUNZIONI DI CONFIGURAZIONE ===
def save_config(bot_path: str, venv_path: str) -> None:
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(f"{bot_path}\n{venv_path}")

def load_config() -> tuple[str | None, str | None]:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
            if len(lines) >= 2:
                return lines[0], lines[1]
    return None, None

def resolve_activate_path(base_path):
    direct = os.path.join(base_path, "activate.bat")
    in_scripts = os.path.join(base_path, "Scripts", "activate.bat")
    if os.path.exists(direct):
        return direct
    elif os.path.exists(in_scripts):
        return in_scripts
    return None

def ask_for_paths():
    messagebox.showinfo("Configurazione manuale", "Seleziona la cartella dove si trova il BOT.")
    bot_path = filedialog.askdirectory(title="Cartella del bot Upload Assistant")
    if not bot_path:
        messagebox.showerror("Errore", "Devi selezionare la cartella del bot.")
        app.destroy()
        exit()

    messagebox.showinfo("Configurazione manuale", "Ora seleziona la cartella del virtual environment (es: venv o Scripts).")
    venv_path = filedialog.askdirectory(title="Cartella del virtual environment o 'Scripts'")
    activate_path = resolve_activate_path(venv_path)

    if not venv_path or not activate_path:
        messagebox.showerror("Errore", "Cartella virtual environment non valida.")
        app.destroy()
        exit()

    save_config(bot_path, venv_path)
    return bot_path, venv_path

def patch_config(content: str, keys: dict) -> str:
    content = re.sub(r'"tmdb_api"\s*:\s*".*?"', f'"tmdb_api": "{keys.get("tmdb_api", "")}"', content)
    content = re.sub(r'"tvdb_api"\s*:\s*".*?"', f'"tvdb_api": "{keys.get("tvdb_api", "")}"', content)
    content = re.sub(r'"tvdb_token"\s*:\s*".*?"', f'"tvdb_token": "{keys.get("tvdb_token", "")}"', content)
    content = re.sub(r'"imgbb_api"\s*:\s*".*?"', f'"imgbb_api": "{keys.get("imgbb_api", "")}"', content)
    content = re.sub(r'"tone_map"\s*:\s*True', '"tone_map": False', content)
    content = re.sub(r'(\"SHRI\"\s*:\s*\{.*?)("api_key"\s*:\s*").*?(\")', r'\1\2' + keys.get("shri_api", "") + r'\3', content, flags=re.DOTALL)
    content = content.replace('"add_logo": False', '"add_logo": True')
    content = content.replace('"logo_language": ""', '"logo_language": "it"')
    content = content.replace('"img_host_1": ""', '"img_host_1": "ptscreens"')
    content = content.replace('"img_host_2": ""', '"img_host_2": "imgbox"')
    content = content.replace('"screens": "4"', '"screens": "6"')
    content = content.replace('"multiScreens": "2"', '"multiScreens": "0"')
    content = content.replace('"search_requests": "False"', '"search_requests": "True"')
    content = content.replace('"use_italian_title": False', '"use_italian_title": True')
    return content

def setup_from_local():
    """Setup usando una copia locale di SHRI-Upload-Assistant-GUI.

    Comportamento:
    - Se la sottocartella 'Upload-Assistant' è presente nella stessa cartella dello script,
      offre all'utente di usarla automaticamente.
    - Altrimenti, chiede all'utente di selezionare la cartella root dove si trova
      'Upload-Assistant'.
    Restituisce (bot_path, venv_path).
    """
    progress_bar.pack(pady=(10, 0))
    progress_bar.set(0.0)
    status_label.configure(text="🔍 Preparazione setup locale...", text_color="yellow")
    app.update()

    repo_root = os.path.abspath(os.path.dirname(__file__))
    detected_bot = os.path.join(repo_root, "Upload-Assistant")

    bot_path = None
    # Se troviamo Upload-Assistant nella stessa repo, chiediamo se usarla
    if os.path.exists(detected_bot) and os.path.isdir(detected_bot):
        dialog = CTkYesNoDialog(app, "Cartella trovata", f"Ho trovato Upload-Assistant in:\n{detected_bot}\nVuoi usarla per il setup?")
        if dialog.result:
            bot_path = detected_bot

    if not bot_path:
        # chiedi all'utente la root dove è clonato 'SHRI-Upload-Assistant-GUI'
        messagebox.showinfo("Setup automatico", "Seleziona la cartella root del progetto 'SHRI-Upload-Assistant-GUI' (dovrebbe contenere la sottocartella Upload-Assistant).")
        target_dir = filedialog.askdirectory(title="Cartella root SHRI-Upload-Assistant-GUI")
        if not target_dir:
            messagebox.showerror("Errore", "Cartella non selezionata. Impossibile continuare.")
            app.destroy()
            exit()

        candidate = os.path.join(target_dir, "Upload-Assistant")
        if not os.path.exists(candidate) or not os.path.isdir(candidate):
            messagebox.showerror("Errore", "Non ho trovato la cartella 'Upload-Assistant' nella root selezionata. Assicurati di aver clonato 'tiberio87/SHRI-Upload-Assistant-GUI'.")
            app.destroy()
            exit()
        bot_path = candidate

    progress_bar.set(0.2)
    app.update()
    venv_path = os.path.join(bot_path, ".venv")

    status_label.configure(text="🔧 Creazione ambiente virtuale...", text_color="yellow")
    app.update()
    subprocess.run(f'python -m venv "{venv_path}"', shell=True)

    progress_bar.set(0.4)
    app.update()

    activate_path = resolve_activate_path(venv_path)
    if not activate_path:
        messagebox.showerror("Errore", "Virtual environment non trovato.")
        app.destroy()
        exit()

    status_label.configure(text="⚙️ Configurazione file...", text_color="yellow")
    app.update()

    example_cfg = os.path.join(bot_path, "data", "example-config.py")
    target_cfg = os.path.join(bot_path, "data", "config.py")

    keys_file = "api_keys.json"
    if not os.path.exists(keys_file):
        messagebox.showerror("Errore", "File api_keys.json mancante! Impossibile proseguire.")
        app.destroy()
        exit()

    try:
        with open(keys_file, "r", encoding="utf-8") as f:
            keys = json.load(f)

        with open(example_cfg, "r", encoding="utf-8") as f:
            content = f.read()

        content = patch_config(content, keys)

        with open(target_cfg, "w", encoding="utf-8") as f:
            f.write(content)

    except Exception as e:
        messagebox.showerror("Errore", f"Errore leggendo o modificando api_keys.json:\n{e}")
        app.destroy()
        exit()

    progress_bar.set(0.7)
    app.update()

    status_label.configure(text="📦 Installazione dipendenze...", text_color="yellow")
    app.update()
    subprocess.run(f'cmd.exe /c "cd /d \"{bot_path}\" && call \"{activate_path}\" && pip install -r requirements.txt"', shell=True)

    progress_bar.set(1.0)
    status_label.configure(text="✅ Setup completato!", text_color="green")
    app.update()

    save_config(bot_path, venv_path)
    progress_bar.pack_forget()
    app.update()

    return bot_path, venv_path
    
# === INIZIO APPLICAZIONE ===
def get_valid_paths() -> tuple[str, str]:
    temp_bot_path, temp_venv_path = load_config()
    
    if not temp_bot_path or not temp_venv_path or not resolve_activate_path(temp_venv_path):
        dialog = CTkYesNoDialog(app, "Setup iniziale", "Il bot non è ancora configurato. Vuoi eseguire il setup automatico?")
        if dialog.result:
            return setup_from_local()
        else:
            return ask_for_paths()
    return temp_bot_path, temp_venv_path

bot_path, venv_path = get_valid_paths()
activate_path = resolve_activate_path(venv_path)
assert activate_path is not None, "Percorso di attivazione non trovato"

# === FUNZIONI APPLICAZIONE ===
def select_path():
    global selected_path
    release_type = release_option.get()

    path = None
    if release_type in ["Film (MKV)", "Serie (Episodio)"]:
        path = filedialog.askopenfilename(filetypes=[("MKV files", "*.mkv")])
    elif release_type in ["Serie (Stagione)", "Film (Disco)"]:
        path = filedialog.askdirectory(title=f"Seleziona una cartella per: {release_type}")

    if path:
        selected_path = path
        path_label.configure(text=os.path.basename(path))
    else:
        selected_path = ""
        path_label.configure(text="Nessuna selezione")

def open_config_py():
    config_path = os.path.join(bot_path, "data", "config.py")
    if not os.path.exists(config_path):
        messagebox.showerror("Errore", "Il file config.py non esiste.")
        return

    try:
        # Proviamo ad aprire con Notepad++
        subprocess.Popen(r'"C:\Program Files\Notepad++\notepad++.exe" "' + config_path + '"')
    except FileNotFoundError:
        # Se Notepad++ non è trovato, ripiega su Notepad
        subprocess.Popen(f'notepad.exe "{config_path}"')
    except Exception as e:
        messagebox.showerror("Errore", f"Impossibile aprire config.py\n{e}")

def run_git_pull():
    progress_bar.set(0.0)
    status_label.configure(text="🔄 Controllo aggiornamenti Bot...", text_color="yellow")
    app.update()
    full_cmd = f'start cmd.exe /k "cd /d \"{bot_path}\" && call \"{activate_path}\" && git pull"'
    subprocess.Popen(full_cmd, shell=True)
    progress_bar.set(1.0)

def run_pip_install():
    progress_bar.set(0.0)
    status_label.configure(text="🔄 Controllo aggiornamenti pip...", text_color="yellow")
    app.update()
    full_cmd = f'start cmd.exe /k "cd /d \"{bot_path}\" && call \"{activate_path}\" && pip install -r requirements.txt"'
    subprocess.Popen(full_cmd, shell=True)
    progress_bar.set(1.0)

def run_upload():
    if not selected_path or not os.path.exists(selected_path):
        status_label.configure(text="❌ Percorso non valido", text_color="red")
        return

    tracker = tracker_option.get().strip().upper()
    imdb_id = imdb_entry.get().strip()
    tmdb_id = tmdb_entry.get().strip()
    tag_value = tag_entry.get().strip()
    service_value = service_entry.get().strip()
    edition_value = edition_entry.get().strip()

    upload_cmd = f'python upload.py "{selected_path}" --skip_auto_torrent --no-seed --trackers {tracker} --cleanup'

    if imdb_id:
        upload_cmd += f" --imdb {imdb_id}"
    if tmdb_id:
        upload_cmd += f" --tmdb {tmdb_id}"
    if tag_value:
        upload_cmd += f" --tag {tag_value}"
    if service_value:
        upload_cmd += f" --service {service_value}"
    if edition_value:
        upload_cmd += f" --edition {edition_value}"

    full_cmd = f'start cmd.exe /k "cd /d \"{bot_path}\" && call \"{activate_path}\" && {upload_cmd}"'
    subprocess.Popen(full_cmd, shell=True)
    status_label.configure(text="✅ Upload avviato...", text_color="green")

# === LAYOUT ===
ctk.CTkLabel(app, text="Tipo di rilascio").pack(pady=(15, 0))
release_option = ctk.CTkComboBox(app, values=["Film (MKV)",  "Film (Disco)", "Serie (Episodio)", "Serie (Stagione)"], width=180)
release_option.set("")
release_option.pack(pady=5)
ToolTip(release_option, "Scegli se caricare:\n- un film (singolo file)\n- un episodio\n- un'intera stagione (cartella)\n- una cartella BluRay (es. BDMV)")

select_btn = ctk.CTkButton(app, text="Seleziona", command=select_path)
select_btn.pack(pady=5)
ToolTip(select_btn, "Seleziona un file .mkv o una cartella a seconda del tipo scelto.")

path_label = ctk.CTkLabel(app, text="Nessuna selezione")
path_label.pack(pady=5)

ctk.CTkLabel(app, text="Tracker").pack(pady=(10, 0))
tracker_option = ctk.CTkComboBox(app, values=["SHRI"], width=120)
tracker_option.set("")
tracker_option.pack(pady=5)
ToolTip(tracker_option, "Seleziona il tracker dove vuoi caricare il file.")

imdb_entry = ctk.CTkEntry(app, placeholder_text="IMDb ID (opzionale)", width=240)
imdb_entry.pack(pady=5)
ToolTip(imdb_entry, "Inserisci l'ID IMDb (opzionale) da imdb.com\nEsempio: tt0068646 per Il Padrino.")

tmdb_entry = ctk.CTkEntry(app, placeholder_text="TMDB ID (opzionale)", width=240)
tmdb_entry.pack(pady=5)
ToolTip(tmdb_entry, "Inserisci l'ID TMDB (opzionale) da TMDB.org\nEsempio: 550 per Fight Club.")

tag_entry = ctk.CTkEntry(app, placeholder_text="TAG gruppo (opzionale)", width=240)
tag_entry.pack(pady=5)
ToolTip(tag_entry, "Inserisci TAG della Crew (opzionale)\nEsempio: G66, iSlaNd, LFi")

service_entry = ctk.CTkEntry(app, placeholder_text="Piattaforma di streaming (opzionale)", width=240)
service_entry.pack(pady=5)
ToolTip(service_entry, "Inserisci un nome servizio per il rilascio\n(es. NF, AMZN, ATVP, DSNP, NOW).")

edition_entry = ctk.CTkEntry(app, placeholder_text="Aggiungi edizione (opzionale)", width=240)
edition_entry.pack(pady=5)
ToolTip(edition_entry, "Inserisci una versione speciale del film (opzionale).\nEsempio: HYBRID, Extended, Remastered, Director's Cut.")

upload_btn = ctk.CTkButton(app, text="Upload", command=run_upload)
upload_btn.pack(pady=10)
ToolTip(upload_btn, "Avvia il comando di upload con i parametri selezionati.")

git_btn = ctk.CTkButton(app, text="Controlla aggiornamenti BOT", command=run_git_pull, fg_color="green", hover_color="darkgreen", text_color="white")
git_btn.pack(pady=5)
ToolTip(git_btn, "Esegui un git pull per aggiornare lo script all'ultima versione.")

pip_btn = ctk.CTkButton(app, text="Controlla aggiornamenti dipendenze", command=run_pip_install, fg_color="green", hover_color="darkgreen", text_color="white")
pip_btn.pack(pady=5)
ToolTip(pip_btn, "Esegui pip install per aggiornare le dipendenze del progetto.")

config_btn = ctk.CTkButton(app, text="Modifica Config.py", command=open_config_py, fg_color="blue", hover_color="darkblue", text_color="white")
config_btn.pack(pady=5)
ToolTip(config_btn, "Apri il file config.py per modificare la configurazione del bot.")

progress_bar = ctk.CTkProgressBar(app, width=400)
progress_bar.set(0)
progress_bar.pack(pady=(10, 0))

status_label = ctk.CTkLabel(app, text="", text_color="green")
status_label.pack(pady=10)

ctk.CTkLabel(app, text="Authors: Tiberio87").pack(pady=5)

app.mainloop()
