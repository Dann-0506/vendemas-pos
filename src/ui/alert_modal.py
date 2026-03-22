import customtkinter as ctk


class AlertModal(ctk.CTkToplevel):
    """Modal de alerta para errores de validación."""

    def __init__(self, master, mensaje):
        super().__init__(master)
        self.title("Error de validación")
        self.geometry("380x220")
        self.minsize(380, 220)
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color="#f8f9fa")
        self.protocol("WM_DELETE_WINDOW", self.destroy)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Franja naranja
        header = ctk.CTkFrame(self, fg_color="#e69500", corner_radius=0, height=50)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text="Campo inválido",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color="white"
                     ).grid(row=0, column=0, padx=20, sticky="w", pady=14)

        # Mensaje
        card = ctk.CTkFrame(self, fg_color="#ffffff",
                            corner_radius=12, border_width=1, border_color="#dee2e6")
        card.grid(row=1, column=0, padx=20, pady=(12, 10), sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(card, text=mensaje,
                     font=ctk.CTkFont(size=13), text_color="#333333",
                     justify="center", wraplength=320
                     ).pack(expand=True)

        # Botón
        btn_bar = ctk.CTkFrame(self, fg_color="#f8f9fa",
                               border_width=1, border_color="#dee2e6",
                               corner_radius=0, height=54)
        btn_bar.grid(row=2, column=0, sticky="ew")
        btn_bar.grid_propagate(False)
        btn_bar.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(btn_bar, text="Entendido",
                      fg_color="#007bff", hover_color="#0056b3",
                      text_color="white", font=ctk.CTkFont(size=13, weight="bold"),
                      height=36, corner_radius=8,
                      command=self.destroy
                      ).grid(row=0, column=0, padx=16, pady=9, sticky="ew")

        self.after(50, lambda: (self.lift(), self.focus_force(), self.grab_set()))