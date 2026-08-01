import os
import subprocess
import sys
import json
import platform
import glob
import shutil
import urllib.request
import urllib.error
import threading
import tempfile
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font, simpledialog

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    from pypresence import Presence
    HAS_PYPRESENCE = True
except ImportError:
    HAS_PYPRESENCE = False

VERSION = "1.1-Release"
GITHUB_REPO = "Menwey/KoroneSnowStrap"
DISCORD_CLIENT_ID = "1532801354010071050"
PEKORA_VERSION_HASH = "version-cde8fee1a1e747d4"
PEKORA_2020L_FOLDER = "2020L"
PEKORA_2021M_FOLDER = "2021M"
PEKORA_FONTS_SUBPATH = os.path.join("content", "fonts")
PEKORA_TEXT_SUBPATH = os.path.join("content", "textures")
LOGO_URL = "https://github.com/Menwey/KoroneSnowStrap/blob/main/assets/imazge.png?raw=true"
ICON_URL = "https://raw.githubusercontent.com/Menwey/KoroneSnowStrap/refs/heads/main/assets/image.ico"
Yagey_dir = os.path.expandvars(r"%appdata%\krnstrapsettings")
SETTINGS_FILE = os.path.join(Yagey_dir, "config.json")

THEMES = {
    "Snow": {"bg": "#2e3440", "surface": "#3b4252", "border": "#4c566a", "accent": "#88c0d0", "text": "#eceff4", "muted": "#616e88", "active_text": "#2e3440"},
    "Cyberpunk": {"bg": "#000505", "surface": "#001a1a", "border": "#00f2ff", "accent": "#00f2ff", "text": "#00f2ff", "muted": "#006666", "active_text": "#000000"},
    "Crimson": {"bg": "#0d0000", "surface": "#1a0000", "border": "#ff0000", "accent": "#ff3333", "text": "#ffe0e0", "muted": "#660000", "active_text": "#ffffff"},
    "Void": {"bg": "#000000", "surface": "#080808", "border": "#121212", "accent": "#ffffff", "text": "#e0e0e0", "muted": "#444444", "active_text": "#000000"},
    "Sakura": {"bg": "#1a1012", "surface": "#2d1b1e", "border": "#4a2c31", "accent": "#ffb7c5", "text": "#ffeef0", "muted": "#855a62", "active_text": "#1a1012"},
    "Oceanic": {"bg": "#011627", "surface": "#0b2942", "border": "#1d3b53", "accent": "#2ec4b6", "text": "#fdfffc", "muted": "#5f7e97", "active_text": "#011627"},
    "Midnight Gold": {"bg": "#0a0a0a", "surface": "#141414", "border": "#262626", "accent": "#d4af37", "text": "#ffffff", "muted": "#555555", "active_text": "#000000"},
    "Purple": {"bg": "#0a0014", "surface": "#16002b", "border": "#2d0052", "accent": "#b366ff", "text": "#f2e6ff", "muted": "#7d6a96", "active_text": "#f2e6ff"},
    "Emerald": {"bg": "#000803", "surface": "#001207", "border": "#00ff62", "accent": "#00ff62", "text": "#d4ffdf", "muted": "#004d1e", "active_text": "#000000"}
}


def load_user_settings():
    default_settings = {
        "theme": "Snow",
        "rpc_enabled": True,
        "last_client": PEKORA_2021M_FOLDER
    }
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                default_settings.update(data)
        except Exception:
            pass
    return default_settings


