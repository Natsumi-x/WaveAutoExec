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
        self.animate_gif()

        self.LABEL9 = CTkLabel(master=self.FRAME0, text="Wave AutoExec", font=CTkFont(size=30, weight="normal"))
        self.LABEL9.grid(row=1, column=0, sticky="ew")
        self.BUTTON10 = CTkButton(master=self, text="Set Scripts Folder", command=self.set_scripts_folder)
        self.BUTTON10.grid(row=2, column=0, pady=10)

        # Frame for the loaded scripts console
        self.loaded_frame = CTkFrame(master=self, fg_color="transparent")
        self.loaded_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        self.loaded_frame.grid_columnconfigure(0, weight=1)

        # Header for the loaded scripts console
        self.loaded_label = CTkLabel(master=self.loaded_frame, text="Loaded Scripts", font=CTkFont(size=14, weight="bold"))
        self.loaded_label.grid(row=0, column=0, sticky="ew")

        # Console to display scripts in the autoexec folder
        self.AUTOEXEC_CONSOLE = CTkTextbox(master=self.loaded_frame, width=280, height=100, state="disabled")
        self.AUTOEXEC_CONSOLE.grid(row=1, column=0, pady=5, sticky="ew")

        # Console to display log messages
        self.CONSOLE = CTkTextbox(master=self, width=280, height=180, state="disabled")
        self.CONSOLE.grid(row=3, column=0, pady=10, padx=10)

        self.OPTIONMENU8 = CTkOptionMenu(master=self, values=["Select a script"], width=263, height=27, command=self.option_menu_select)
        self.OPTIONMENU8.grid(row=4, column=0, pady=10)

        self.load_settings()
        if self.script_folder:
            self.update_option_menu()
        self.update_autoexec_console()

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

    def set_scripts_folder(self):
        # Open a dialog to set the scripts folder and update the option menu
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.script_folder = folder_selected
            self.update_option_menu()
            self.save_settings()
            self.update_console(f"Set scripts folder: {self.script_folder}")

    def update_option_menu(self):
        # Update the option menu with the available .luau scripts and add 'None' option
        luau_files = [f for f in os.listdir(self.script_folder) if f.endswith('.luau')]
        self.update_console(f"Found .luau files: {luau_files}")
        if luau_files:
            luau_files.append("None/Delete all scripts")
            self.OPTIONMENU8.configure(values=luau_files)
            self.OPTIONMENU8.set("Select a script")
            self.save_settings()

    def update_autoexec_console(self):
        # Update the console with the list of scripts in the autoexec folder
        self.AUTOEXEC_CONSOLE.configure(state="normal")
        self.AUTOEXEC_CONSOLE.delete("1.0", "end")
        try:
            files = os.listdir(AUTOEXEC_FOLDER)
            luau_files = [f"- {f}" for f in files if f.endswith('.luau')]
            self.AUTOEXEC_CONSOLE.insert("end", "\n".join(luau_files) + "\n")
        except Exception as e:
            self.AUTOEXEC_CONSOLE.insert("end", f"Error accessing autoexec folder: {e}\n")
        self.AUTOEXEC_CONSOLE.configure(state="disabled")

    def option_menu_select(self, selected_file):
        # Handle the selection of a script from the option menu
        if selected_file != "Select a script":
            if selected_file == "None/Delete all scripts":
                self.confirm_delete()
                return

            source_path = os.path.join(self.script_folder, selected_file)
            self.update_console(f"Selected file: {source_path}")

            if not os.path.isfile(source_path):
                self.update_console(f"Source file does not exist: {source_path}")
                return

            if not os.path.isdir(AUTOEXEC_FOLDER):
                self.update_console(f"Creating autoexec folder: {AUTOEXEC_FOLDER}")
                os.makedirs(AUTOEXEC_FOLDER, exist_ok=True)

            previous_script_path = os.path.join(AUTOEXEC_FOLDER, self.last_selected_script)
            if self.last_selected_script and os.path.isfile(previous_script_path):
                os.remove(previous_script_path)
                self.update_console(f"Removed previous script: {previous_script_path}")

            try:
                target_path = os.path.join(AUTOEXEC_FOLDER, selected_file)
                self.update_console(f"Copying file from {source_path} to {target_path}")
                shutil.copy(source_path, target_path)
                self.update_console(f"Copied '{selected_file}' to {AUTOEXEC_FOLDER}")
            except Exception as e:
                self.update_console(f"Failed to copy '{selected_file}': {e}")
                return

            self.last_selected_script = selected_file
            self.save_settings()
            self.update_autoexec_console()

    def confirm_delete(self):
        # Show a confirmation dialog to delete all scripts in the AutoExec folder
        if messagebox.askyesno("Confirm Delete", "This will delete all scripts in your AutoExec folder, are you sure?"):
            self.update_console("Selected 'None', deleting all scripts in autoexec folder.")
            try:
                for filename in os.listdir(AUTOEXEC_FOLDER):
                    file_path = os.path.join(AUTOEXEC_FOLDER, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        self.update_console(f"Removed file: {file_path}")
                self.last_selected_script = ""
                self.save_settings()
            except Exception as e:
                self.update_console(f"Failed to delete scripts: {e}")
            self.update_autoexec_console()

    def update_console(self, message):
        # Update the console textbox with a new message
        self.CONSOLE.configure(state="normal")
        self.CONSOLE.insert("end", message + "\n")
        self.CONSOLE.configure(state="disabled")
        self.CONSOLE.see("end")
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
