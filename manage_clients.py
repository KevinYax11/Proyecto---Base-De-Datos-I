import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class ClientManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Administrar Clientes")
        self.root.geometry("800x600")
        self.root.configure(bg="#f5f5dc")

        # Frame principal
        main_frame = tk.Frame(self.root, bg="#f5f5dc")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Título
        title_label = tk.Label(main_frame, text="Administrar Clientes", font=("Helvetica", 16, "bold"), bg="#f5f5dc")
        title_label.pack(pady=10)

        # Instrucciones
        tk.Label(main_frame, text="Nota: 'NIT' es opcional para facturación. Ingresa 'CF' para Consumidor Final.",
                 font=("Helvetica", 10), bg="#f5f5dc", fg="#666666").pack(pady=5)

        # Formulario para agregar cliente
        form_frame = tk.Frame(main_frame, bg="#f5f5dc")
        form_frame.pack(pady=10)

        # Nombre completo
        tk.Label(form_frame, text="Nombre Completo (requerido):", bg="#f5f5dc").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = tk.Entry(form_frame)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        # Teléfono
        tk.Label(form_frame, text="Teléfono (requerido):", bg="#f5f5dc").grid(row=1, column=0, padx=5, pady=5)
        self.phone_entry = tk.Entry(form_frame)
        self.phone_entry.grid(row=1, column=1, padx=5, pady=5)

        # Dirección
        tk.Label(form_frame, text="Dirección (opcional):", bg="#f5f5dc").grid(row=2, column=0, padx=5, pady=5)
        self.address_entry = tk.Entry(form_frame)
        self.address_entry.grid(row=2, column=1, padx=5, pady=5)

        # Tipo
        tk.Label(form_frame, text="Tipo (requerido):", bg="#f5f5dc").grid(row=3, column=0, padx=5, pady=5)
        self.type_combobox = ttk.Combobox(form_frame, values=["particular", "empresa"], state="readonly")
        self.type_combobox.grid(row=3, column=1, padx=5, pady=5)
        self.type_combobox.set("particular")

        # NIT
        tk.Label(form_frame, text="NIT (opcional):", bg="#f5f5dc").grid(row=4, column=0, padx=5, pady=5)
        self.nit_entry = tk.Entry(form_frame)
        self.nit_entry.grid(row=4, column=1, padx=5, pady=5)

        # Botón para agregar cliente
        add_button = tk.Button(main_frame, text="Agregar Cliente", command=self.add_client, bg="#4682b4", fg="#ffffff", font=("Helvetica", 12))
        add_button.pack(pady=10)

        # Tabla de clientes
        columns = ("ID", "Nombre", "Teléfono", "Dirección", "Tipo", "NIT", "Creado")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(fill="both", expand=True, pady=10)

        # Botón para cerrar
        close_button = tk.Button(main_frame, text="Cerrar", command=self.root.destroy, bg="#4682b4", fg="#ffffff", font=("Helvetica", 12))
        close_button.pack(pady=10)

        # Cargar clientes existentes
        self.load_clients()

    def load_clients(self):
        try:
            conn = sqlite3.connect("database.db")
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT cliente_id, nombre_completo, telefono, direccion, tipo, rfc, created_at
                FROM clientes
            """)
            clients = cursor.fetchall()

            for client in clients:
                self.tree.insert("", "end", values=(
                    client["cliente_id"],
                    client["nombre_completo"],
                    client["telefono"],
                    client["direccion"] if client["direccion"] else "",
                    client["tipo"],
                    "CF" if client["rfc"] == "CF" else (client["rfc"] if client["rfc"] else ""),
                    client["created_at"]
                ))

            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al cargar clientes: {e}")

    def add_client(self):
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        address = self.address_entry.get().strip() if self.address_entry.get().strip() else None
        client_type = self.type_combobox.get()
        nit = self.nit_entry.get().upper().strip() if self.nit_entry.get().strip() else None  # Convertir a mayúsculas

        # Validaciones
        if not name or not phone or not client_type:
            messagebox.showerror("Error", "Por favor, completa todos los campos obligatorios (Nombre, Teléfono, Tipo).")
            return

        # Validar NIT: puede ser "CF", un valor válido o NULL
        nit_value = "CF" if nit == "CF" else nit

        try:
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO clientes (nombre_completo, telefono, direccion, tipo, rfc, created_at)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
            """, (name, phone, address, client_type, nit_value))
            conn.commit()
            client_id = cursor.lastrowid

            # Obtener la fecha de creación
            cursor.execute("SELECT created_at FROM clientes WHERE cliente_id = ?", (client_id,))
            created_at = cursor.fetchone()[0]

            # Actualizar la tabla
            self.tree.insert("", "end", values=(client_id, name, phone, address if address else "", client_type, "CF" if nit_value == "CF" else (nit_value if nit_value else ""), created_at))
            conn.close()

            # Limpiar formulario
            self.name_entry.delete(0, tk.END)
            self.phone_entry.delete(0, tk.END)
            self.address_entry.delete(0, tk.END)
            self.nit_entry.delete(0, tk.END)
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al agregar cliente: {e}")