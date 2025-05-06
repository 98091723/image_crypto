import tkinter as tk
from gui import ImageCryptoGUI
import os

def init_log():
    if not os.path.exists("log"):
        os.makedirs("log")

def main():
    init_log()
    root = tk.Tk()
    app = ImageCryptoGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()