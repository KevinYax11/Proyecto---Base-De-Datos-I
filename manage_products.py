import tkinter as tk
from tkinter import messagebox, ttk, filedialog, Toplevel
from database import Database
from PIL import Image, ImageTk
import os
import shutil

class ProductManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Administrar Productos")
        self.root.geometry("900x700")
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

        tk.Label(form_frame, text="Categoría:", bg="#f5f5dc").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.category_combobox = ttk.Combobox(form_frame, state="readonly")
        self.category_combobox.grid(row=0, column=1, padx=5, pady=5)
        self.category_map = self.load_categories()
        self.category_combobox["values"] = list(self.category_map.keys())
        if self.category_combobox["values"]:
            self.category_combobox.current(0)

        tk.Label(form_frame, text="Nombre:", bg="#f5f5dc").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.name = tk.Entry(form_frame)
        self.name.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Precio Diario:", bg="#f5f5dc").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.price = tk.Entry(form_frame)
        self.price.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Cantidad Total:", bg="#f5f5dc").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.quantity = tk.Entry(form_frame)
        self.quantity.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Imagen:", bg="#f5f5dc").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.image_path = tk.StringVar()
        self.image_entry = tk.Entry(form_frame, textvariable=self.image_path, state='readonly')
        self.image_entry.grid(row=4, column=1, padx=5, pady=5)
        tk.Button(form_frame, text="Seleccionar Imagen", command=self.select_image, bg="#4682b4", fg="#ffffff").grid(row=4, column=2, padx=5, pady=5)

        # Botones
        button_frame = tk.Frame(root, bg="#f5f5dc")
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Agregar", command=self.add_product, bg="#4682b4", fg="#ffffff").pack(side="left", padx=5)
        tk.Button(button_frame, text="Actualizar", command=self.update_product, bg="#4682b4", fg="#ffffff").pack(side="left", padx=5)
        tk.Button(button_frame, text="Eliminar", command=self.delete_product, bg="#4682b4", fg="#ffffff").pack(side="left", padx=5)

        # Treeview
        self.tree = ttk.Treeview(root, columns=("ID", "Nombre", "Precio", "Cantidad", "Imagen"), show="headings", height=10)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Precio", text="Precio Diario")
        self.tree.heading("Cantidad", text="Cantidad Total")
        self.tree.heading("Imagen", text="Imagen")
        self.tree.column("ID", width=50)
        self.tree.column("Nombre", width=200)
        self.tree.column("Precio", width=100)
        self.tree.column("Cantidad", width=100)
        self.tree.column("Imagen", width=150)
        self.tree.pack(pady=10, padx=10, fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.load_product)
        self.tree.bind("<Double-1>", self.show_image_on_double_click)

        self.images = {}
        self.image_paths = {}
        self.preview_window = None
        self.load_products()

    def load_categories(self):
        query = "SELECT categoria_id, nombre FROM categorias WHERE es_activa = TRUE"
        categories = self.db.execute_query(query, fetch=True)
        category_map = {}
        if categories:
            for category in categories:
                category_map[category["nombre"]] = category["categoria_id"]
        return category_map

    def select_image(self):
        initial_dir = os.path.join(os.getcwd(), "images")
        file_path = filedialog.askopenfilename(
            initialdir=initial_dir,
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if file_path:
            self.image_path.set(file_path)
            print(f"Imagen seleccionada: {file_path}")
            self.show_image_preview(file_path)

    def show_image_on_double_click(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected)
        if item["values"][4] == "Ver Imagen":
            product_id = item["values"][0]
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

    def save_image(self, image_path):
        if not image_path:
            return None
        filename = os.path.basename(image_path)
        destination = os.path.join("images", filename)
        os.makedirs("images", exist_ok=True)
        shutil.copy(image_path, destination)
        print(f"Imagen guardada en: {destination}")
        return destination

    def load_products(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        query = """
        SELECT producto_id, nombre, precio_diario, cantidad_total, imagen_principal 
        FROM productos 
        WHERE es_activo = TRUE
        """
        products = self.db.execute_query(query, fetch=True)
        if products is not None:
            for product in products:
                print(f"Cargando producto: {product}")
                try:
                    image = Image.open(product["imagen_principal"])
                    image = image.resize((70, 70), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    self.images[product["producto_id"]] = photo
                    self.image_paths[product["producto_id"]] = product["imagen_principal"]
                    self.tree.insert("", "end", values=(
                        product["producto_id"],
                        product["nombre"],
                        product["precio_diario"],
                        product["cantidad_total"],
                        "Ver Imagen"
                    ), image=photo)
                except Exception as e:
                    print(f"Error cargando imagen: {e}")
                    self.tree.insert("", "end", values=(
                        product["producto_id"],
                        product["nombre"],
                        product["precio_diario"],
                        product["cantidad_total"],
                        "Sin Imagen"
                    ))
        else:
            messagebox.showerror("Error", "No se pudieron cargar los productos.")

    def add_product(self):
        selected_category = self.category_combobox.get()
        if not selected_category:
            messagebox.showerror("Error", "Por favor seleccione una categoría.")
            return
        category_id = self.category_map.get(selected_category)

        image_path = self.save_image(self.image_path.get()) or 'images/placeholder.png'
        query = """
        INSERT INTO productos (categoria_id, nombre, precio_diario, cantidad_total, cantidad_disponible, imagen_principal, es_activo)
        VALUES (%s, %s, %s, %s, %s, %s, TRUE)
        """
        params = (
            category_id,
            self.name.get(),
            self.price.get(),
            self.quantity.get(),
            self.quantity.get(),
            image_path
        )
        if self.db.execute_query(query, params):
            messagebox.showinfo("Éxito", "¡Producto agregado!")
            self.load_products()
            self.clear_form()
            if self.preview_window:
                self.preview_window.destroy()
        else:
            messagebox.showerror("Error", "No se pudo agregar el producto.")

    def update_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Seleccione un producto para actualizar.")
            return
        product_id = self.tree.item(selected)["values"][0]

        selected_category = self.category_combobox.get()
        if not selected_category:
            messagebox.showerror("Error", "Por favor seleccione una categoría.")
            return
        category_id = self.category_map.get(selected_category)

        # Obtener el producto actual para mantener la imagen existente
        current_query = "SELECT imagen_principal FROM productos WHERE producto_id = %s"
        current_product = self.db.execute_query(current_query, (product_id,), fetch=True)
        if not current_product:
            messagebox.showerror("Error", "No se pudo cargar el producto actual.")
            return
        current_image = current_product[0]["imagen_principal"]

        # Solo guardar una nueva imagen si se seleccionó una nueva
        new_image_path = self.image_path.get()
        if new_image_path and new_image_path != current_image:
            image_path = self.save_image(new_image_path)
            if not image_path:
                image_path = current_image
        else:
            image_path = current_image

        query = """
        UPDATE productos
        SET categoria_id = %s, nombre = %s, precio_diario = %s, cantidad_total = %s, cantidad_disponible = %s, imagen_principal = %s
        WHERE producto_id = %s
        """
        params = (
            category_id,
            self.name.get(),
            self.price.get(),
            self.quantity.get(),
            self.quantity.get(),
            image_path,
            product_id
        )
        if self.db.execute_query(query, params):
            messagebox.showinfo("Éxito", "¡Producto actualizado!")
            self.load_products()
            self.clear_form()
            if self.preview_window:
                self.preview_window.destroy()
        else:
            messagebox.showerror("Error", "No se pudo actualizar el producto.")

    def delete_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Seleccione un producto para eliminar.")
            return
        product_id = self.tree.item(selected)["values"][0]
        query = "UPDATE productos SET es_activo = FALSE WHERE producto_id = %s"
        if self.db.execute_query(query, (product_id,)):
            messagebox.showinfo("Éxito", "¡Producto eliminado!")
            self.load_products()
            self.clear_form()
            if self.preview_window:
                self.preview_window.destroy()
        else:
            messagebox.showerror("Error", "No se pudo eliminar el producto.")

    def load_product(self, event):
        selected = self.tree.selection()
        if selected:
            product_id = self.tree.item(selected)["values"][0]
            query = "SELECT * FROM productos WHERE producto_id = %s"
            product = self.db.execute_query(query, (product_id,), fetch=True)
            if product and len(product) > 0:
                product = product[0]
                self.clear_form()
                for cat_name, cat_id in self.category_map.items():
                    if cat_id == product["categoria_id"]:
                        self.category_combobox.set(cat_name)
                        break
                self.name.insert(0, product["nombre"])
                self.price.insert(0, product["precio_diario"])
                self.quantity.insert(0, product["cantidad_total"])
                self.image_path.set(product["imagen_principal"])
            else:
                messagebox.showerror("Error", "No se pudo cargar el producto.")

    def clear_form(self):
        if self.category_combobox["values"]:
            self.category_combobox.current(0)
        self.name.delete(0, tk.END)
        self.price.delete(0, tk.END)
        self.quantity.delete(0, tk.END)
        self.image_path.set("")
        if self.preview_window:
            self.preview_window.destroy()