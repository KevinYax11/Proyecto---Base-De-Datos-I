import tkinter as tk
from tkinter import messagebox
import hashlib
from database import Database

class LoginWindow:
    def __init__(self, root, on_login_success):
        self.root = root
        self.root.title("Inicio de Sesión - Renta de Mobiliario")
        self.root.geometry("300x200")
        self.on_login_success = on_login_success
        self.db = Database()

        # Fondo
        self.root.configure(bg="#f5f5dc")

        # Elementos de la interfaz
        tk.Label(root, text="Correo Electrónico:", bg="#f5f5dc").pack(pady=10)
        self.email_entry = tk.Entry(root)
        self.email_entry.pack()

        tk.Label(root, text="Contraseña:", bg="#f5f5dc").pack(pady=10)
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack()

        tk.Button(root, text="Iniciar Sesión", command=self.login, bg="#4682b4", fg="#ffffff").pack(pady=20)

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        query = "SELECT * FROM usuarios WHERE email = %s AND password_hash = %s AND rol = 'admin' AND estado = 'activo'"
        result = self.db.execute_query(query, (email, password_hash), fetch=True)

        if result:
            messagebox.showinfo("Éxito", "¡Inicio de sesión exitoso!")
            self.root.destroy()
            self.on_login_success()
        else:
            messagebox.showerror("Error", "Credenciales inválidas o no es administrador.")