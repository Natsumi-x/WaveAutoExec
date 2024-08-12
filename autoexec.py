import os
import shutil
import json
from customtkinter import *
from tkinter import filedialog
from PIL import Image, ImageSequence
import sys
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Constants for file and folder paths
SETTINGS_FILE = "settings.json"
AUTOEXEC_FOLDER = os.path.expandvars(r'%LOCALAPPDATA%\Wave\autoexec')

def resource_path(relative_path):
    # Gets the absolute path to a resource, working both in development and when packaged with PyInstaller.
    try:
        # Get the base path from PyInstaller's temporary directory
        base_path = sys._MEIPASS
    except Exception:
        # If not running in a PyInstaller bundle, use the current directory
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class App(CTk):
    # Main application class for managing and running Roblox Wave autoexec scripts.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialize instance variables
        self.script_folder = ""
        self.load_settings()
        
        # Keep track of previous files for efficient updating
        self.previous_files = set()
        
        # Configure main window grid layout
        self.grid_columnconfigure(0, weight=1)

        # Create and configure header frame
        self.header_frame = CTkFrame(master=self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10)
        self.header_frame.grid_columnconfigure(0, weight=1)

        # Load and display animated GIF logo
        self.gif_path = resource_path("Assets/animated.gif")
        self.gif_frames, self.frame_durations = self.load_gif(self.gif_path)
        self.gif_index = 0
        self.gif_label = CTkLabel(master=self.header_frame, text="")
        self.gif_label.grid(row=0, column=0, sticky="ew", pady=10)
        self.gif_label.bind("<Button-1>", self.open_log_window)
        self.animate_gif()

        # Display application title
        self.title_label = CTkLabel(master=self.header_frame, text="Wave AutoExec", font=CTkFont(size=30, weight="normal"))
        self.title_label.grid(row=1, column=0, sticky="ew")

        # Button to set the scripts folder
        self.set_folder_button = CTkButton(master=self, text="Set Scripts Folder", command=self.set_scripts_folder)
        self.set_folder_button.grid(row=2, column=0, pady=30)

        # Create scrollable frame for script checkboxes
        self.checkbox_frame = CTkScrollableFrame(
            master=self, width=280, height=340, fg_color="#1D1E1E",
            scrollbar_button_hover_color="#1D1E1E",
            scrollbar_button_color="#1D1E1E"
        )
        self.checkbox_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)

        # Initialize log messages list
        self.log_messages = []

        # Initialize file system observer
        self.observer = Observer()

        # Start the file system observer
        self.restart_observer()
        if self.script_folder:
            self.update_option_menu()

    def load_settings(self):
        # Load settings from the settings file.
        if os.path.isfile(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                self.script_folder = settings.get("script_folder", "")

    def load_gif(self, path):
        # Loads a GIF file and returns a list of CTkImage frames and their durations.
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
        # Animates the GIF logo by cycling through the loaded frames.
        if self.gif_frames:
            self.gif_label.configure(image=self.gif_frames[self.gif_index])
            duration = self.frame_durations[self.gif_index]
            self.gif_index = (self.gif_index + 1) % len(self.gif_frames)
            self.after(duration, self.animate_gif)

    def open_log_window(self, event=None):
        # Opens a new window to display log messages.
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
        # Opens a directory dialog to select the scripts folder and updates the UI.
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.script_folder = folder_selected
            self.update_option_menu()
            self.save_settings()
            self.update_console(f"Set scripts folder: {self.script_folder}")
            self.restart_observer()

    def restart_observer(self):
        # Restarts the file system observer for the script folder and autoexec folder
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
        self.observer = Observer()

        if os.path.isdir(self.script_folder):
            self.observer.schedule(Handler(self), self.script_folder, recursive=False)
        if os.path.isdir(AUTOEXEC_FOLDER):
            self.observer.schedule(Handler(self), AUTOEXEC_FOLDER, recursive=False)
        self.observer.start()

    def update_option_menu(self):
        # Updates the checkbox list with the available .luau scripts in the selected folder and autoexec folder.
        script_files = {f for f in os.listdir(self.script_folder) if f.endswith('.luau')} if os.path.isdir(self.script_folder) else set()
        autoexec_files = {f for f in os.listdir(AUTOEXEC_FOLDER) if f.endswith('.luau')} if os.path.isdir(AUTOEXEC_FOLDER) else set()

        # Rebuild checkboxes only if the set of files has changed
        if script_files != self.previous_files: 
            for widget in self.checkbox_frame.winfo_children():
                widget.destroy()

            all_files = sorted(script_files | autoexec_files)

            for script in all_files:
                self.create_checkbox(script, script in autoexec_files)

            self.previous_files = script_files.copy() 
        else:
            # If the set of files hasn't changed, update checkbox colors
            for checkbox in self.checkbox_frame.winfo_children():
                script = checkbox.cget("text")
                self.update_checkbox_color(checkbox, script in script_files, script in autoexec_files)

    def update_checkbox_color(self, checkbox, in_scripts, in_autoexec):
        # Updates the color of a checkbox based on its presence in script folder and autoexec folder
        if in_autoexec and in_scripts:
            checkbox.select()
            checkbox.configure(text_color="#318ce7")
        elif in_autoexec:
            checkbox.select()
            checkbox.configure(fg_color="purple", text_color="purple")
        else:
            checkbox.deselect()
            checkbox.configure(text_color="white")

    def create_checkbox(self, script, in_autoexec):
        # Creates a checkbox for a script and configures its initial state
        var = BooleanVar(value=in_autoexec)
        checkbox = CTkCheckBox(master=self.checkbox_frame, text=script, variable=var)
        self.update_checkbox_color(checkbox, script in {f for f in os.listdir(self.script_folder) if f.endswith('.luau')} if os.path.isdir(self.script_folder) else set(), in_autoexec)
        checkbox.configure(command=lambda s=script, cb=checkbox, v=var: self.on_checkbox_toggle(s, cb, v))
        checkbox.pack(anchor="w", pady=2)

    def on_checkbox_toggle(self, script, checkbox, var):
        # Handles checkbox toggle events, adding or removing scripts from the autoexec folder.
        if var.get():
            self.add_script_to_autoexec(script)
            checkbox.select()
            checkbox.configure(text_color="#318ce7")
        else:
            self.remove_script_from_autoexec(script)
            checkbox.deselect()
            checkbox.configure(text_color="white")

    def add_script_to_autoexec(self, script):
        # Add the script to the autoexec folder if it exists in the script folder
        source_path = os.path.join(self.script_folder, script)
        if os.path.isfile(source_path):
            target_path = os.path.join(AUTOEXEC_FOLDER, script)
            if not os.path.isfile(target_path):
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
        # Save the current settings to the settings file.
        settings = {
            "script_folder": self.script_folder
        }
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)

class Handler(FileSystemEventHandler):
    # File system event handler for monitoring changes in script and autoexec folders
    def __init__(self, app):
        self.app = app

    def on_created(self, event):
        # Handle file creation events
        if not event.is_directory and event.src_path.endswith('.luau'):
            self.app.after(100, self.app.update_option_menu)

    def on_deleted(self, event):
        # Handle file deletion events
        if not event.is_directory and event.src_path.endswith('.luau'):
            self.app.after(100, self.app.update_option_menu)

if __name__ == "__main__":
    set_default_color_theme("blue")
    root = App()
    root.geometry("300x600")
    root.title("AutoExec")
    root.configure(fg_color=['#000000', '#000000'])
    root.mainloop()

# Made by @_natsumix
