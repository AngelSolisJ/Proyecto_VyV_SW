import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from DB import BaseDatos
from Validacion_datos import validar_datos_entrada

class AplicacionUnificada:
    def __init__(self, master):
        self.master = master
        master.title("TiendApp | Sistema de Gestión de Inventario")
        master.geometry("900x600")
        master.configure(bg='#f0f0f0')
        
        self.db = BaseDatos()
        self.usuario_actual = None
        self.es_admin_actual = False
        
        self.contenedor = ttk.Frame(master)
        self.contenedor.pack(fill='both', expand=True)
        
        self.mostrar_login()
    
    def limpiar_contenedor(self):
        for widget in self.contenedor.winfo_children():
            widget.destroy()
    
    def mostrar_login(self):
        self.limpiar_contenedor()
        self.master.geometry("400x300")
        self.master.title("TiendApp | Inicio de Sesión")
        
        main_frame = ttk.Frame(self.contenedor, padding="40 40 40 40")
        main_frame.pack(expand=True, fill='both')
        
        titulo = ttk.Label(main_frame, text="Sistema de Inventario", 
                          font=('Arial', 16, 'bold'))
        titulo.pack(pady=(0, 30))
        
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(pady=10)
        
        ttk.Label(form_frame, text="Usuario:", font=('Arial', 10)).grid(
            row=0, column=0, sticky='w', padx=5, pady=10
        )
        self.usuario_entry = ttk.Entry(form_frame, width=25, font=('Arial', 10))
        self.usuario_entry.grid(row=0, column=1, padx=5, pady=10)
        self.usuario_entry.focus()
        
        ttk.Label(form_frame, text="Contraseña:", font=('Arial', 10)).grid(
            row=1, column=0, sticky='w', padx=5, pady=10
        )
        self.contraseña_entry = ttk.Entry(form_frame, width=25, show='*', font=('Arial', 10))
        self.contraseña_entry.grid(row=1, column=1, padx=5, pady=10)
        
        self.contraseña_entry.bind('<Return>', lambda e: self.validar_login())
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        btn_ingresar = tk.Button(btn_frame, text="Ingresar", 
                                command=self.validar_login,
                                bg='#4CAF50', fg='white',
                                font=('Arial', 10, 'bold'),
                                width=12, relief='raised', bd=2)
        btn_ingresar.pack(side='left', padx=5)
        
        btn_salir = tk.Button(btn_frame, text="Salir", 
                             command=self.master.quit,
                             font=('Arial', 10),
                             width=12, relief='raised', bd=2)
        btn_salir.pack(side='left', padx=5)
    
    def validar_login(self):
        usuario = self.usuario_entry.get().strip()
        contraseña = self.contraseña_entry.get()
        
        if not usuario or not contraseña:
            messagebox.showerror("Error", "Por favor ingrese usuario y contraseña.")
            return
        
        valido, id_usuario, es_admin = self.db.validar_usuario(usuario, contraseña)
        
        if valido:
            self.usuario_actual = usuario
            self.es_admin_actual = es_admin
            self.mostrar_inventario()
        else:
            messagebox.showerror("Error de Autenticación", 
                               "Usuario o contraseña incorrectos.")
            self.contraseña_entry.delete(0, tk.END)
            self.usuario_entry.focus()
    
    def mostrar_inventario(self):
        self.limpiar_contenedor()
        self.master.geometry("900x600")
        
        titulo = f"TiendApp | Gestión de Inventario - Usuario: {self.usuario_actual}"
        if self.es_admin_actual:
            titulo += " (Administrador)"
        self.master.title(titulo)
        
        self.id_var = tk.StringVar()
        self.nombre_var = tk.StringVar()
        self.categoria_var = tk.StringVar(value="Alimentos")
        self.cantidad_var = tk.StringVar()
        self.precio_var = tk.StringVar()
        
        input_frame = ttk.Frame(self.contenedor, padding="15 15 15 15")
        input_frame.pack(fill='x', padx=10, pady=10)
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
                ttk.Combobox(input_frame, textvariable=var, 
                             values=["Alimentos", "Bebidas", "Limpieza", "Electrónica", "Otros"], 
                             state="readonly").grid(
                    row=row_num, column=1, padx=5, pady=5, sticky='ew'
                )
            else:
                ttk.Entry(input_frame, textvariable=var, width=40).grid(
                    row=row_num, column=1, padx=5, pady=5, sticky='ew'
                )
        
        button_frame = ttk.Frame(self.contenedor, padding="10 10 10 10")
        button_frame.pack(fill='x', padx=10, pady=5)
        
        if self.es_admin_actual:
            button_frame.columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
            ttk.Button(button_frame, text="➕ Registrar", command=self.registrar, style='Accent.TButton').grid(row=0, column=0, padx=5, pady=5, sticky='ew')
            ttk.Button(button_frame, text="✏️ Actualizar", command=self.actualizar).grid(row=0, column=1, padx=5, pady=5, sticky='ew')
            ttk.Button(button_frame, text="🗑️ Eliminar", command=self.eliminar).grid(row=0, column=2, padx=5, pady=5, sticky='ew')
            ttk.Button(button_frame, text="📋 Consultar", command=self.consultar).grid(row=0, column=3, padx=5, pady=5, sticky='ew')
            ttk.Button(button_frame, text="👥 Usuarios", command=self.mostrar_usuarios, style='Accent.TButton').grid(row=0, column=4, padx=5, pady=5, sticky='ew')
            ttk.Button(button_frame, text="🚪 Salir", command=self.cerrar_sesion).grid(row=0, column=5, padx=5, pady=5, sticky='ew')
        else:
            button_frame.columnconfigure((0, 1, 2, 3, 4), weight=1)
            ttk.Button(button_frame, text="➕ Registrar", command=self.registrar, style='Accent.TButton').grid(row=0, column=0, padx=5, pady=5, sticky='ew')
            ttk.Button(button_frame, text="✏️ Actualizar", command=self.actualizar).grid(row=0, column=1, padx=5, pady=5, sticky='ew')
            ttk.Button(button_frame, text="🗑️ Eliminar", command=self.eliminar).grid(row=0, column=2, padx=5, pady=5, sticky='ew')
            ttk.Button(button_frame, text="📋 Consultar", command=self.consultar).grid(row=0, column=3, padx=5, pady=5, sticky='ew')
            ttk.Button(button_frame, text="🚪 Salir", command=self.cerrar_sesion).grid(row=0, column=4, padx=5, pady=5, sticky='ew')
        
        table_frame = ttk.Frame(self.contenedor, padding="10 10 10 10")
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)
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
    
    def cerrar_sesion(self):
        self.usuario_actual = None
        self.es_admin_actual = False
        self.mostrar_login()
    
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
    
    def mostrar_usuarios(self):
        if not self.es_admin_actual:
            messagebox.showerror("Error", "Solo los administradores pueden gestionar usuarios.")
            return
        
        self.limpiar_contenedor()
        self.master.geometry("800x500")
        self.master.title("TiendApp | Gestión de Usuarios")
        
        titulo_frame = ttk.Frame(self.contenedor, padding="10 10 10 10")
        titulo_frame.pack(fill='x')
        
        ttk.Label(titulo_frame, text="Gestión de Usuarios", font=('Arial', 16, 'bold')).pack()
        
        form_frame = ttk.Frame(self.contenedor, padding="10 10 10 10")
        form_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(form_frame, text="Usuario:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        usuario_entry = ttk.Entry(form_frame, width=20)
        usuario_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Contraseña:", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky='w', padx=5, pady=5)
        contraseña_entry = ttk.Entry(form_frame, width=20, show='*')
        contraseña_entry.grid(row=0, column=3, padx=5, pady=5)
        
        es_admin_var = tk.IntVar()
        ttk.Checkbutton(form_frame, text="Es Administrador", variable=es_admin_var).grid(row=0, column=4, padx=5, pady=5)
        
        table_frame = ttk.Frame(self.contenedor, padding="10 10 10 10")
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columnas = ("ID", "Usuario", "Tipo")
        tree_usuarios = ttk.Treeview(table_frame, columns=columnas, show='headings', height=12)
        
        for col in columnas:
            tree_usuarios.heading(col, text=col, anchor=tk.CENTER)
            tree_usuarios.column(col, anchor=tk.CENTER, width=200)
        
        tree_usuarios.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree_usuarios.yview)
        tree_usuarios.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        
        def actualizar_lista():
            for item in tree_usuarios.get_children():
                tree_usuarios.delete(item)
            
            usuarios = self.db.obtener_usuarios()
            for usuario in usuarios:
                tipo = "Administrador" if usuario[2] else "Usuario"
                tree_usuarios.insert('', tk.END, values=(usuario[0], usuario[1], tipo))
        
        def agregar_usuario():
            usuario = usuario_entry.get().strip()
            contraseña = contraseña_entry.get()
            
            if not usuario or not contraseña:
                messagebox.showerror("Error", "Complete todos los campos.")
                return
            
            exito, mensaje = self.db.registrar_usuario(usuario, contraseña, es_admin_var.get())
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                usuario_entry.delete(0, tk.END)
                contraseña_entry.delete(0, tk.END)
                es_admin_var.set(0)
                actualizar_lista()
            else:
                messagebox.showerror("Error", mensaje)
        
        def eliminar_usuario_seleccionado():
            seleccion = tree_usuarios.selection()
            if not seleccion:
                messagebox.showerror("Error", "Seleccione un usuario para eliminar.")
                return
            
            item = tree_usuarios.item(seleccion[0])
            id_usuario = item['values'][0]
            nombre_usuario = item['values'][1]
            
            if messagebox.askyesno("Confirmar", f"¿Eliminar usuario '{nombre_usuario}'?"):
                exito, mensaje = self.db.eliminar_usuario(id_usuario)
                if exito:
                    messagebox.showinfo("Éxito", mensaje)
                    actualizar_lista()
                else:
                    messagebox.showerror("Error", mensaje)
        
        btn_frame = ttk.Frame(self.contenedor, padding="10 10 10 10")
        btn_frame.pack(fill='x', padx=10, pady=5)
        
        btn_agregar = tk.Button(btn_frame, text="➕ Agregar Usuario", 
                               command=agregar_usuario,
                               bg='#4CAF50', fg='white',
                               font=('Arial', 10, 'bold'),
                               relief='raised', bd=2)
        btn_agregar.pack(side='left', padx=5)
        
        btn_eliminar = tk.Button(btn_frame, text="🗑️ Eliminar Seleccionado", 
                                command=eliminar_usuario_seleccionado,
                                font=('Arial', 10),
                                relief='raised', bd=2)
        btn_eliminar.pack(side='left', padx=5)
        
        btn_volver = tk.Button(btn_frame, text="⬅️ Volver al Inventario", 
                              command=self.mostrar_inventario,
                              font=('Arial', 10),
                              relief='raised', bd=2)
        btn_volver.pack(side='right', padx=5)
        
        actualizar_lista()

if __name__ == '__main__':
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('clam')
    
    style.configure('Accent.TButton', background='#4CAF50', foreground='white', font=('Arial', 10, 'bold'))
    style.map('Accent.TButton', background=[('active', '#66BB6A')])
    
    app = AplicacionUnificada(root)
    root.mainloop()
