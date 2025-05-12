import tkinter as tk
from login import LoginWindow
from dashboard import Dashboard

def main():
    root = tk.Tk()
    login = LoginWindow(root, lambda: open_dashboard())
    root.mainloop()

def open_dashboard():
    root = tk.Tk()
    dashboard = Dashboard(root)
    root.mainloop()


main()