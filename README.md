# AutoExec Script Manager

AutoExec is a desktop application built with `customtkinter` that allows users to manage `.luau` scripts for the Wave application. It provides a graphical interface to select and copy scripts to an auto-execution folder and includes features such as GIF animation and script deletion.

<div align="center">
  <img src="Assets/autoexec.gif" alt="AutoExec GUI" width="300">
</div>

## Features

- **Select Scripts Folder**: Easily set the folder where your `.luau` scripts are located.
- **Script Management**: Select a script to copy it to the auto-execution folder. Use the "None" option to delete all scripts in the folder.
- **Settings Persistence**: Remembers your last selected folder and script.

## Requirements

- Python 3.x
- [customtkinter](https://github.com/TomSchimansky/CustomTkinter)
- [Pillow](https://python-pillow.org/)
- `tkinter` (usually included with Python)

## Installation

1. **Clone the Repository**:
   ```#bash
   git clone https://github.com/Natsumi-x/autoexec-script-manager.git
   cd autoexec-script-manager
   ```

2. **Install Dependencies**:
   ```bash
   pip install customtkinter Pillow
   ```

## Usage

1. **Run the Application**:
   ```bash
   python main.py
   ```

2. **Select Scripts Folder**: Click "Set Scripts Folder" to choose the directory containing your `.luau` scripts.

3. **Choose a Script**: Use the drop-down menu to select a script to copy to the auto-execution folder. Choose "None" to delete all scripts in the folder.

## Building with PyInstaller

1. **Install PyInstaller**:
   ```bash
   pip install pyinstaller
   ```

2. **Create Executable**:
   ```bash
   pyinstaller --noconfirm --onefile --windowed --icon "<PATH>\waveautoexec\icon.ico" --add-data "<PATH>\waveautoexec\Assets;Assets/"  "<PATH>\waveautoexec\autoexec.py"
   ```
   Replace `<PATH>` with the path to the folder.

3. **Run the Executable**:
   Navigate to the `output` directory and execute the `AutoExec.exe`.

## Code Overview

### Key Components

- **GIF Handling**: Uses `Pillow` to load and display animated GIFs.
- **Script Selection**: Provides a drop-down menu for selecting scripts.
- **Settings Management**: Saves and loads user settings from a JSON file.

### Functions

- `resource_path(relative_path)`: Manages file paths for development and bundled environments.
- `load_gif(path)`: Loads GIF frames and durations.
- `animate_gif()`: Animates the GIF in the interface.
- `set_scripts_folder()`: Opens a dialog to set the scripts folder.
- `update_option_menu()`: Updates the script selection menu.
- `option_menu_select(selected_file)`: Handles script selection and copying.
- `confirm_delete()`: Confirms and deletes all scripts in the auto-execution folder.
- `update_console(message)`: Updates the console with messages.
- `save_settings()`: Saves the current settings to a file.
- `load_settings()`: Loads settings from a file.

## Contribution

Feel free to contribute by opening issues or submitting pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License.
