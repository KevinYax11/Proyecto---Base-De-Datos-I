import tkinter as tk
from tkinter import messagebox, ttk, Toplevel
from database import Database
from PIL import Image, ImageTk

class EventManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Administrar Eventos")
        self.root.geometry("1000x800")
        self.db = Database()

        # Estilo
        self.style = ttk.Style()
        self.style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))
        self.style.configure("Treeview", rowheight=80)

        # Fondo
        self.root.configure(bg="#f5f5dc")

        # Formulario
        form_frame = tk.Frame(root, bg="#f5f5dc")
        form_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(form_frame, text="Cliente ID:", bg="#f5f5dc").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.client_id = tk.Entry(form_frame)
        self.client_id.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Nombre:", bg="#f5f5dc").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.name = tk.Entry(form_frame)
        self.name.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Fecha Inicio:", bg="#f5f5dc").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.date_start = tk.Entry(form_frame)
        self.date_start.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Fecha Fin:", bg="#f5f5dc").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.date_end = tk.Entry(form_frame)
        self.date_end.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Dirección:", bg="#f5f5dc").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.location = tk.Entry(form_frame)
        self.location.grid(row=4, column=1, padx=5, pady=5)

        # Botones
        button_frame = tk.Frame(root, bg="#f5f5dc")
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Agregar Evento", command=self.add_event, bg="#4682b4", fg="#ffffff").pack(side="left", padx=5)
        tk.Button(button_frame, text="Actualizar Evento", command=self.update_event, bg="#4682b4", fg="#ffffff").pack(side="left", padx=5)
        tk.Button(button_frame, text="Eliminar Evento", command=self.delete_event, bg="#4682b4", fg="#ffffff").pack(side="left", padx=5)

        # Treeview para Eventos
        self.event_tree = ttk.Treeview(root, columns=("ID", "Nombre", "Fecha Inicio", "Fecha Fin", "Dirección"), show="headings", height=5)
        self.event_tree.heading("ID", text="ID")
        self.event_tree.heading("Nombre", text="Nombre")
        self.event_tree.heading("Fecha Inicio", text="Fecha Inicio")
        self.event_tree.heading("Fecha Fin", text="Fecha Fin")
        self.event_tree.heading("Dirección", text="Dirección")
        self.event_tree.column("ID", width=50)
        self.event_tree.column("Nombre", width=150)
        self.event_tree.column("Fecha Inicio", width=150)
        self.event_tree.column("Fecha Fin", width=150)
        self.event_tree.column("Dirección", width=200)
        self.event_tree.pack(pady=10, padx=10, fill="both")
        self.event_tree.bind("<<TreeviewSelect>>", self.load_event)

        # Treeview para Productos Asociados
        tk.Label(root, text="Productos Asociados (vía Rentas)", font=('Helvetica', 12, 'bold'), bg="#f5f5dc").pack(pady=5)
        self.product_tree = ttk.Treeview(root, columns=("Renta ID", "Producto", "Cantidad", "Imagen"), show="headings", height=5)
        self.product_tree.heading("Renta ID", text="Renta ID")
        self.product_tree.heading("Producto", text="Producto")
        self.product_tree.heading("Cantidad", text="Cantidad")
        self.product_tree.heading("Imagen", text="Imagen")
        self.product_tree.column("Renta ID", width=100)
        self.product_tree.column("Producto", width=200)
        self.product_tree.column("Cantidad", width=100)
        self.product_tree.column("Imagen", width=150)
        self.product_tree.pack(pady=10, padx=10, fill="both", expand=True)
        self.product_tree.bind("<Double-1>", self.show_image_on_double_click)

        self.images = {}
        self.image_paths = {}
        self.preview_window = None
        self.load_events()

    def show_image_on_double_click(self, event):
        selected = self.product_tree.selection()
        if not selected:
            return
        item = self.product_tree.item(selected)
        if item["values"][3] == "Ver Imagen":
            renta_id = item["values"][0]
            product_name = item["values"][1]
            product_id = f"{renta_id}_{product_name}"
            image_path = self.image_paths.get(product_id)
            if image_path:
                self.show_image_preview(image_path)

    def show_image_preview(self, image_path):
        if self.preview_window:
            self.preview_window.destroy()

        self.preview_window = Toplevel(self.root)
        self.preview_window.title("Vista Previa de la Imagen")
        self.preview_window.geometry("300x300")

        try:
            image = Image.open(image_path)
            image = image.resize((250, 250), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            label = tk.Label(self.preview_window, image=photo)
            label.image = photo
            label.pack(pady=10)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen para vista previa: {e}")
            self.preview_window.destroy()

    def load_events(self):
        for item in self.event_tree.get_children():
            self.event_tree.delete(item)
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)

        query = """
        SELECT evento_id, nombre_evento, fecha_hora_inicio, fecha_hora_fin, direccion_evento 
        FROM eventos 
        """
        events = self.db.execute_query(query, fetch=True)
        if events is not None:
            for event in events:
                self.event_tree.insert("", "end", values=(
                    event["evento_id"],
                    event["nombre_evento"],
                    event["fecha_hora_inicio"],
                    event["fecha_hora_fin"],
                    event["direccion_evento"]
                ))

        product_query = """
        SELECT r.renta_id, dr.cantidad, p.nombre, p.imagen_principal
        FROM rentas r
        JOIN detalle_renta dr ON r.renta_id = dr.renta_id
        JOIN productos p ON dr.producto_id = p.producto_id
        """
        products = self.db.execute_query(product_query, fetch=True)
        if products is not None:
            for product in products:
                try:
                    image = Image.open(product["imagen_principal"])
                    image = image.resize((70, 70), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    product_id = f"{product['renta_id']}_{product['nombre']}"
                    self.images[product_id] = photo
                    self.image_paths[product_id] = product["imagen_principal"]
                    self.product_tree.insert("", "end", values=(
                        product["renta_id"],
                        product["nombre"],
                        product["cantidad"],
                        "Ver Imagen"
                    ), image=photo)
                except Exception as e:
                    print(f"Error cargando imagen: {e}")
                    self.product_tree.insert("", "end", values=(
                        product["renta_id"],
                        product["nombre"],
                        product["cantidad"],
                        "Sin Imagen"
                    ))

    def add_event(self):
        query = """
        INSERT INTO eventos (cliente_id, nombre_evento, fecha_hora_inicio, fecha_hora_fin, direccion_evento)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            self.client_id.get(),
            self.name.get(),
            self.date_start.get(),
            self.date_end.get(),
            self.location.get()
        )
        if self.db.execute_query(query, params):
            messagebox.showinfo("Éxito", "¡Evento agregado!")
            self.load_events()
            self.clear_form()
        else:
            messagebox.showerror("Error", "No se pudo agregar el evento.")

    def update_event(self):
        selected = self.event_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Seleccione un evento para actualizar.")
            return
        event_id = self.event_tree.item(selected)["values"][0]
        query = """
        UPDATE eventos
        SET cliente_id = %s, nombre_evento = %s, fecha_hora_inicio = %s, fecha_hora_fin = %s, direccion_evento = %s
        WHERE evento_id = %s
        """
        params = (
            self.client_id.get(),
            self.name.get(),
            self.date_start.get(),
            self.date_end.get(),
            self.location.get(),
            event_id
        )
        if self.db.execute_query(query, params):
            messagebox.showinfo("Éxito", "¡Evento actualizado!")
            self.load_events()
            self.clear_form()
        else:
            messagebox.showerror("Error", "No se pudo actualizar el evento.")

    def delete_event(self):
        selected = self.event_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Seleccione un evento para eliminar.")
            return
        event_id = self.event_tree.item(selected)["values"][0]
        query = "DELETE FROM eventos WHERE evento_id = %s"
        if self.db.execute_query(query, (event_id,)):
            messagebox.showinfo("Éxito", "¡Evento eliminado!")
            self.load_events()
            self.clear_form()
        else:
            messagebox.showerror("Error", "No se pudo eliminar el evento.")

    def load_event(self, event):
        selected = self.event_tree.selection()
        if selected:
            event_id = self.event_tree.item(selected)["values"][0]
            query = "SELECT * FROM eventos WHERE evento_id = %s"
            event = self.db.execute_query(query, (event_id,), fetch=True)
            if event and len(event) > 0:
                event = event[0]
                self.clear_form()
                self.client_id.insert(0, event["cliente_id"])
                self.name.insert(0, event["nombre_evento"])
                self.date_start.insert(0, event["fecha_hora_inicio"])
                self.date_end.insert(0, event["fecha_hora_fin"])
                self.location.insert(0, event["direccion_evento"])
            else:
                messagebox.showerror("Error", "No se pudo cargar el evento.")

    def clear_form(self):
        self.client_id.delete(0, tk.END)
        self.name.delete(0, tk.END)
        self.date_start.delete(0, tk.END)
        self.date_end.delete(0, tk.END)
        self.location.delete(0, tk.END)