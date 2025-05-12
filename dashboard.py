import tkinter as tk
from tkinter import messagebox
from manage_products import ProductManager
from manage_categories import CategoryManager
from manage_clients import ClientManager
from manage_rentals import RentalManager
from manage_events import EventManager
from PIL import Image, ImageTk
import os


class Dashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Panel de Administración - Relaxed Lounge Service")
        self.root.geometry("800x600")  # Aumentado la altura para acomodar el logo

        # Fondo
        self.root.configure(bg="#f5f5dc")

        # Título
        tk.Label(root, text="Panel de Administración", font=("Helvetica", 16, "bold"), bg="#f5f5dc").pack(pady=20)

        # Crear un contenedor principal para ambas filas de botones
        container_frame = tk.Frame(root, bg="#f5f5dc")
        container_frame.pack(pady=20)

        # Primera fila de botones (3 botones)
        row1_frame = tk.Frame(container_frame, bg="#f5f5dc")
        row1_frame.pack(pady=15)

        # Segunda fila de botones (2 botones)
        row2_frame = tk.Frame(container_frame, bg="#f5f5dc")
        row2_frame.pack(pady=15)

        # Definir estilo común de botones
        button_style = {"bg": "#4682b4", "fg": "#ffffff", "width": 20, "height": 2, "font": ("Helvetica", 12)}

        # Botones de la primera fila (3 botones)
        btn_products = tk.Button(row1_frame, text="Administrar Productos", command=self.open_products, **button_style)
        btn_products.pack(side="left", padx=10)

        btn_categories = tk.Button(row1_frame, text="Administrar Categorías", command=self.open_categories,
                                   **button_style)
        btn_categories.pack(side="left", padx=10)

        btn_clients = tk.Button(row1_frame, text="Administrar Clientes", command=self.open_clients, **button_style)
        btn_clients.pack(side="left", padx=10)

        # Botones de la segunda fila (2 botones) - centrados
        btn_rentals = tk.Button(row2_frame, text="Administrar Rentas", command=self.open_rentals, **button_style)
        btn_rentals.pack(side="left", padx=10)

        btn_events = tk.Button(row2_frame, text="Administrar Eventos", command=self.open_events, **button_style)
        btn_events.pack(side="left", padx=10)

        # Frame para el logo
        logo_frame = tk.Frame(root, bg="#f5f5dc")
        logo_frame.pack(pady=30)  # Espacio entre botones y logo

        # Cargar y mostrar el logo
        try:
            logo_path = os.path.join("images\\logo.jpg")  # Ruta de la imagen
            logo_image = Image.open(logo_path)

            # Redimensionar la imagen a un tamaño moderado (ajusta según necesites)
            logo_image = logo_image.resize((800, 230), Image.LANCZOS)

            # Convertir la imagen para Tkinter
            self.logo_photo = ImageTk.PhotoImage(logo_image)

            # Mostrar la imagen en un label
            logo_label = tk.Label(logo_frame, image=self.logo_photo, bg="#f5f5dc")
            logo_label.pack()
        except Exception as e:
            print(f"Error al cargar el logo: {e}")
            tk.Label(logo_frame, text="Logo no disponible", font=("Helvetica", 12), bg="#f5f5dc").pack()

    def open_products(self):
        new_window = tk.Toplevel(self.root)
        ProductManager(new_window)

    def open_categories(self):
        new_window = tk.Toplevel(self.root)
        CategoryManager(new_window)

    def open_clients(self):
        new_window = tk.Toplevel(self.root)
        ClientManager(new_window)

    def open_rentals(self):
        new_window = tk.Toplevel(self.root)
        RentalManager(new_window)

    def open_events(self):
        new_window = tk.Toplevel(self.root)
        EventManager(new_window)