def save_user_settings(settings):
    try:
        os.makedirs(Yagey_dir, exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
    except Exception:
        pass


def check_for_updates(parent_window):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "KoroneSnowStrap-Updater"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                latest = data.get("tag_name", "").lstrip("v").strip()
                if latest and latest != VERSION:
                    is_exe = sys.argv[0].endswith(".exe")
                    target_url = None
                    
                    if is_exe:
                        for asset in data.get("assets", []):
                            name = asset.get("name", "")
                            if name.lower() == "koronesnowstrap.exe":
                                target_url = asset.get("browser_download_url")
                                break
                    else:
                        target_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/voidstrap.py"

                    if target_url:
                        parent_window.after(0, lambda: _prompt_update(latest, target_url))
    except Exception:
        pass


def _prompt_update(new_ver, download_url):
    if messagebox.askyesno("Update Available", f"New version {new_ver} is available!\nDo you want to update now?"):
        try:
            current_file = os.path.abspath(sys.argv[0])
            is_exe = current_file.endswith(".exe")
            
            if is_exe:
                temp_file = os.path.join(tempfile.gettempdir(), "KoroneSnowStrap_new.exe")
                urllib.request.urlretrieve(download_url, temp_file)
                
                if os.path.getsize(temp_file) < 1000000:
                    raise ValueError("Downloaded EXE binary is corrupted or incomplete.")

                bat_script = os.path.join(tempfile.gettempdir(), "update_korone.bat")
                with open(bat_script, "w") as f:
                    f.write(
                        '@echo off\n'
                        'timeout /t 2 /nobreak > nul\n'
                        f'move /y "{temp_file}" "{current_file}"\n'
                        f'start "" "{current_file}"\n'
                        'del "%~f0"\n'
                    )
                subprocess.Popen([bat_script], shell=True)
                sys.exit(0)
            else:
                script_name = os.path.basename(current_file)
                temp_file = os.path.join(tempfile.gettempdir(), f"temp_{script_name}")
                urllib.request.urlretrieve(download_url, temp_file)
                
                with open(temp_file, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if "class KoroneSnowStrap" not in content and "import tkinter" not in content:
                        raise ValueError("Downloaded script is invalid!")

                shutil.move(temp_file, current_file)
                messagebox.showinfo("Success", "Updated! Restarting application...")
                subprocess.Popen([sys.executable, current_file])
                sys.exit(0)
        except Exception as err:
            messagebox.showerror("Update Error", f"Failed to update: {err}")


def rpc_standalone_worker(client_name):
    if not HAS_PYPRESENCE:
        return

    def is_game_running():
        if platform.system() == "Windows":
            try:
                output = subprocess.check_output('tasklist /FI "IMAGENAME eq ProjectXPlayerBeta.exe"', shell=True).decode("utf-8", errors="ignore")
                return "ProjectXPlayerBeta.exe" in output
            except Exception:
                return False
        return True

    time.sleep(3)

    try:
        RPC = Presence(DISCORD_CLIENT_ID)
        RPC.connect()
        start_time = time.time()
        
        RPC.update(
            state="In Main Menu / Playing",
            details=f"Playing on Client {client_name}",
            start=start_time,
            large_image="korone_logo",
            large_text="KoroneSnowStrap Client",
            small_image="korone_logo",
            small_text="Korone Client"
        )

        while is_game_running():
            time.sleep(5)

        RPC.close()
    except Exception:
        pass


def launch_detached_rpc(client_name):
    script_path = os.path.abspath(sys.argv[0])
    creation_flags = subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
    subprocess.Popen([sys.executable, script_path, "--rpc-worker", client_name], creationflags=creation_flags)


def download_resource(url, filename):
    path = os.path.join(tempfile.gettempdir(), filename)
    if not os.path.exists(path):
        try:
            urllib.request.urlretrieve(url, path)
        except Exception:
            return None
    return path


def get_version_roots():
    paths = [
        os.path.expandvars(r"%localappdata%\ProjectX\Versions"),
        os.path.expandvars(r"%localappdata%\Pekora\Versions")
    ]
    return [p for p in set(paths) if os.path.isdir(p)]


def iter_version_dirs():
    for root in get_version_roots():
        for folder in sorted(glob.glob(os.path.join(root, "*"))):
            if os.path.isdir(folder):
                yield folder


def get_executable_paths(folder_name):
    return [os.path.join(v, folder_name, "ProjectXPlayerBeta.exe") for v in iter_version_dirs()]


def load_fastflags(client_folder):
    filename = f"fastFlags_{client_folder}.json"
    flags = {}
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                flags = json.load(f)
        except Exception:
            flags = {}
            
    if "DFIntTaskSchedulerTargetFps" not in flags:
        flags["DFIntTaskSchedulerTargetFps"] = "120"
        save_fastflags(client_folder, flags)
        
    return flags


def save_fastflags(client_folder, flags):
    filename = f"fastFlags_{client_folder}.json"
    with open(filename, "w") as f:
        json.dump(flags, f, indent=2)


def apply_fastflags():
    for client_folder in [PEKORA_2020L_FOLDER, PEKORA_2021M_FOLDER]:
        flags = load_fastflags(client_folder)
        for ver_dir in iter_version_dirs():
            target_path = os.path.join(ver_dir, client_folder)
            if os.path.isdir(target_path):
                Yagey_dir = os.path.join(target_path, "ClientSettings")
                os.makedirs(Yagey_dir, exist_ok=True)
                file_path = os.path.join(Yagey_dir, "ClientAppSettings.json")
                with open(file_path, "w") as f:
                    json.dump(flags, f, indent=2)


class ClientLoader(tk.Toplevel):
    def __init__(self, parent, logo, theme):
        super().__init__(parent)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.bg_color = theme["bg"]
        self.accent_color = theme["accent"]
        self.configure(bg=self.bg_color)
        
        width, height = 420, 280
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        pos_x = (screen_w - width) // 2
        pos_y = (screen_h - height) // 2
        self.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

        if logo:
            tk.Label(self, image=logo, bg=self.bg_color).pack(pady=(40, 15))

        tk.Label(self, text="STARTING CLIENT", font=("Consolas", 14, "bold"), fg=theme["text"], bg=self.bg_color).pack()
        self.status = tk.Label(self, text="Preparing session...", font=("Consolas", 10), fg=theme["muted"], bg=self.bg_color)
        self.status.pack(pady=(10, 25))

        self.progress = tk.Canvas(self, width=300, height=4, bg=theme["surface"], highlightthickness=0)
        self.progress.pack()
        self.bar = self.progress.create_rectangle(-100, 0, 0, 4, fill=self.accent_color, outline="")
        self.pos = -100
        self.animate()

    def animate(self):
        if not self.winfo_exists():
            return
        self.pos += 4
        if self.pos > 300:
            self.pos = -100
        try:
            self.progress.coords(self.bar, self.pos, 0, self.pos + 100, 4)
            self.after(16, self.animate)
        except Exception:
            pass


class KoroneSnowStrap(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("KoroneSnowStrap")
        self.geometry("880x520")
        self.resizable(False, False)

        self.user_settings = load_user_settings()
        selected_theme = self.user_settings.get("theme", "Snow")
        self.theme = THEMES.get(selected_theme, THEMES["Snow"])

        self.f_main = font.Font(family="Consolas", size=10)
        self.f_lg = font.Font(family="Consolas", size=13, weight="bold")
        self.f_xl = font.Font(family="Consolas", size=15, weight="bold")
        self.f_sm = font.Font(family="Consolas", size=9)

        self._load_resources()
        self._build_ui()

        threading.Thread(target=check_for_updates, args=(self,), daemon=True).start()

    def update_user_setting(self, key, value):
        self.user_settings[key] = value
        save_user_settings(self.user_settings)

    def _load_resources(self):
        logo_path = download_resource(LOGO_URL, "kstrap_logo.jpg")
        self.logo_img = None
        if logo_path and HAS_PIL:
            try:
                img = Image.open(logo_path).resize((120, 120), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(img)
            except Exception:
                pass

        icon_path = download_resource(ICON_URL, "kstrap_icon.ico")
        if icon_path and platform.system().lower() == "windows":
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

    def _build_ui(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.configure(bg=self.theme["bg"])
        self.sidebar = tk.Frame(self, bg=self.theme["surface"], width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        if self.logo_img:
            tk.Label(self.sidebar, image=self.logo_img, bg=self.theme["surface"]).pack(pady=20)

        self.content = tk.Frame(self, bg=self.theme["bg"])
        self.content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        navigation = [
            ("launch", "▶  Launch"),
            ("fastflags", "⚙  FastFlags"),
            ("editfont", "✎  Fonts"),
            ("editcursor", "🖱  Cursor"),
            ("appearance", "🎨  Design"),
            ("credits", "★  Credits")
        ]

        self._btns = {}
        for key, label in navigation:
            btn = tk.Button(
                self.sidebar, text=label, font=self.f_main, anchor="w", padx=20,
                bg=self.theme["surface"], fg=self.theme["muted"], bd=0, relief=tk.FLAT,
                cursor="hand2", activebackground=self.theme["accent"],
                command=lambda k=key: self.show(k)
            )
            btn.pack(fill=tk.X, pady=2)
            self._btns[key] = btn

        self.pages = {
            "launch": LaunchPage(self.content, self),
            "fastflags": FastFlagsPage(self.content, self),
            "editfont": EditFontPage(self.content, self),
            "editcursor": EditCursorPage(self.content, self),
            "appearance": AppearancePage(self.content, self),
            "credits": CreditsPage(self.content, self)
        }

        for page in self.pages.values():
            page.place(relwidth=1, relheight=1)

        self.show("launch")

    def show(self, key):
        for k, btn in self._btns.items():
            active = (k == key)
            btn.configure(
                bg=self.theme["accent"] if active else self.theme["surface"],
                fg=self.theme["active_text"] if active else self.theme["muted"]
            )
        self.pages[key].tkraise()
        self.pages[key].on_show()

    def change_theme(self, name):
        self.theme = THEMES[name]
        self.update_user_setting("theme", name)
        self._build_ui()
        self.show("appearance")


class BasePage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=app.theme["bg"])
        self.app = app

    def on_show(self):
        pass

    def _title(self, title_text, subtitle_text=""):
        header = tk.Frame(self, bg=self.app.theme["bg"])
        header.pack(fill=tk.X, padx=24, pady=(20, 0))
        tk.Label(header, text=title_text, font=self.app.f_xl, fg=self.app.theme["text"], bg=self.app.theme["bg"]).pack(anchor="w")

        if subtitle_text:
            tk.Label(header, text=subtitle_text, font=self.app.f_sm, fg=self.app.theme["muted"], bg=self.app.theme["bg"]).pack(anchor="w")

        tk.Frame(self, bg=self.app.theme["border"], height=1).pack(fill=tk.X, padx=24, pady=(8, 20))

    def _btn(self, parent, text, command, color=None):
        bg_color = color if color else self.app.theme["accent"]
        return tk.Button(
            parent, text=text, font=self.app.f_main, bg=bg_color, fg=self.app.theme["active_text"],
            relief=tk.FLAT, bd=0, padx=15, pady=8, cursor="hand2", command=command
        )


class LaunchPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        saved_rpc = self.app.user_settings.get("rpc_enabled", True)
        self.rpc_enabled = tk.BooleanVar(value=saved_rpc)

    def _on_rpc_toggle(self):
        self.app.update_user_setting("rpc_enabled", self.rpc_enabled.get())

    def on_show(self):
        for widget in self.winfo_children():
            widget.destroy()

        self._title("Launch")
        container = tk.Frame(self, bg=self.app.theme["bg"])
        container.pack(fill=tk.X, padx=24)

        clients = [
            ("2021M", PEKORA_2021M_FOLDER),
            ("2020L", PEKORA_2020L_FOLDER)
        ]

        for year, folder in clients:
            card = tk.Frame(container, bg=self.app.theme["surface"], padx=20, pady=20)
            card.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.BOTH)

            tk.Label(card, text=f"Client {year}", font=self.app.f_lg, fg=self.app.theme["text"], bg=self.app.theme["surface"]).pack(anchor="w")
            tk.Label(card, text="Standard play mode", font=self.app.f_sm, fg=self.app.theme["muted"], bg=self.app.theme["surface"]).pack(anchor="w", pady=(0, 15))

            self._btn(card, "▶ Launch", lambda f=folder, y=year: self._start(f, y)).pack(fill=tk.X)

        options_card = tk.Frame(self, bg=self.app.theme["surface"], padx=20, pady=15)
        options_card.pack(fill=tk.X, padx=34, pady=20)

        tk.Label(options_card, text="Launch Settings", font=self.app.f_lg, fg=self.app.theme["text"], bg=self.app.theme["surface"]).pack(anchor="w", pady=(0, 10))

        rpc_check = tk.Checkbutton(
            options_card, text="Enable Native Discord RPC Integration", variable=self.rpc_enabled,
            font=self.app.f_main, fg=self.app.theme["text"], bg=self.app.theme["surface"],
            activebackground=self.app.theme["surface"], activeforeground=self.app.theme["text"],
            selectcolor=self.app.theme["bg"], bd=0, cursor="hand2",
            command=self._on_rpc_toggle
        )
        rpc_check.pack(anchor="w")

    def _start(self, folder, client_name):
        executables = get_executable_paths(folder)
        target_exe = next((p for p in executables if os.path.isfile(p)), None)

        if not target_exe:
            messagebox.showerror("Error", "Client not found!")
            return

        loader = ClientLoader(self.app, self.app.logo_img, self.app.theme)

        def runner():
            apply_fastflags()
            subprocess.Popen([target_exe, "--app"])

            if self.rpc_enabled.get():
                launch_detached_rpc(client_name)

            time.sleep(4)
            if loader.winfo_exists():
                self.app.after(0, loader.destroy)

        threading.Thread(target=runner, daemon=True).start()


class FastFlagsPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        saved_ver = self.app.user_settings.get("last_client", PEKORA_2021M_FOLDER)
        self.selected_ver = tk.StringVar(value=saved_ver)

    def on_show(self):
        for widget in self.winfo_children():
            widget.destroy()

        self._title("FastFlags Settings")

        switch_frame = tk.Frame(self, bg=self.app.theme["bg"])
        switch_frame.pack(fill=tk.X, padx=24, pady=(0, 10))

        for text, value in [("2021 Client", PEKORA_2021M_FOLDER), ("2020 Client", PEKORA_2020L_FOLDER)]:
            selected = (value == self.selected_ver.get())
            tk.Button(
                switch_frame, text=text, font=self.app.f_main,
                bg=self.app.theme["accent"] if selected else self.app.theme["surface"],
                fg=self.app.theme["active_text"] if selected else self.app.theme["text"],
                bd=0, padx=15, pady=4, cursor="hand2",
                command=lambda v=value: self._set_version(v)
            ).pack(side=tk.LEFT, padx=2)

        fps_card = tk.Frame(self, bg=self.app.theme["surface"], padx=15, pady=10)
        fps_card.pack(fill=tk.X, padx=24, pady=(0, 10))

        tk.Label(
            fps_card, 
            text="⚡ Quick FPS Limit:", 
            font=self.app.f_main, 
            fg=self.app.theme["text"], 
            bg=self.app.theme["surface"]
        ).pack(side=tk.LEFT, padx=(0, 10))

        current_flags = load_fastflags(self.selected_ver.get())
        current_fps = str(current_flags.get("DFIntTaskSchedulerTargetFps", "120"))

        fps_presets = [("60 (Lock)", "60"), ("120 FPS", "120"), ("144 FPS", "144"), ("240 FPS", "240"), ("360 FPS", "360")]
        for label, fps_val in fps_presets:
            is_active = (current_fps == fps_val)
            tk.Button(
                fps_card, text=label, font=self.app.f_sm,
                bg=self.app.theme["accent"] if is_active else self.app.theme["bg"],
                fg=self.app.theme["active_text"] if is_active else self.app.theme["text"],
                bd=0, padx=10, pady=3, cursor="hand2",
                command=lambda v=fps_val: self._set_fps(v)
            ).pack(side=tk.LEFT, padx=3)

        toolbar = tk.Frame(self, bg=self.app.theme["bg"])
        toolbar.pack(fill=tk.X, padx=24, pady=5)
        self._btn(toolbar, "+ Add Flag", self._add_flag).pack(side=tk.LEFT, padx=(0, 5))
        self._btn(toolbar, "📝 Edit Raw JSON", self._edit_json, color=self.app.theme["surface"]).pack(side=tk.LEFT)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background=self.app.theme["surface"], foreground=self.app.theme["text"], fieldbackground=self.app.theme["surface"], borderwidth=0)
        style.map("Treeview", background=[("selected", self.app.theme["accent"])])

        self.tree = ttk.Treeview(self, columns=("K", "V"), show="headings", height=8)
        self.tree.heading("K", text="Flag Name")
        self.tree.heading("V", text="Value")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=24, pady=10)

        flags = load_fastflags(self.selected_ver.get())
        for key, val in flags.items():
            self.tree.insert("", "end", values=(key, val))

    def _set_version(self, ver):
        self.selected_ver.set(ver)
        self.app.update_user_setting("last_client", ver)
        self.on_show()

    def _set_fps(self, fps_value):
        flags = load_fastflags(self.selected_ver.get())
        flags["DFIntTaskSchedulerTargetFps"] = str(fps_value)
        save_fastflags(self.selected_ver.get(), flags)
        self.on_show()

    def _add_flag(self):
        key = simpledialog.askstring("Add Flag", "Flag Key:")
        value = simpledialog.askstring("Add Flag", "Value:")

        if key:
            flags = load_fastflags(self.selected_ver.get())
            flags[key] = str(value)
            save_fastflags(self.selected_ver.get(), flags)
            self.on_show()

    def _edit_json(self):
        editor = tk.Toplevel(self)
        editor.title(f"JSON Editor ({self.selected_ver.get()})")
        editor.geometry("550x450")
        editor.configure(bg=self.app.theme["bg"])

        text_area = tk.Text(editor, bg=self.app.theme["surface"], fg=self.app.theme["text"], font=("Consolas", 10), bd=0, padx=10, pady=10)
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))

        current_flags = load_fastflags(self.selected_ver.get())
        text_area.insert("1.0", json.dumps(current_flags, indent=2))

        def save_json():
            try:
                parsed = json.loads(text_area.get("1.0", tk.END))
                save_fastflags(self.selected_ver.get(), parsed)
                editor.destroy()
                self.on_show()
            except Exception as e:
                messagebox.showerror("Invalid JSON", f"Syntax error:\n{e}")

        btn_frame = tk.Frame(editor, bg=self.app.theme["bg"])
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        self._btn(btn_frame, "Save JSON", save_json).pack()


