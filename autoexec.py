import os
import shutil
import json
from customtkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageSequence
import sys

SETTINGS_FILE = "settings.json"
AUTOEXEC_FOLDER = os.path.expandvars(r'%LOCALAPPDATA%\Wave\autoexec')

def resource_path(relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class App(CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.script_folder = ""
        self.last_selected_script = ""

        self.grid_columnconfigure(0, weight=1)

        self.FRAME0 = CTkFrame(master=self, fg_color="transparent")
        self.FRAME0.grid(row=0, column=0, sticky="ew", padx=10)
        self.FRAME0.grid_columnconfigure(0, weight=1)

        # Initialize GIF handling
        self.gif_path = resource_path("Assets/animated.gif")
        self.gif_frames, self.frame_durations = self.load_gif(self.gif_path)
        self.gif_index = 0
        self.gif_label = CTkLabel(master=self.FRAME0, text="")
        self.gif_label.grid(row=0, column=0, sticky="ew", pady=10)
        self.gif_label.bind("<Button-1>", self.open_log_window)
        self.animate_gif()

        self.LABEL9 = CTkLabel(master=self.FRAME0, text="Wave AutoExec", font=CTkFont(size=30, weight="normal"))
        self.LABEL9.grid(row=1, column=0, sticky="ew")
        self.BUTTON10 = CTkButton(master=self, text="Set Scripts Folder", command=self.set_scripts_folder)
        self.BUTTON10.grid(row=2, column=0, pady=30)

        # Frame for the checkboxes
        self.checkbox_frame = CTkScrollableFrame(
            master=self, width=280, height=340, fg_color="#1D1E1E",
            scrollbar_button_hover_color="#1D1E1E",
            scrollbar_button_color="#1D1E1E"
        )
        self.checkbox_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)

        self.log_messages = []

        self.load_settings()
        if self.script_folder:
            self.update_option_menu()

    def load_gif(self, path):
        # Load GIF and return a list of CTkImage frames and their durations
        frames = []
        frame_durations = []
        with Image.open(path) as img:
            for frame in ImageSequence.Iterator(img):
                frame = frame.convert("RGBA")
                ctk_image = CTkImage(dark_image=frame, size=(80, 80))
                frames.append(ctk_image)
                frame_durations.append(frame.info.get('duration', 100))
        return frames, frame_durations

    def animate_gif(self):
        # Animate the GIF by updating the label with the next frame in the sequence
        if self.gif_frames:
            self.gif_label.configure(image=self.gif_frames[self.gif_index])
            duration = self.frame_durations[self.gif_index]
            self.gif_index = (self.gif_index + 1) % len(self.gif_frames)
            self.after(duration, self.animate_gif)

    def open_log_window(self, event=None):
        # Open a new window to display log messages
        log_window = CTkToplevel(self)
        log_window.geometry("600x300")
        log_window.title("Log Messages")
        log_window.configure(fg_color="#000000")

        log_textbox = CTkTextbox(master=log_window, width=580, height=280, state="normal", fg_color="#1D1E1E")
        log_textbox.pack(pady=10, padx=10)

        for message in self.log_messages:
            log_textbox.insert("end", message + "\n")

        log_textbox.configure(state="disabled")

    def set_scripts_folder(self):
        # Open a dialog to set the scripts folder and update the options
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.script_folder = folder_selected
            self.update_option_menu()
            self.save_settings()
            self.update_console(f"Set scripts folder: {self.script_folder}")

    def update_option_menu(self):
        # Update the checkbox list with the available .luau scripts
        for widget in self.checkbox_frame.winfo_children():
            widget.destroy()

        luau_files = [f for f in os.listdir(self.script_folder) if f.endswith('.luau')]
        self.update_console(f"Found .luau files: {luau_files}")

        for script in luau_files:
            var = BooleanVar()
            checkbox = CTkCheckBox(
                master=self.checkbox_frame, text=script, variable=var
            )
            checkbox.configure(command=lambda s=script, cb=checkbox, v=var: self.on_checkbox_toggle(s, cb, v))
            checkbox.pack(anchor="w", pady=2)

    def on_checkbox_toggle(self, script, checkbox, var):
        # Handle the checkbox toggle event
        if var.get():
            checkbox.configure(text_color="#318ce7")
            self.add_script_to_autoexec(script)
        else:
            checkbox.configure(text_color="white")
            self.remove_script_from_autoexec(script)

    def add_script_to_autoexec(self, script):
        # Add the script to the autoexec folder
        source_path = os.path.join(self.script_folder, script)
        if not os.path.isfile(source_path):
            self.update_console(f"Source file does not exist: {source_path}")
            return

        if not os.path.isdir(AUTOEXEC_FOLDER):
            os.makedirs(AUTOEXEC_FOLDER, exist_ok=True)

        target_path = os.path.join(AUTOEXEC_FOLDER, script)
        shutil.copy(source_path, target_path)
        self.update_console(f"Copied '{script}' to {AUTOEXEC_FOLDER}")

    def remove_script_from_autoexec(self, script):
        # Remove the script from the autoexec folder
        target_path = os.path.join(AUTOEXEC_FOLDER, script)
        if os.path.isfile(target_path):
            os.remove(target_path)
            self.update_console(f"Removed '{script}' from {AUTOEXEC_FOLDER}")

    def update_console(self, message):
        # Update the log message list
        self.log_messages.append(message)
        print(message)

    def save_settings(self):
        # Save the current settings to a JSON file
        settings = {
            "script_folder": self.script_folder,
            "last_selected_script": self.last_selected_script
        }
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)

    def load_settings(self):
        # Load the settings from a JSON file if it exists
        if os.path.isfile(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                self.script_folder = settings.get("script_folder", "")
                self.last_selected_script = settings.get("last_selected_script", "")

if __name__ == "__main__":
    set_default_color_theme("blue")
    root = App()
    root.geometry("300x600")
    root.title("AutoExec")
    root.configure(fg_color=['#000000', '#000000'])
    root.mainloop()

# Made by @_natsumix
