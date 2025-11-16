# app.py
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk  # Importar ttk para un look and feel moderno

# Importar lógica de negocio y persistencia
from DB import BaseDatos 
from Validacion_datos import validar_datos_entrada 

class TiendaAppGUI:
    def __init__(self, master):
        self.master = master
        master.title("TiendApp | Gestión de Inventario")
        master.configure(bg='#f0f0f0')
        
        self.db = BaseDatos()

        # --- Variables de control ---
        self.id_var = tk.StringVar()
        self.nombre_var = tk.StringVar()
        self.categoria_var = tk.StringVar(value="Alimentos") 
        self.cantidad_var = tk.StringVar()
        self.precio_var = tk.StringVar()

       
        master.columnconfigure(0, weight=1)
        master.rowconfigure(2, weight=1) 

        input_frame = ttk.Frame(master, padding="15 15 15 15")
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        input_frame.columnconfigure(1, weight=1) 
        
        campos = [
            ("ID:", self.id_var, 0),
            ("Nombre:", self.nombre_var, 1),
            ("Categoría:", self.categoria_var, 2),
            ("Cantidad:", self.cantidad_var, 3),
            ("Precio:", self.precio_var, 4)
        ]

        for i, (label_text, var, row_num) in enumerate(campos):
            ttk.Label(input_frame, text=label_text, font=('Arial', 10, 'bold')).grid(
                row=row_num, column=0, sticky='w', padx=5, pady=5
            )
            if label_text == "Categoría:":
                ttk.Combobox(input_frame, textvariable=var, values=["Alimentos", "Bebidas", "Limpieza", "Otros"], state="readonly").grid(
                    row=row_num, column=1, padx=5, pady=5, sticky='ew'
                )
            else:
                ttk.Entry(input_frame, textvariable=var, width=40).grid(
                    row=row_num, column=1, padx=5, pady=5, sticky='ew'
                )

    
        button_frame = ttk.Frame(master, padding="10 10 10 10")
        button_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        button_frame.columnconfigure((0, 1, 2, 3), weight=1)
        
        ttk.Button(button_frame, text="➕ Registrar", command=self.registrar, style='Accent.TButton').grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        ttk.Button(button_frame, text="✏️ Actualizar", command=self.actualizar).grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        ttk.Button(button_frame, text="🗑️ Eliminar (ID)", command=self.eliminar).grid(row=0, column=2, padx=5, pady=5, sticky='ew')
        ttk.Button(button_frame, text="📋 Consultar Todo", command=self.consultar).grid(row=0, column=3, padx=5, pady=5, sticky='ew')


        table_frame = ttk.Frame(master, padding="10 10 10 10")
        table_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)


        columnas = ("ID", "Nombre", "Categoría", "Cantidad", "Precio")
        self.lista_inventario = ttk.Treeview(table_frame, columns=columnas, show='headings')
        
        for col in columnas:
            self.lista_inventario.heading(col, text=col, anchor=tk.CENTER)
            self.lista_inventario.column(col, anchor=tk.CENTER, width=100)
            
        self.lista_inventario.grid(row=0, column=0, sticky='nsew')
        

        scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.lista_inventario.yview)
        self.lista_inventario.configure(yscrollcommand=scroll.set)
        scroll.grid(row=0, column=1, sticky='ns')

        self.consultar() 
        

    def registrar(self):
        id_p = self.id_var.get()
        nombre = self.nombre_var.get()
        cantidad = self.cantidad_var.get()
        precio = self.precio_var.get()
        categoria = self.categoria_var.get()

        valido, mensaje = validar_datos_entrada(cantidad, precio, nombre)

        if not valido:
            messagebox.showerror("Error de Validación", mensaje)
            return
        
        exito, mensaje = self.db.registrar_producto(id_p, nombre, categoria, int(cantidad), float(precio))

        if exito:
            messagebox.showinfo("Éxito", mensaje)
            self.limpiar_campos()
            self.consultar()
        else:
            messagebox.showerror("Error de Registro", mensaje)
            
    def consultar(self):

        for item in self.lista_inventario.get_children():
            self.lista_inventario.delete(item)
            
        productos = self.db.obtener_productos()
        
        for producto in productos:
            self.lista_inventario.insert('', tk.END, values=producto)
            
    def actualizar(self):
        id_p = self.id_var.get()
        nombre = self.nombre_var.get()
        cantidad = self.cantidad_var.get()
        precio = self.precio_var.get()
        categoria = self.categoria_var.get()

        if not id_p:
            messagebox.showerror("Error", "Debe ingresar el ID del producto a actualizar.")
            return

        valido, mensaje = validar_datos_entrada(cantidad, precio, nombre)

        if not valido:
            messagebox.showerror("Error de Validación", mensaje)
            return

        exito, mensaje = self.db.actualizar_producto(id_p, nombre, categoria, int(cantidad), float(precio))
        
        if exito:
            messagebox.showinfo("Éxito", mensaje)
            self.limpiar_campos()
            self.consultar()
        else:
            messagebox.showerror("Error de Actualización", mensaje)

    def eliminar(self):
 
        id_p = self.id_var.get()
        if not id_p:
             messagebox.showerror("Error", "Debe ingresar el ID del producto a eliminar.")
             return
             
        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar el producto con ID: {id_p}?"):
            exito, mensaje = self.db.eliminar_producto(id_p)
            
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                self.limpiar_campos()
                self.consultar()
            else:
                messagebox.showerror("Error de Eliminación", mensaje)

    def limpiar_campos(self):
        self.id_var.set("")
        self.nombre_var.set("")
        self.categoria_var.set("Alimentos")
        self.cantidad_var.set("")
        self.precio_var.set("")

if __name__ == '__main__':
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('clam') 
    
    style.configure('Accent.TButton', background='#4CAF50', foreground='white', font=('Arial', 10, 'bold'))
    style.map('Accent.TButton', background=[('active', '#66BB6A')])

    app = TiendaAppGUI(root)
    root.mainloop()