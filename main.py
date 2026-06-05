"""
main.py

Point d'entree de Check_file.
"""

import tkinter as tk
from application import MainWindow


def main():
    root = tk.Tk()
    root.resizable(True, True)
    MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
    