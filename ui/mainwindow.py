import os, mimetypes, filecmp
from difflibparser.difflibparser import *
from ui.mainwindow_ui import MainWindowUI
try:    # for Python2
    from Tkinter import *
    from tkFileDialog import askopenfilename, askdirectory
    from tkSimpleDialog import askstring
except ImportError:    # for Python3
    from tkinter import *
    from tkinter.filedialog import askopenfilename, askdirectory
    from tkinter.simpledialog import askstring

class MainWindow:
    def start(self, leftpath = None, rightpath = None):
        self.main_window = Tk()
        self.main_window.title('Python GUI Compare Text and Directories')
        self.__main_window_ui = MainWindowUI(self.main_window)
        self.left_content = ""  # Initialize left_content
        self.right_content = ""  # Initialize right_content
        self.leftFile = ''
        self.rightFile = ''
        self.diff_method = "side_by_side"  # Default diff method
        self.__main_window_ui.center_window()
        # Add the diff method options
        self.__main_window_ui.create_diff_method_options(self.main_window, self.update_diff_method)
        self.__main_window_ui.create_file_path_labels()
        self.__main_window_ui.create_text_areas()
        self.__main_window_ui.create_search_text_entry(self.__findNext)
        self.__main_window_ui.create_line_numbers()
        self.__main_window_ui.create_scroll_bars()
        self.__main_window_ui.create_file_treeview()
        self.__init_text_tags()
        path_to_my_project = os.getcwd()
        self.__main_window_ui.add_menu('File', [
            {'name': 'Compare Files', 'command': self.__browse_files},
            {'name': 'Compare Directories', 'command': self.__browse_directories},
            {'name': 'Compare Text Input', 'command': self.__show_text_input_dialog},

            {'separator'},
            {'name': 'Exit', 'command': self.__exit, 'accelerator': 'Alt+F4'}
            ])
        self.__main_window_ui.add_menu('Edit', [
            {'name': 'Find', 'command': self.__startFindText, 'accelerator': 'Ctrl+F'},
            {'separator'},
            {'name': 'Cut', 'command': self.__cut, 'accelerator': 'Ctrl+X'},
            {'name': 'Copy', 'command': self.__copy, 'accelerator': 'Ctrl+C'},
            {'name': 'Paste', 'command': self.__paste, 'accelerator': 'Ctrl+P'},
            {'separator'},
            {'name': 'Go To Line', 'command': self.__goToLine, 'accelerator': 'Ctrl+G'}
            ])
        self.__main_window_ui.fileTreeView.bind('<<TreeviewSelect>>', lambda *x:self.treeViewItemSelected())

        if (leftpath and os.path.isdir(leftpath)) or (rightpath and os.path.isdir(rightpath)):
            self.__load_directories(leftpath, rightpath)
        else:
            self.leftFile = leftpath if leftpath and not os.path.isdir(leftpath) else ''
            self.rightFile = rightpath if rightpath and not os.path.isdir(rightpath) else ''
            self.filesChanged()

        self.__bind_key_shortcuts()

        self.main_window.mainloop()

    def __bind_key_shortcuts(self):
        self.main_window.bind('<Control-f>', lambda *x: self.__startFindText())
        self.main_window.bind('<Control-g>', lambda *x: self.__goToLine())
        self.main_window.bind('<Escape>', lambda *x: self.__endFindText())
        self.main_window.bind('<F3>', self.__main_window_ui.searchTextDialog.nextResult)

    def __browse_files(self):
        self.__load_file('left')
        self.__load_file('right')
        self.filesChanged()
        self.__main_window_ui.fileTreeView.grid_remove()
        self.__main_window_ui.fileTreeYScrollbar.grid_remove()
        self.__main_window_ui.fileTreeXScrollbar.grid_remove()
    def __read_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return ""
    # Load directories into the treeview
    def __browse_directories(self):
        leftDir = self.__load_directory('left')
        rightDir = self.__load_directory('right')
        self.__load_directories(leftDir, rightDir)

    def __load_directories(self, leftDir, rightDir):
        if leftDir and rightDir:
            self.__main_window_ui.fileTreeView.grid()
            self.__main_window_ui.fileTreeYScrollbar.grid()
            self.__main_window_ui.fileTreeXScrollbar.grid()
            self.__main_window_ui.fileTreeView.delete(*self.__main_window_ui.fileTreeView.get_children())
            self.__browse_process_directory('', leftDir, rightDir)
    def __show_text_input_dialog(self):
        text_input_dialog = Toplevel(self.main_window)
        text_input_dialog.title("Compare Text-s Dialog")
        
        # Set size for the dialog
        text_input_dialog.geometry("900x900")
        
        # Left Text Label
        left_text_label = Label(text_input_dialog, text="Left Text:")
        left_text_label.grid(row=0, column=0, padx=10, pady=5, sticky=W)

        # Left Text Area with Scrollbar
        left_text_frame = Frame(text_input_dialog)
        left_text_frame.grid(row=1, column=0, padx=10, pady=5, sticky=N+S+E+W)
        left_text_scrollbar = Scrollbar(left_text_frame)
        left_text_area = Text(left_text_frame, yscrollcommand=left_text_scrollbar.set)
        left_text_scrollbar.config(command=left_text_area.yview)
        left_text_scrollbar.pack(side=RIGHT, fill=Y)
        left_text_area.pack(side=LEFT, fill=BOTH, expand=True)

        # Right Text Label
        right_text_label = Label(text_input_dialog, text="Right Text:")
        right_text_label.grid(row=0, column=1, padx=10, pady=5, sticky=W)

        # Right Text Area with Scrollbar
        right_text_frame = Frame(text_input_dialog)
        right_text_frame.grid(row=1, column=1, padx=10, pady=5, sticky=N+S+E+W)
        right_text_scrollbar = Scrollbar(right_text_frame)
        right_text_area = Text(right_text_frame, yscrollcommand=right_text_scrollbar.set)
        right_text_scrollbar.config(command=right_text_area.yview)
        right_text_scrollbar.pack(side=RIGHT, fill=Y)
        right_text_area.pack(side=LEFT, fill=BOTH, expand=True)

        # Compare Button
        compare_button = Button(text_input_dialog, text="Compare", command=lambda: self.__compare_texts(left_text_area.get("1.0", "end-1c"), right_text_area.get("1.0", "end-1c"), text_input_dialog))
        compare_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Make grid layout expandable
        text_input_dialog.grid_rowconfigure(1, weight=1)
        text_input_dialog.grid_columnconfigure(0, weight=1)
        text_input_dialog.grid_columnconfigure(1, weight=1)


    def __compare_texts(self, left_text, right_text, dialog):
        self.left_content = left_text
        self.right_content = right_text
        self.filesChanged()
        dialog.destroy()  # Close the dialog
        diff = DifflibParser(self.left_content, self.right_content, method=self.diff_method)

        # enable text area edits so we can clear and insert into them
        self.__main_window_ui.leftFileTextArea.config(state=NORMAL)
        self.__main_window_ui.rightFileTextArea.config(state=NORMAL)
        self.__main_window_ui.leftLinenumbers.config(state=NORMAL)
        self.__main_window_ui.rightLinenumbers.config(state=NORMAL)

        # clear all text areas
        self.__main_window_ui.leftFileTextArea.delete(1.0, END)
        self.__main_window_ui.rightFileTextArea.delete(1.0, END)
        self.__main_window_ui.leftLinenumbers.delete(1.0, END)
        self.__main_window_ui.rightLinenumbers.delete(1.0, END)

        leftlineno = rightlineno = 1
        for line in diff:
            if line['code'] == DiffCode.SIMILAR:
                self.__main_window_ui.leftFileTextArea.insert('end', line['line'] + '\n')
                self.__main_window_ui.rightFileTextArea.insert('end', line['line'] + '\n')
            elif line['code'] == DiffCode.RIGHTONLY:
                self.__main_window_ui.leftFileTextArea.insert('end', '\n', 'gray')
                self.__main_window_ui.rightFileTextArea.insert('end', line['line'] + '\n', 'green')
            elif line['code'] == DiffCode.LEFTONLY:
                self.__main_window_ui.leftFileTextArea.insert('end', line['line'] + '\n', 'red')
                self.__main_window_ui.rightFileTextArea.insert('end', '\n', 'gray')
            elif line['code'] == DiffCode.CHANGED:
                for (i,c) in enumerate(line['line']):
                    self.__main_window_ui.leftFileTextArea.insert('end', c, 'darkred' if i in line['leftchanges'] else 'red')
                for (i,c) in enumerate(line['newline']):
                    self.__main_window_ui.rightFileTextArea.insert('end', c, 'darkgreen' if i in line['rightchanges'] else 'green')
                self.__main_window_ui.leftFileTextArea.insert('end', '\n')
                self.__main_window_ui.rightFileTextArea.insert('end', '\n')

            if line['code'] == DiffCode.LEFTONLY:
                self.__main_window_ui.leftLinenumbers.insert('end', str(leftlineno) + '\n', 'line')
                self.__main_window_ui.rightLinenumbers.insert('end', '\n', 'line')
                leftlineno += 1
            elif line['code'] == DiffCode.RIGHTONLY:
                self.__main_window_ui.leftLinenumbers.insert('end', '\n', 'line')
                self.__main_window_ui.rightLinenumbers.insert('end', str(rightlineno) + '\n', 'line')
                rightlineno += 1
            else:
                self.__main_window_ui.leftLinenumbers.insert('end', str(leftlineno) + '\n', 'line')
                self.__main_window_ui.rightLinenumbers.insert('end', str(rightlineno) + '\n', 'line')
                leftlineno += 1
                rightlineno += 1

        # calc width of line numbers texts and set it
        self.__main_window_ui.leftLinenumbers.config(width=len(str(leftlineno)))
        self.__main_window_ui.rightLinenumbers.config(width=len(str(rightlineno)))

        # disable text areas to prevent further editing
        self.__main_window_ui.leftFileTextArea.config(state=DISABLED)
        self.__main_window_ui.rightFileTextArea.config(state=DISABLED)
        self.__main_window_ui.leftLinenumbers.config(state=DISABLED)
        self.__main_window_ui.rightLinenumbers.config(state=DISABLED)
    def __init_text_tags(self):
        # Configuring text tags for left and right file text areas
        self.__main_window_ui.leftFileTextArea.tag_configure("added", background="#90EE90")  # light green
        self.__main_window_ui.leftFileTextArea.tag_configure("removed", background="#FFCCCB")  # light red
        self.__main_window_ui.leftFileTextArea.tag_configure("changed", background="#FFFFE0")  # light yellow

        self.__main_window_ui.rightFileTextArea.tag_configure("added", background="#90EE90")  # light green
        self.__main_window_ui.rightFileTextArea.tag_configure("removed", background="#FFCCCB")  # light red
        self.__main_window_ui.rightFileTextArea.tag_configure("changed", background="#FFFFE0")  # light yellow



    def show_side_by_side_diff(self):
        parser = DifflibParser(self.left_content.splitlines(), self.right_content.splitlines(), method="Side by Side")
        left_lines = []
        right_lines = []

        for line in parser:
            line_content = line['line']
            if line_content.startswith('- '):
                left_lines.append((line_content[2:], "removed"))
                right_lines.append(('', ""))
            elif line_content.startswith('+ '):
                left_lines.append(('', ""))
                right_lines.append((line_content[2:], "added"))
            elif line_content.startswith('  '):
                left_lines.append((line_content[2:], ""))
                right_lines.append((line_content[2:], ""))

        max_width = max(len(line[0]) for line in left_lines) if left_lines else 0
        formatted_lines = [f"{l[0].ljust(max_width)} | {r[0]}" for l, r in zip(left_lines, right_lines)]

        self.__main_window_ui.leftFileTextArea.delete(1.0, END)
        self.__main_window_ui.rightFileTextArea.delete(1.0, END)

        for line, tag in left_lines:
            self.__main_window_ui.leftFileTextArea.insert(END, line + "\n", tag)
        for line, tag in right_lines:
            self.__main_window_ui.rightFileTextArea.insert(END, line + "\n", tag)

        self.__main_window_ui.rightFileTextArea.grid()
        # Disable text areas to prevent further editing
        self.__main_window_ui.leftFileTextArea.config(state=DISABLED)
        self.__main_window_ui.rightFileTextArea.config(state=DISABLED)
        self.__main_window_ui.leftLinenumbers.config(state=DISABLED)
        self.__main_window_ui.rightLinenumbers.config(state=DISABLED)
    def show_inline_diff(self):
        parser = DifflibParser(self.left_content.splitlines(), self.right_content.splitlines(), method="Inline")
        self.__main_window_ui.leftFileTextArea.delete(1.0, END)
        self.__main_window_ui.rightFileTextArea.delete(1.0, END)

        for line in parser:
            code = line.get('code')
            if code == DiffCode.SIMILAR:
                self.__main_window_ui.leftFileTextArea.insert(END, line.get('line', '') + "\n")
                self.__main_window_ui.rightFileTextArea.insert(END, line.get('line', '') + "\n")
            elif code == DiffCode.RIGHTONLY:
                self.__main_window_ui.rightFileTextArea.insert(END, line.get('line', '') + "\n", "added")
            elif code == DiffCode.LEFTONLY:
                self.__main_window_ui.leftFileTextArea.insert(END, line.get('line', '') + "\n", "removed")
            elif code == DiffCode.CHANGED:
                left_changes = ''.join(
                    [line.get('line', '')[i] if i not in line.get('leftchanges', []) else '' for i in range(len(line.get('line', '')))]
                )
                right_changes = ''.join(
                    [line.get('newline', '')[i] if i not in line.get('rightchanges', []) else '' for i in range(len(line.get('newline', '')))]
                )
                self.__main_window_ui.leftFileTextArea.insert(END, left_changes + "\n", "removed")
                self.__main_window_ui.rightFileTextArea.insert(END, right_changes + "\n", "added")

        self.__main_window_ui.rightFileTextArea.grid_remove()
        # Disable text areas to prevent further editing
        self.__main_window_ui.leftFileTextArea.config(state=DISABLED)
        self.__main_window_ui.rightFileTextArea.config(state=DISABLED)
        self.__main_window_ui.leftLinenumbers.config(state=DISABLED)
        self.__main_window_ui.rightLinenumbers.config(state=DISABLED)
    def show_diff_only(self):
        parser = DifflibParser(self.left_content.splitlines(), self.right_content.splitlines(), method="Diff Only")
        self.__main_window_ui.leftFileTextArea.delete(1.0, END)
        self.__main_window_ui.rightFileTextArea.delete(1.0, END)

        for line in parser:
            code = line.get('code')
            if code == DiffCode.LEFTONLY or code == DiffCode.CHANGED:
                self.__main_window_ui.leftFileTextArea.insert(END, line.get('line', '') + "\n", "removed")
            if code == DiffCode.RIGHTONLY or code == DiffCode.CHANGED:
                self.__main_window_ui.rightFileTextArea.insert(END, line.get('newline', '') + "\n", "added")

        self.__main_window_ui.rightFileTextArea.grid()
        # disable text areas to prevent further editing
        self.__main_window_ui.leftFileTextArea.config(state=DISABLED)
        self.__main_window_ui.rightFileTextArea.config(state=DISABLED)
        self.__main_window_ui.leftLinenumbers.config(state=DISABLED)
        self.__main_window_ui.rightLinenumbers.config(state=DISABLED)
    def show_complete_file_diff(self):
        parser = DifflibParser(self.left_content.splitlines(), self.right_content.splitlines(), method="Complete File")
        self.__main_window_ui.leftFileTextArea.delete(1.0, END)
        self.__main_window_ui.rightFileTextArea.delete(1.0, END)

        for line in parser:
            code = line.get('code')
            line_text = line.get('line', '')
            newline_text = line.get('newline', '')

            if code == DiffCode.SIMILAR:
                self.__main_window_ui.leftFileTextArea.insert(END, line_text + "\n")
                self.__main_window_ui.rightFileTextArea.insert(END, line_text + "\n")
            elif code == DiffCode.RIGHTONLY:
                self.__main_window_ui.rightFileTextArea.insert(END, line_text + "\n", "added")
            elif code == DiffCode.LEFTONLY:
                self.__main_window_ui.leftFileTextArea.insert(END, line_text + "\n", "removed")
            elif code == DiffCode.CHANGED:
                left_changes = ''.join(
                    [line_text[i] if i not in line.get('leftchanges', []) else '' for i in range(len(line_text))]
                )
                right_changes = ''.join(
                    [newline_text[i] if i not in line.get('rightchanges', []) else '' for i in range(len(newline_text))]
                )
                self.__main_window_ui.leftFileTextArea.insert(END, left_changes + "\n", "removed")
                self.__main_window_ui.rightFileTextArea.insert(END, right_changes + "\n", "added")

        # Ensure the widget is visible
        self.__main_window_ui.rightFileTextArea.grid()
        # Disable text areas to prevent further editing
        self.__main_window_ui.leftFileTextArea.config(state=DISABLED)
        self.__main_window_ui.rightFileTextArea.config(state=DISABLED)
        self.__main_window_ui.leftLinenumbers.config(state=DISABLED)
        self.__main_window_ui.rightLinenumbers.config(state=DISABLED)

    # Recursive method to fill the treevie with given directory hierarchy
    def __browse_process_directory(self, parent, leftPath, rightPath):
        if parent == '':
            leftPath = leftPath.rstrip('/')
            rightPath = rightPath.rstrip('/')
            leftDirName = os.path.basename(leftPath)
            rightDirName = os.path.basename(rightPath)
            self.__main_window_ui.fileTreeView.heading('#0', text=leftDirName + ' / ' + rightDirName, anchor=W)
        leftListing = os.listdir(leftPath)
        rightListing = os.listdir(rightPath)
        mergedListing = list(set(leftListing) | set(rightListing))
        painted = FALSE
        for l in mergedListing:
            newLeftPath = leftPath + '/' + l
            newRightPath = rightPath + '/' + l
            bindValue = (newLeftPath, newRightPath)
            # Item in left dir only
            if l in leftListing and l not in rightListing:
                self.__main_window_ui.fileTreeView.insert(parent, 'end', text=l, value=bindValue, open=False, tags=('red','simple'))
                painted = TRUE
            # Item in right dir only
            elif l in rightListing and l not in leftListing:
                self.__main_window_ui.fileTreeView.insert(parent, 'end', text=l, value=bindValue, open=False, tags=('green','simple'))
                painted = TRUE
            # Item in both dirs
            else:
                # If one of the diffed items is a file and the other is a directory, show in yellow indicating a difference
                if (not os.path.isdir(newLeftPath) and os.path.isdir(newRightPath)) or (os.path.isdir(newLeftPath) and not os.path.isdir(newRightPath)):
                    self.__main_window_ui.fileTreeView.insert(parent, 'end', text=l, value=bindValue, open=False, tags=('yellow','simple'))
                    painted = TRUE
                else:
                    # If both are directories, show in white and recurse on contents
                    if os.path.isdir(newLeftPath) and os.path.isdir(newRightPath):
                        oid = self.__main_window_ui.fileTreeView.insert(parent, 'end', text=l, open=False)
                        painted = self.__browse_process_directory(oid, newLeftPath, newRightPath)
                        if painted:
                            self.__main_window_ui.fileTreeView.item(oid, tags=('purpleLight', 'simple'))
                    else:
                        # Both are files. diff the two files to either show them in white or yellow
                        if (filecmp.cmp(newLeftPath, newRightPath)):
                            oid = self.__main_window_ui.fileTreeView.insert(parent, 'end', text=l, value=bindValue, open=False, tags=('simple'))
                        else:
                            oid = self.__main_window_ui.fileTreeView.insert(parent, 'end', text=l, value=bindValue, open=False, tags=('yellow','simple'))
                            painted = TRUE
        return painted

    def __load_file(self, pos):
        fname = askopenfilename()
        if fname:
            if pos == 'left':
                self.leftFile = fname
            else:
                self.rightFile = fname
            return fname
        else:
            return None

    def __load_directory(self, pos):
        dirName = askdirectory()
        if dirName:
            if pos == 'left':
                self.__main_window_ui.leftFileLabel.config(text=dirName)
            else:
                self.__main_window_ui.rightFileLabel.config(text=dirName)
            return dirName
        else:
            return None

    # Callback for changing a file path
    def filesChanged(self):
        self.__main_window_ui.leftLinenumbers.grid_remove()
        self.__main_window_ui.rightLinenumbers.grid_remove()

        if not self.leftFile or not self.rightFile:
            self.__main_window_ui.leftFileTextArea.config(background=self.__main_window_ui.grayColor)
            self.__main_window_ui.rightFileTextArea.config(background=self.__main_window_ui.grayColor)
            return

        if os.path.exists(self.leftFile):
            self.__main_window_ui.leftFileLabel.config(text=self.leftFile)
            self.__main_window_ui.leftFileTextArea.config(background=self.__main_window_ui.whiteColor)
            self.__main_window_ui.leftLinenumbers.grid()
            self.left_content = self.__read_file(self.leftFile)  # Read left file content
        else:
            self.__main_window_ui.leftFileLabel.config(text='')
            self.left_content = ''

        if os.path.exists(self.rightFile):
            self.__main_window_ui.rightFileLabel.config(text=self.rightFile)
            self.__main_window_ui.rightFileTextArea.config(background=self.__main_window_ui.whiteColor)
            self.__main_window_ui.rightLinenumbers.grid()
            self.right_content = self.__read_file(self.rightFile)  # Read right file content
        else:
            self.__main_window_ui.rightFileLabel.config(text='')
            self.right_content = ''

        self.diff_files_into_text_areas()

    def treeViewItemSelected(self):
        item_id = self.__main_window_ui.fileTreeView.focus()
        paths = self.__main_window_ui.fileTreeView.item(item_id)['values']
        if paths == None or len(paths) == 0:
            return
        self.leftFile = paths[0]
        self.rightFile = paths[1]
        self.filesChanged()

    # Insert file contents into text areas and highlight differences
    def diff_files_into_text_areas(self):
        try:
            with open(self.leftFile, 'r') as f:
                leftFileContents = f.read()
        except Exception as e:
            print(f"Error reading left file: {e}")
            leftFileContents = ''
        try:
            with open(self.rightFile, 'r') as f:
                rightFileContents = f.read()
        except Exception as e:
            print(f"Error reading right file: {e}")
            rightFileContents = ''

        diff = DifflibParser(leftFileContents.splitlines(), rightFileContents.splitlines(), method=self.diff_method)

        # enable text area edits so we can clear and insert into them
        self.__main_window_ui.leftFileTextArea.config(state=NORMAL)
        self.__main_window_ui.rightFileTextArea.config(state=NORMAL)
        self.__main_window_ui.leftLinenumbers.config(state=NORMAL)
        self.__main_window_ui.rightLinenumbers.config(state=NORMAL)

        # clear all text areas
        self.__main_window_ui.leftFileTextArea.delete(1.0, END)
        self.__main_window_ui.rightFileTextArea.delete(1.0, END)
        self.__main_window_ui.leftLinenumbers.delete(1.0, END)
        self.__main_window_ui.rightLinenumbers.delete(1.0, END)

        leftlineno = rightlineno = 1
        for line in diff:
            if line['code'] == DiffCode.SIMILAR:
                self.__main_window_ui.leftFileTextArea.insert('end', line['line'] + '\n')
                self.__main_window_ui.rightFileTextArea.insert('end', line['line'] + '\n')
            elif line['code'] == DiffCode.RIGHTONLY:
                self.__main_window_ui.leftFileTextArea.insert('end', '\n', 'gray')
                self.__main_window_ui.rightFileTextArea.insert('end', line['line'] + '\n', 'green')
            elif line['code'] == DiffCode.LEFTONLY:
                self.__main_window_ui.leftFileTextArea.insert('end', line['line'] + '\n', 'red')
                self.__main_window_ui.rightFileTextArea.insert('end', '\n', 'gray')
            elif line['code'] == DiffCode.CHANGED:
                for (i,c) in enumerate(line['line']):
                    self.__main_window_ui.leftFileTextArea.insert('end', c, 'darkred' if i in line['leftchanges'] else 'red')
                for (i,c) in enumerate(line['newline']):
                    self.__main_window_ui.rightFileTextArea.insert('end', c, 'darkgreen' if i in line['rightchanges'] else 'green')
                self.__main_window_ui.leftFileTextArea.insert('end', '\n')
                self.__main_window_ui.rightFileTextArea.insert('end', '\n')

            if line['code'] == DiffCode.LEFTONLY:
                self.__main_window_ui.leftLinenumbers.insert('end', str(leftlineno) + '\n', 'line')
                self.__main_window_ui.rightLinenumbers.insert('end', '\n', 'line')
                leftlineno += 1
            elif line['code'] == DiffCode.RIGHTONLY:
                self.__main_window_ui.leftLinenumbers.insert('end', '\n', 'line')
                self.__main_window_ui.rightLinenumbers.insert('end', str(rightlineno) + '\n', 'line')
                rightlineno += 1
            else:
                self.__main_window_ui.leftLinenumbers.insert('end', str(leftlineno) + '\n', 'line')
                self.__main_window_ui.rightLinenumbers.insert('end', str(rightlineno) + '\n', 'line')
                leftlineno += 1
                rightlineno += 1

        # calc width of line numbers texts and set it
        self.__main_window_ui.leftLinenumbers.config(width=len(str(leftlineno)))
        self.__main_window_ui.rightLinenumbers.config(width=len(str(rightlineno)))

        # disable text areas to prevent further editing
        self.__main_window_ui.leftFileTextArea.config(state=DISABLED)
        self.__main_window_ui.rightFileTextArea.config(state=DISABLED)
        self.__main_window_ui.leftLinenumbers.config(state=DISABLED)
        self.__main_window_ui.rightLinenumbers.config(state=DISABLED)
    def update_diff_method(self):
        # Update the diff method based on the user's selection
        self.diff_method = self.__main_window_ui.diff_method.get()

        # Clear current text areas
        self.__main_window_ui.leftFileTextArea.config(state=NORMAL)
        self.__main_window_ui.leftFileTextArea.delete('1.0', END)
        self.__main_window_ui.rightFileTextArea.config(state=NORMAL)
        self.__main_window_ui.rightFileTextArea.delete('1.0', END)

        # Display the diff according to the selected method
        if self.diff_method == "side_by_side":
            self.show_side_by_side_diff()
        elif self.diff_method == "inline":
            self.show_inline_diff()
        elif self.diff_method == "diff_only":
            self.show_diff_only()
        elif self.diff_method == "complete_file":
            self.show_complete_file_diff()

    def __cut(self):
        area = self.__getActiveTextArea()
        if area:
            area.event_generate("<<Cut>>")

    def __copy(self):
        area = self.__getActiveTextArea()
        if area:
            area.event_generate("<<Copy>>")

    def __paste(self):
        area = self.__getActiveTextArea()
        if area:
            area.event_generate("<<Paste>>")

    def __getActiveTextArea(self):
        if self.main_window.focus_get() == self.__main_window_ui.leftFileTextArea:
            return self.__main_window_ui.leftFileTextArea
        elif self.main_window.focus_get() == self.__main_window_ui.rightFileTextArea:
            return self.__main_window_ui.rightFileTextArea
        else:
            return None

    def __goToLine(self):
        line = askstring('Go to line', 'Enter line number:')
        if line:
            try:
                linenumber = int(line)
                self.__main_window_ui.leftFileTextArea.see(float(linenumber) + 5)
            except:
                pass

    def __startFindText(self):
        self.__main_window_ui.searchTextDialog.grid()
        self.__main_window_ui.searchTextDialog.focus()

    def __endFindText(self):
        self.__main_window_ui.leftFileTextArea.tag_remove('search', 1.0, END)
        self.__main_window_ui.rightFileTextArea.tag_remove('search', 1.0, END)
        self.__main_window_ui.searchTextDialog.unfocus()
        self.__main_window_ui.searchTextDialog.grid_remove()

    def __findNext(self, searchresult):
        term,leftpos,rightpos = searchresult['term'], searchresult['indices'][0], searchresult['indices'][1]
        if leftpos != -1:
            self.__main_window_ui.leftFileTextArea.tag_remove('search', 1.0, END)
            self.__main_window_ui.leftFileTextArea.tag_add('search', leftpos, '%s + %sc' % (leftpos, len(term)))
            # scroll to position plus five lines for visibility
            self.__main_window_ui.leftFileTextArea.see(float(leftpos) + 5)
        if rightpos != -1:
            self.__main_window_ui.rightFileTextArea.tag_remove('search', 1.0, END)
            self.__main_window_ui.rightFileTextArea.tag_add('search', rightpos, '%s + %sc' % (rightpos, len(term)))
            # scroll to position plus five lines for visibility
            self.__main_window_ui.rightFileTextArea.see(float(rightpos) + 5)

    def __exit(self):
        self.main_window.destroy()
