import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class QuotationCreationManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Realizar Cotización")
        self.root.geometry("600x400")
        self.root.configure(bg="#f5f5dc")

        # Frame principal
        main_frame = tk.Frame(self.root, bg="#f5f5dc")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Título
        title_label = tk.Label(main_frame, text="Realizar Cotización", font=("Helvetica", 16, "bold"), bg="#f5f5dc")
        title_label.pack(pady=10)

        # Formulario
        form_frame = tk.Frame(main_frame, bg="#f5f5dc")
        form_frame.pack(pady=10)

        # Selección de categoría
        tk.Label(form_frame, text="Categoría:", bg="#f5f5dc").grid(row=0, column=0, padx=5, pady=5)
        self.category_combobox = ttk.Combobox(form_frame, state="readonly")
        self.category_combobox.grid(row=0, column=1, padx=5, pady=5)
        self.category_combobox.bind("<<ComboboxSelected>>", self.update_products)

        # Selección de producto
        tk.Label(form_frame, text="Producto:", bg="#f5f5dc").grid(row=1, column=0, padx=5, pady=5)
        self.product_combobox = ttk.Combobox(form_frame, state="readonly")
        self.product_combobox.grid(row=1, column=1, padx=5, pady=5)

        # Cantidad
        tk.Label(form_frame, text="Cantidad:", bg="#f5f5dc").grid(row=2, column=0, padx=5, pady=5)
        self.quantity_entry = tk.Entry(form_frame)
        self.quantity_entry.grid(row=2, column=1, padx=5, pady=5)

        # Días de renta
        tk.Label(form_frame, text="Días de Renta:", bg="#f5f5dc").grid(row=3, column=0, padx=5, pady=5)
        self.days_entry = tk.Entry(form_frame)
        self.days_entry.grid(row=3, column=1, padx=5, pady=5)

        # Botón para calcular costo
        calculate_button = tk.Button(form_frame, text="Calcular Costo", command=self.calculate_cost, bg="#4682b4", fg="#ffffff", font=("Helvetica", 12))
        calculate_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Label para mostrar el costo
        self.cost_label = tk.Label(form_frame, text="Costo Total: $0.00", font=("Helvetica", 12), bg="#f5f5dc")
        self.cost_label.grid(row=5, column=0, columnspan=2, pady=10)

        # Botón para cerrar
        close_button = tk.Button(main_frame, text="Cerrar", command=self.root.destroy, bg="#4682b4", fg="#ffffff", font=("Helvetica", 12))
        close_button.pack(pady=10)

        # Cargar categorías y productos
        self.load_categories()

    def load_categories(self):
        try:
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute("SELECT categoria_id, nombre FROM categorias WHERE es_activa = 1")
            categories = cursor.fetchall()
            self.category_dict = {cat[1]: cat[0] for cat in categories}  # {nombre: id}
            self.category_combobox['values'] = list(self.category_dict.keys())
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al cargar categorías: {e}")

    def update_products(self, event=None):
        selected_category = self.category_combobox.get()
        if not selected_category:
            return

        category_id = self.category_dict[selected_category]
        try:
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute("SELECT producto_id, nombre FROM productos WHERE categoria_id = ? AND es_activo = 1", (category_id,))
            products = cursor.fetchall()
            self.product_dict = {prod[1]: prod[0] for prod in products}  # {nombre: id}
            self.product_combobox['values'] = list(self.product_dict.keys())
            self.product_combobox.set("")  # Limpiar selección
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al cargar productos: {e}")

    def calculate_cost(self):
        selected_product = self.product_combobox.get()
        quantity_str = self.quantity_entry.get()
        days_str = self.days_entry.get()

        # Validaciones
        if not selected_product:
            messagebox.showerror("Error", "Por favor, selecciona un producto.")
            return
        if not quantity_str or not days_str:
            messagebox.showerror("Error", "Por favor, ingresa la cantidad y los días de renta.")
            return

        try:
            quantity = int(quantity_str)
            days = int(days_str)
            if quantity <= 0 or days <= 0:
                messagebox.showerror("Error", "La cantidad y los días deben ser mayores a 0.")
                return
        except ValueError:
            messagebox.showerror("Error", "La cantidad y los días deben ser números enteros.")
            return

        # Obtener el precio del producto
        product_id = self.product_dict[selected_product]
        try:
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute("SELECT precio_diario FROM productos WHERE producto_id = ?", (product_id,))
            product = cursor.fetchone()
            if product:
                price_per_day = product[0]
                total_cost = price_per_day * quantity * days
                self.cost_label.config(text=f"Costo Total: ${total_cost:.2f}")
            else:
                messagebox.showerror("Error", "Producto no encontrado.")
            conn.close()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al calcular el costo: {e}")