# Python_GUI_Compare_Tool - Updated Version For  A Minimalistic Difflib GUI Created by Yebrahim 

Python_GUI_Compare_Tool is an open-source Tkinter-based GUI for Python's `difflib` module and updated version a gui created by yebrahim https://github.com/yebrahim/pydiff, allowing users to compare two text files or directory trees. This tool highlights differences, displays line numbers, and supports multiple diff methods, including side-by-side, inline, and diff-only views.


## Features

- Compare files and directories with ease
- Highlight differences with color-coded tags
- Support for multiple diff methods:
  - Side-by-Side
  - Inline
  - Diff-Only
  - Complete File
- Tree view for directory comparison
- Search functionality within files
- Simple and intuitive GUI

## Installation

### Prerequisites

- Python 3.x
- Tkinter library

### Clone the Repository
git clone https://github.com/petrunetworking/Python_GUI_Compare_Tool.git
cd Python_GUI_Compare_Tool
Install Dependencies
You can install required dependencies using pip:
If you don't have tkinter, install it using:

# Ubuntu/Debian
sudo apt-get install python3-tk

# macOS
brew install python-tk
## Usage

### Running the Application

You can run the application directly from the command line:
You can run the application directly from the command line:
python3 Python_GUI_Compare_Tool.py
Opening the GUI
Upon running the script, the Python_GUI_Compare_Tool GUI will open. You can then select files or directories for comparison using the menu or buttons.

Example
Compare Files: Click on the "File" menu and select "Compare Files." Choose two files to compare.
[menu_open_file](../Python_GUI_Compare_Tool/screenshot).png
Compare Directories: Click on the "File" menu and select "Compare Directories." Choose two directories to compare their contents.
[dir_compare](../Python_GUI_Compare_Tool/screenshot)
Switch Diff Methods: Use the diff method options to change between side-by-side, inline, diff-only, and complete file views.
[switch_method_compare](../Python_GUI_Compare_Tool/screenshot)
Search Text: Use the search bar to find specific text within the files.

## Code Structure

### Main Files

* `Python_GUI_Compare_Tool.py`: Main script to launch the application.
* `difflibparser/difflibparser.py`: Handles parsing and comparing files using difflib.
* `ui/mainwindow_ui.py`: Manages the Tkinter GUI components and layout.
* `ui/mainwindow.py`: Manages the Tkinter GUI components and layout.

### Key Components

* `MainWindow`: Initializes the GUI, handles user input, and controls file and directory comparisons.
* `DifflibParser`: Handles the logic for comparing files, generating diff outputs, and returning results based on the selected diff method.
* `Text Tags`: Configures the text tags for highlighting added, removed, and changed lines.

## Contributing

Contributions are welcome! If you have any improvements or feature requests, feel free to open a pull request or submit an issue on GitHub.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.