import tkinter as tk
from tkinter import messagebox, ttk, filedialog, Toplevel
from database import Database
from PIL import Image, ImageTk
import os
import shutil

class CategoryManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Administrar Categorías")
        self.root.geometry("800x600")
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

        tk.Label(form_frame, text="Nombre:", bg="#f5f5dc").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.name = tk.Entry(form_frame)
        self.name.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Descripción:", bg="#f5f5dc").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.description = tk.Entry(form_frame)
        self.description.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Icono:", bg="#f5f5dc").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.image_path = tk.StringVar()
        self.image_entry = tk.Entry(form_frame, textvariable=self.image_path, state='readonly')
        self.image_entry.grid(row=2, column=1, padx=5, pady=5)
        tk.Button(form_frame, text="Seleccionar Imagen", command=self.select_image, bg="#4682b4", fg="#ffffff").grid(row=2, column=2, padx=5, pady=5)

        # Botones
        button_frame = tk.Frame(root, bg="#f5f5dc")
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Agregar", command=self.add_category, bg="#4682b4", fg="#ffffff").pack(side="left", padx=5)
        tk.Button(button_frame, text="Actualizar", command=self.update_category, bg="#4682b4", fg="#ffffff").pack(side="left", padx=5)
        tk.Button(button_frame, text="Eliminar", command=self.delete_category, bg="#4682b4", fg="#ffffff").pack(side="left", padx=5)

        # Treeview
        self.tree = ttk.Treeview(root, columns=("ID", "Nombre", "Descripción", "Icono"), show="headings", height=10)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Descripción", text="Descripción")
        self.tree.heading("Icono", text="Icono")
        self.tree.column("ID", width=50)
        self.tree.column("Nombre", width=150)
        self.tree.column("Descripción", width=250)
        self.tree.column("Icono", width=150)
        self.tree.pack(pady=10, padx=10, fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.load_category)
        self.tree.bind("<Double-1>", self.show_image_on_double_click)

        self.images = {}
        self.image_paths = {}
        self.preview_window = None
        self.load_categories()

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
        if item["values"][3] == "Ver Imagen":
            category_id = item["values"][0]
            image_path = self.image_paths.get(category_id)
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

    def load_categories(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        query = "SELECT categoria_id, nombre, descripcion, icono FROM categorias WHERE es_activa = TRUE"
        categories = self.db.execute_query(query, fetch=True)
        if categories is not None:
            for category in categories:
                print(f"Cargando categoría: {category}")
                try:
                    image = Image.open(category["icono"])
                    image = image.resize((70, 70), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    self.images[category["categoria_id"]] = photo
                    self.image_paths[category["categoria_id"]] = category["icono"]
                    self.tree.insert("", "end", values=(
                        category["categoria_id"],
                        category["nombre"],
                        category["descripcion"],
                        "Ver Imagen"
                    ), image=photo)
                except Exception as e:
                    print(f"Error cargando imagen: {e}")
                    self.tree.insert("", "end", values=(
                        category["categoria_id"],
                        category["nombre"],
                        category["descripcion"],
                        "Sin Imagen"
                    ))
        else:
            messagebox.showerror("Error", "No se pudieron cargar las categorías.")

    def add_category(self):
        image_path = self.save_image(self.image_path.get()) or 'images/placeholder.png'
        query = """
        INSERT INTO categorias (nombre, descripcion, icono, es_activa)
        VALUES (%s, %s, %s, TRUE)
        """
        params = (
            self.name.get(),
            self.description.get(),
            image_path
        )
        if self.db.execute_query(query, params):
            messagebox.showinfo("Éxito", "¡Categoría agregada!")
            self.load_categories()
            self.clear_form()
            if self.preview_window:
                self.preview_window.destroy()
        else:
            messagebox.showerror("Error", "No se pudo agregar la categoría.")

    def update_category(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Seleccione una categoría para actualizar.")
            return
        category_id = self.tree.item(selected)["values"][0]

        # Obtener la categoría actual para mantener la imagen existente si no se seleccionó una nueva
        current_query = "SELECT icono FROM categorias WHERE categoria_id = %s"
        current_category = self.db.execute_query(current_query, (category_id,), fetch=True)
        if not current_category:
            messagebox.showerror("Error", "No se pudo cargar la categoría actual.")
            return
        current_image = current_category[0]["icono"]

        # Solo guardar una nueva imagen si se seleccionó una nueva
        new_image_path = self.image_path.get()
        if new_image_path and new_image_path != current_image:  # Verificar si la imagen cambió
            image_path = self.save_image(new_image_path)
            if not image_path:  # Si no se pudo guardar la nueva imagen, mantener la existente
                image_path = current_image
        else:
            image_path = current_image  # Mantener la imagen existente

        query = """
        UPDATE categorias
        SET nombre = %s, descripcion = %s, icono = %s
        WHERE categoria_id = %s
        """
        params = (
            self.name.get(),
            self.description.get(),
            image_path,
            category_id
        )
        if self.db.execute_query(query, params):
            messagebox.showinfo("Éxito", "¡Categoría actualizada!")
            self.load_categories()
            self.clear_form()
            if self.preview_window:
                self.preview_window.destroy()
        else:
            messagebox.showerror("Error", "No se pudo actualizar la categoría.")

    def delete_category(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Seleccione una categoría para eliminar.")
            return
        category_id = self.tree.item(selected)["values"][0]
        query = "UPDATE categorias SET es_activa = FALSE WHERE categoria_id = %s"
        if self.db.execute_query(query, (category_id,)):
            messagebox.showinfo("Éxito", "¡Categoría eliminada!")
            self.load_categories()
            self.clear_form()
            if self.preview_window:
                self.preview_window.destroy()
        else:
            messagebox.showerror("Error", "No se pudo eliminar la categoría.")

    def load_category(self, event):
        selected = self.tree.selection()
        if selected:
            category_id = self.tree.item(selected)["values"][0]
            query = "SELECT * FROM categorias WHERE categoria_id = %s"
            category = self.db.execute_query(query, (category_id,), fetch=True)
            if category and len(category) > 0:
                category = category[0]
                self.clear_form()
                self.name.insert(0, category["nombre"])
                self.description.insert(0, category["descripcion"])
                self.image_path.set(category["icono"])
            else:
                messagebox.showerror("Error", "No se pudo cargar la categoría.")

    def clear_form(self):
        self.name.delete(0, tk.END)
        self.description.delete(0, tk.END)
        self.image_path.set("")
        if self.preview_window:
            self.preview_window.destroy()