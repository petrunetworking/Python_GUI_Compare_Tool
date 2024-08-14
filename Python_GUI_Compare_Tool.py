from ui.mainwindow import *
import argparse, sys

parser = argparse.ArgumentParser(description="Python_GUI_Compare_Tool - Python Tkinter GUI tool based on Python's difflib to compare two files of Directories")
parser.add_argument('-p', '--paths', metavar=('path1', 'path2'), nargs=2, help='Two paths to compare', required=False)

args = parser.parse_args()

leftpath = args.paths[0] if args.paths else None
rightpath = args.paths[1] if args.paths else None

main_window = MainWindow()
main_window.start(leftpath, rightpath)
