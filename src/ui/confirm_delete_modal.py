import customtkinter as ctk


class ConfirmDeleteModal(ctk.CTkToplevel):
    """Modal de confirmación antes de eliminar un producto."""

    def __init__(self, master, nombre_producto, on_confirm):
        super().__init__(master)
        self.on_confirm = on_confirm

        self.title("Confirmar eliminación")
        self.geometry("420x260")
        self.minsize(420, 260)
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color="#f8f9fa")
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build(nombre_producto)
        self.after(50, self._post_init)

    def _post_init(self):
        self.lift()
        self.focus_force()
        self.grab_set()

    def _build(self, nombre):
        # Franja roja
        header = ctk.CTkFrame(self, fg_color="#dc3545", corner_radius=0, height=60)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header, text="Eliminar Producto",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="white"
                     ).grid(row=0, column=0, padx=24, sticky="w", pady=(10, 2))
        ctk.CTkLabel(header, text="Esta acción no se puede deshacer",
                     font=ctk.CTkFont(size=11),
                     text_color="#f5c6cb"
                     ).grid(row=1, column=0, padx=24, sticky="w", pady=(0, 8))

        # Cuerpo
        card = ctk.CTkFrame(self, fg_color="#ffffff",
                            corner_radius=12, border_width=1, border_color="#dee2e6")
        card.grid(row=1, column=0, padx=20, pady=(16, 12), sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(card,
                     text=f"¿Estás seguro de que deseas eliminar\nel producto \"{nombre}\"?",
                     font=ctk.CTkFont(size=13), text_color="#333333",
                     justify="center"
                     ).pack(expand=True)

        # Botones
        btn_bar = ctk.CTkFrame(self, fg_color="#f8f9fa",
                               border_width=1, border_color="#dee2e6",
                               corner_radius=0, height=60)
        btn_bar.grid(row=2, column=0, sticky="ew")
        btn_bar.grid_propagate(False)
        btn_bar.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(btn_bar, text="Cancelar",
                      fg_color="transparent", border_width=2, border_color="#dee2e6",
                      text_color="#333333", hover_color="#e9ecef",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      height=38, corner_radius=8,
                      command=self.destroy
                      ).grid(row=0, column=0, padx=(16, 8), pady=11, sticky="ew")

        ctk.CTkButton(btn_bar, text="Sí, eliminar",
                      fg_color="#dc3545", hover_color="#a71d2a",
                      text_color="white", font=ctk.CTkFont(size=13, weight="bold"),
                      height=38, corner_radius=8,
                      command=self._confirmar
                      ).grid(row=0, column=1, padx=(8, 16), pady=11, sticky="ew")

    def _confirmar(self):
        self.grab_release()
        self.destroy()
        self.on_confirm()