class AppearancePage(BasePage):
    def on_show(self):
        for widget in self.winfo_children():
            widget.destroy()

        self._title("Design Settings")
        grid = tk.Frame(self, bg=self.app.theme["bg"])
        grid.pack(fill=tk.BOTH, expand=True, padx=24)

        for i, (name, theme_data) in enumerate(THEMES.items()):
            card = tk.Frame(grid, bg=self.app.theme["surface"], padx=10, pady=10)
            card.grid(row=i // 3, column=i % 3, padx=5, pady=5, sticky="nsew")

            tk.Label(card, text=name, font=self.app.f_main, fg=theme_data["accent"], bg=self.app.theme["surface"]).pack(pady=5)
            self._btn(card, "Apply", lambda n=name: self.app.change_theme(n)).pack(fill=tk.X)

        for col in range(3):
            grid.grid_columnconfigure(col, weight=1)


class EditFontPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        saved_ver = self.app.user_settings.get("last_client", PEKORA_2021M_FOLDER)
        self.selected_ver = tk.StringVar(value=saved_ver)

    def _set_version(self, ver):
        self.selected_ver.set(ver)
        self.app.update_user_setting("last_client", ver)
        self.on_show()

    def _get_font_directory(self):
        roots = get_version_roots()
        for root in roots:
            path = os.path.join(root, PEKORA_VERSION_HASH, self.selected_ver.get(), PEKORA_FONTS_SUBPATH)
            if os.path.isdir(path):
                return path
        return None

    def on_show(self):
        for widget in self.winfo_children():
            widget.destroy()

        self._title("Font Settings", "Direct mirror replacement")
        card = tk.Frame(self, bg=self.app.theme["surface"], padx=20, pady=20)
        card.pack(fill=tk.X, padx=24)

        switch_frame = tk.Frame(card, bg=self.app.theme["surface"])
        switch_frame.pack(fill=tk.X, pady=(0, 20))

        for text, value in [("2021 Client", PEKORA_2021M_FOLDER), ("2020 Client", PEKORA_2020L_FOLDER)]:
            selected = (value == self.selected_ver.get())
            tk.Button(
                switch_frame, text=text, font=self.app.f_main,
                bg=self.app.theme["accent"] if selected else self.app.theme["bg"],
                fg=self.app.theme["active_text"] if selected else self.app.theme["text"],
                bd=0, padx=20, cursor="hand2", command=lambda v=value: self._set_version(v)
            ).pack(side=tk.LEFT, padx=2)

        self._btn(card, "✎ Select Font & Overwrite All", self._replace_fonts).pack(fill=tk.X)

    def _replace_fonts(self):
        font_file = filedialog.askopenfilename(title="Select Font", filetypes=[("Font Files", "*.ttf *.otf")])
        if not font_file:
            return

        destination = self._get_font_directory()
        if not destination:
            messagebox.showerror("Error", "Version directory not found!")
            return

        try:
            count = 0
            for item in os.listdir(destination):
                if item.lower().endswith((".ttf", ".otf")):
                    shutil.copy2(font_file, os.path.join(destination, item))
                    count += 1
            messagebox.showinfo("Success", f"Replaced {count} fonts.")
        except Exception as err:
            messagebox.showerror("Error", str(err))


class EditCursorPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        saved_ver = self.app.user_settings.get("last_client", PEKORA_2021M_FOLDER)
        self.selected_ver = tk.StringVar(value=saved_ver)

    def _set_version(self, ver):
        self.selected_ver.set(ver)
        self.app.update_user_setting("last_client", ver)
        self.on_show()

    def _get_cursor_directory(self):
        roots = get_version_roots()
        for root in roots:
            path = os.path.join(root, PEKORA_VERSION_HASH, self.selected_ver.get(), PEKORA_TEXT_SUBPATH, "Cursors", "KeyboardMouse")
            if os.path.isdir(path):
                return path
        return None

    def on_show(self):
        for widget in self.winfo_children():
            widget.destroy()

        self._title("Cursor Settings", "Direct replacement (64x64)")
        card = tk.Frame(self, bg=self.app.theme["surface"], padx=20, pady=20)
        card.pack(fill=tk.X, padx=24)

        switch_frame = tk.Frame(card, bg=self.app.theme["surface"])
        switch_frame.pack(fill=tk.X, pady=(0, 20))

        for text, value in [("2021 Client", PEKORA_2021M_FOLDER), ("2020 Client", PEKORA_2020L_FOLDER)]:
            selected = (value == self.selected_ver.get())
            tk.Button(
                switch_frame, text=text, font=self.app.f_main,
                bg=self.app.theme["accent"] if selected else self.app.theme["bg"],
                fg=self.app.theme["active_text"] if selected else self.app.theme["text"],
                bd=0, padx=20, cursor="hand2", command=lambda v=value: self._set_version(v)
            ).pack(side=tk.LEFT, padx=2)

        self._btn(card, "🖱 Select Image & Apply", self._replace_cursor).pack(fill=tk.X)

    def _replace_cursor(self):
        if not HAS_PIL:
            messagebox.showerror("Error", "Pillow required!")
            return

        img_path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])
        if not img_path:
            return

        destination = self._get_cursor_directory()
        if not destination:
            messagebox.showerror("Error", "Cursor folder not found!")
            return

        try:
            image = Image.open(img_path).resize((64, 64), Image.Resampling.LANCZOS)
            for cursor_name in ["ArrowCursor.png", "ArrowFarCursor.png"]:
                image.save(os.path.join(destination, cursor_name), "PNG")
            messagebox.showinfo("Success", "Cursor updated.")
        except Exception as err:
            messagebox.showerror("Error", str(err))


class CreditsPage(BasePage):
    def on_show(self):
        for widget in self.winfo_children():
            widget.destroy()

        self._title("Credits", f"Running version {VERSION}")
        card = tk.Frame(self, bg=self.app.theme["surface"], padx=20, pady=20)
        card.pack(fill=tk.X, padx=24)

        info_text = "Menwey - Dev\nPonuss - UI Design\nBased on Korone VoidStrap by vmdx"
        tk.Label(card, text=info_text, font=self.app.f_lg, fg=self.app.theme["accent"], bg=self.app.theme["surface"], justify=tk.LEFT).pack(anchor="w")
        tk.Label(self, text="github.com/menwey/KoroneSnowStrap", font=self.app.f_sm, fg=self.app.theme["muted"], bg=self.app.theme["bg"]).pack(side=tk.BOTTOM, pady=20)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--rpc-worker":
        client_name = sys.argv[2] if len(sys.argv) > 2 else "2021M"
        rpc_standalone_worker(client_name)
    else:
        app = KoroneSnowStrap()
        app.mainloop()
