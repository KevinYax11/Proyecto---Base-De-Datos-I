import tkinter as tk
from tkinter import messagebox, ttk, Toplevel
from database import Database
from PIL import Image, ImageTk

class RentalManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Administrar Rentas")
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

        tk.Label(form_frame, text="Evento ID:", bg="#f5f5dc").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.event_id = tk.Entry(form_frame)
        self.event_id.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Fecha Entrega:", bg="#f5f5dc").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.start_date = tk.Entry(form_frame)
        self.start_date.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Fecha Devolución:", bg="#f5f5dc").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.end_date = tk.Entry(form_frame)
        self.end_date.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Producto ID:", bg="#f5f5dc").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.product_id = tk.Entry(form_frame)
        self.product_id.grid(row=4, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Cantidad:", bg="#f5f5dc").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.quantity = tk.Entry(form_frame)
        self.quantity.grid(row=5, column=1, padx=5, pady=5)

        # Botones
        button_frame = tk.Frame(root, bg="#f5f5dc")
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Agregar Renta", command=self.add_rental, bg="#4682b4", fg="#ffffff").pack(side="left", padx=5)
        tk.Button(button_frame, text="Actualizar Renta", command=self.update_rental, bg="#4682b4", fg="#ffffff").pack(side="left", padx=5)
        tk.Button(button_frame, text="Eliminar Renta", command=self.delete_rental, bg="#4682b4", fg="#ffffff").pack(side="left", padx=5)

        # Treeview para Rentas
        self.rental_tree = ttk.Treeview(root, columns=("ID", "Cliente", "Evento", "Fecha Entrega", "Fecha Devolución"), show="headings", height=5)
        self.rental_tree.heading("ID", text="ID")
        self.rental_tree.heading("Cliente", text="Cliente ID")
        self.rental_tree.heading("Evento", text="Evento ID")
        self.rental_tree.heading("Fecha Entrega", text="Fecha Entrega")
        self.rental_tree.heading("Fecha Devolución", text="Fecha Devolución")
        self.rental_tree.column("ID", width=50)
        self.rental_tree.column("Cliente", width=100)
        self.rental_tree.column("Evento", width=100)
        self.rental_tree.column("Fecha Entrega", width=150)
        self.rental_tree.column("Fecha Devolución", width=150)
        self.rental_tree.pack(pady=10, padx=10, fill="both")
        self.rental_tree.bind("<<TreeviewSelect>>", self.load_rental)

        # Treeview para Detalles de Productos
        tk.Label(root, text="Detalles de Productos", font=('Helvetica', 12, 'bold'), bg="#f5f5dc").pack(pady=5)
        self.detail_tree = ttk.Treeview(root, columns=("Renta ID", "Producto", "Cantidad", "Imagen"), show="headings", height=5)
        self.detail_tree.heading("Renta ID", text="Renta ID")
        self.detail_tree.heading("Producto", text="Producto")
        self.detail_tree.heading("Cantidad", text="Cantidad")
        self.detail_tree.heading("Imagen", text="Imagen")
        self.detail_tree.column("Renta ID", width=100)
        self.detail_tree.column("Producto", width=200)
        self.detail_tree.column("Cantidad", width=100)
        self.detail_tree.column("Imagen", width=150)
        self.detail_tree.pack(pady=10, padx=10, fill="both", expand=True)
        self.detail_tree.bind("<Double-1>", self.show_image_on_double_click)

        self.images = {}
        self.image_paths = {}
        self.preview_window = None
        self.load_rentals()

    def show_image_on_double_click(self, event):
        selected = self.detail_tree.selection()
        if not selected:
            return
        item = self.detail_tree.item(selected)
        if item["values"][3] == "Ver Imagen":
            renta_id = item["values"][0]
            product_name = item["values"][1]
            detail_id = f"{renta_id}_{product_name}"
            image_path = self.image_paths.get(detail_id)
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

    def load_rentals(self):
        for item in self.rental_tree.get_children():
            self.rental_tree.delete(item)
        for item in self.detail_tree.get_children():
            self.detail_tree.delete(item)

        query = """
        SELECT renta_id, cliente_id, evento_id, fecha_entrega_estimada, fecha_devolucion_estimada 
        FROM rentas 
        """
        rentals = self.db.execute_query(query, fetch=True)
        if rentals is not None:
            for rental in rentals:
                self.rental_tree.insert("", "end", values=(
                    rental["renta_id"],
                    rental["cliente_id"],
                    rental["evento_id"],
                    rental["fecha_entrega_estimada"],
                    rental["fecha_devolucion_estimada"]
                ))

        detail_query = """
        SELECT dr.renta_id, dr.cantidad, p.nombre, p.imagen_principal
        FROM detalle_renta dr
        JOIN productos p ON dr.producto_id = p.producto_id
        """
        details = self.db.execute_query(detail_query, fetch=True)
        if details is not None:
            for detail in details:
                try:
                    image = Image.open(detail["imagen_principal"])
                    image = image.resize((70, 70), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    detail_id = f"{detail['renta_id']}_{detail['nombre']}"
                    self.images[detail_id] = photo
                    self.image_paths[detail_id] = detail["imagen_principal"]
                    self.detail_tree.insert("", "end", values=(
                        detail["renta_id"],
                        detail["nombre"],
                        detail["cantidad"],
                        "Ver Imagen"
                    ), image=photo)
                except Exception as e:
                    print(f"Error cargando imagen: {e}")
                    self.detail_tree.insert("", "end", values=(
                        detail["renta_id"],
                        detail["nombre"],
                        detail["cantidad"],
                        "Sin Imagen"
                    ))

    def add_rental(self):
        rental_query = """
        INSERT INTO rentas (cliente_id, evento_id, fecha_entrega_estimada, fecha_devolucion_estimada, codigo_renta, subtotal, impuestos, total, estado_pago, estado_renta)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        rental_params = (
            self.client_id.get(),
            self.event_id.get(),
            self.start_date.get(),
            self.end_date.get(),
            f"RENTA-{self.client_id.get()}-{self.event_id.get()}",
            0.00,
            0.00,
            0.00,
            'pendiente',
            'reservado'
        )
        rental_id = None
        cursor = self.db.connection.cursor(dictionary=True)
        try:
            cursor.execute(rental_query, rental_params)
            self.db.connection.commit()
            cursor.execute("SELECT LAST_INSERT_ID() as id")
            rental_id = cursor.fetchone()["id"]
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar la renta: {e}")
            return
        finally:
            cursor.close()

        detail_query = """
        INSERT INTO detalle_renta (renta_id, producto_id, cantidad, precio_unitario, precio_total, dias_renta)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        detail_params = (rental_id, self.product_id.get(), self.quantity.get(), 0.00, 0.00, 1)
        if self.db.execute_query(detail_query, detail_params):
            messagebox.showinfo("Éxito", "¡Renta agregada!")
            self.load_rentals()
            self.clear_form()
        else:
            messagebox.showerror("Error", "No se pudo agregar el detalle de la renta.")

    def update_rental(self):
        selected = self.rental_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Seleccione una renta para actualizar.")
            return
        rental_id = self.rental_tree.item(selected)["values"][0]

        # Actualizar la renta
        rental_query = """
        UPDATE rentas
        SET cliente_id = %s, evento_id = %s, fecha_entrega_estimada = %s, fecha_devolucion_estimada = %s
        WHERE renta_id = %s
        """
        rental_params = (
            self.client_id.get(),
            self.event_id.get(),
            self.start_date.get(),
            self.end_date.get(),
            rental_id
        )
        if not self.db.execute_query(rental_query, rental_params):
            messagebox.showerror("Error", "No se pudo actualizar la renta.")
            return

        # Actualizar el detalle de la renta (borrar e insertar nuevo)
        delete_detail_query = "DELETE FROM detalle_renta WHERE renta_id = %s"
        if not self.db.execute_query(delete_detail_query, (rental_id,)):
            messagebox.showerror("Error", "No se pudo actualizar el detalle de la renta.")
            return

        detail_query = """
        INSERT INTO detalle_renta (renta_id, producto_id, cantidad, precio_unitario, precio_total, dias_renta)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        detail_params = (rental_id, self.product_id.get(), self.quantity.get(), 0.00, 0.00, 1)
        if self.db.execute_query(detail_query, detail_params):
            messagebox.showinfo("Éxito", "¡Renta actualizada!")
            self.load_rentals()
            self.clear_form()
        else:
            messagebox.showerror("Error", "No se pudo actualizar el detalle de la renta.")

    def delete_rental(self):
        selected = self.rental_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Seleccione una renta para eliminar.")
            return
        rental_id = self.rental_tree.item(selected)["values"][0]
        query = "DELETE FROM rentas WHERE renta_id = %s"
        if self.db.execute_query(query, (rental_id,)):
            messagebox.showinfo("Éxito", "¡Renta eliminada!")
            self.load_rentals()
            self.clear_form()
        else:
            messagebox.showerror("Error", "No se pudo eliminar la renta.")

    def load_rental(self, event):
        selected = self.rental_tree.selection()
        if selected:
            rental_id = self.rental_tree.item(selected)["values"][0]
            query = "SELECT * FROM rentas WHERE renta_id = %s"
            rental = self.db.execute_query(query, (rental_id,), fetch=True)
            if rental and len(rental) > 0:
                rental = rental[0]
                self.clear_form()
                self.client_id.insert(0, rental["cliente_id"])
                self.event_id.insert(0, rental["evento_id"])
                self.start_date.insert(0, rental["fecha_entrega_estimada"])
                self.end_date.insert(0, rental["fecha_devolucion_estimada"])

                detail_query = "SELECT producto_id, cantidad FROM detalle_renta WHERE renta_id = %s"
                details = self.db.execute_query(detail_query, (rental_id,), fetch=True)
                if details and len(details) > 0:
                    self.product_id.insert(0, details[0]["producto_id"])
                    self.quantity.insert(0, details[0]["cantidad"])
            else:
                messagebox.showerror("Error", "No se pudo cargar la renta.")

    def clear_form(self):
        self.client_id.delete(0, tk.END)
        self.event_id.delete(0, tk.END)
        self.start_date.delete(0, tk.END)
        self.end_date.delete(0, tk.END)
        self.product_id.delete(0, tk.END)
        self.quantity.delete(0, tk.END)