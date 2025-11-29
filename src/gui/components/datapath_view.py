import tkinter as tk
from tkinter import font

class DatapathView(tk.Canvas):
    def __init__(self, master, registers, **kwargs):
        super().__init__(master, bg='white', highlightthickness=0, **kwargs)
        self.registers_ref = registers

        # --- Mundo Virtual (Largura aumentada para roteamento limpo) ---
        self.VW = 1500
        self.VH = 1600

        # --- Grid Horizontal (X) ---
        self.X_MAR_MBR = 200    # Esquerda: Componentes de Memória
        self.X_BUS_C   = 450    # Barramento C (Escrita)
        self.X_REGS    = 750    # Centro dos Registradores
        self.X_BUS_A   = 1050   # Barramento A (Leitura)
        self.X_BUS_B   = 1250   # Barramento B (Leitura)

        # --- Cores ---
        self.C_OFF      = "#333333"
        self.C_BUS_A    = "#0000FF" # Azul
        self.C_BUS_B    = "#00AA00" # Verde
        self.C_BUS_C    = "#FF0000" # Vermelho
        self.C_BG_REG   = "#FFFFFF"
        self.C_ACTIVE   = "#FFFFA0" # Amarelo Claro
        self.C_LATCH    = "#F0F0F0"

        self.signals = None
        self.reg_values = {}

        # Ordem da Pilha de Registradores
        self.stack_order = [
            ("PC", 2), ("AC", 4), ("SP", 3), 
            ("IR", 5), ("TIR", 6), 
            ("0", 7), ("+1", 8), ("-1", 9), 
            ("AMASK", 10), ("SMASK", 11)
        ]

        self.bind("<Configure>", self.on_resize)

    def update_state(self, signals, reg_values):
        self.signals = signals
        self.reg_values = reg_values
        self.draw()

    def on_resize(self, event):
        self.draw()

    # --- Helpers de Geometria ---
    def t(self, x, y):
        """Escala coordenadas virtuais para a tela."""
        w_win = self.winfo_width()
        h_win = self.winfo_height()
        scale = min(w_win / self.VW, h_win / self.VH) * 0.95
        off_x = (w_win - self.VW * scale) / 2
        off_y = (h_win - self.VH * scale) / 2
        return off_x + x * scale, off_y + y * scale

    def get_font(self, size, bold=False):
        s = min(self.winfo_width()/self.VW, self.winfo_height()/self.VH)
        fs = max(8, int(size * s * 1.5))
        return font.Font(family="Helvetica", size=fs, weight="bold" if bold else "normal")

    # --- Primitivas de Desenho ---
    def rect(self, x, y, w, h, fill="white", outline="black", width=2, text=None, val=None):
        x0, y0 = self.t(x - w/2, y - h/2)
        x1, y1 = self.t(x + w/2, y + h/2)
        self.create_rectangle(x0, y0, x1, y1, fill=fill, outline=outline, width=width)
        if text:
            f = self.get_font(12, True)
            self.create_text(*self.t(x - w/2 + 10, y), text=text, anchor="w", font=f)
        if val is not None:
            f = self.get_font(12, False)
            self.create_text(*self.t(x + w/2 - 10, y), text=val, anchor="e", font=f, fill="#555")

    def wire(self, pts, color, width=2, arrow=None):
        tk_pts = [c for p in pts for c in self.t(*p)]
        # Arrowshape refinado para parecer técnico
        self.create_line(tk_pts, fill=color, width=width, arrow=arrow, 
                         arrowshape=(10, 12, 4), joinstyle=tk.MITER, capstyle=tk.ROUND)

    def dot(self, x, y, color, r=5):
        cx, cy = self.t(x, y)
        self.create_oval(cx-r, cy-r, cx+r, cy+r, fill=color, outline="black")

    def trapezoid(self, x, y, w_top, w_bot, h, fill="white", text=None):
        pts = [
            (x - w_top/2, y), (x + w_top/2, y),
            (x + w_bot/2, y + h), (x - w_bot/2, y + h)
        ]
        tk_pts = [c for p in pts for c in self.t(*p)]
        self.create_polygon(tk_pts, fill=fill, outline="black", width=2)
        if text:
            self.create_text(*self.t(x, y + h/2), text=text, font=self.get_font(11, True))

    def ula_shape(self, x, y, fill="white", text=None, subtext=None):
        """Desenha a ULA (V com recorte)."""
        w_outer = 90
        w_inner = 30
        h_notch = 30
        h_total = 100
        w_tip = 30

        pts = [
            (x - w_outer, y),               # Topo Esq Externo
            (x - w_inner, y + h_notch),     # Notch Esq
            (x + w_inner, y + h_notch),     # Notch Dir
            (x + w_outer, y),               # Topo Dir Externo
            (x + w_tip, y + h_total),       # Ponta Dir
            (x - w_tip, y + h_total)        # Ponta Esq
        ]
        tk_pts = [c for p in pts for c in self.t(*p)]
        self.create_polygon(tk_pts, fill=fill, outline="black", width=2)
        
        if text:
            self.create_text(*self.t(x, y + 60), text=text, font=self.get_font(16, True))
        if subtext:
            self.create_text(*self.t(x + w_outer + 10, y + 50), text=subtext, 
                             font=self.get_font(10), fill="blue", anchor="w")

    # --- Lógica de Desenho ---
    def draw(self):
        self.delete("all")
        if self.winfo_width() < 100: return

        sig = self.signals
        
        # Cores Ativas
        ca = self.C_BUS_A if (sig and not sig.amux) else self.C_OFF
        cb = self.C_BUS_B if sig else self.C_OFF
        cc = self.C_BUS_C if (sig and sig.enc) else self.C_OFF

        # --- Topo e Fundo do Diagrama ---
        Y_TOP = 40
        Y_BOT_LOOP = 1450 # Ponto mais baixo onde o Shifter retorna
        
        # 1. Barramento C (A linha vertical principal)
        # Ele sobe a partir da conexão do Shifter (ver passo 8)
        self.wire([(self.X_BUS_C, Y_BOT_LOOP - 50), (self.X_BUS_C, Y_TOP)], color=cc, width=4, arrow=tk.LAST)
        self.create_text(*self.t(self.X_BUS_C, Y_TOP-20), text="Bus C", font=self.get_font(14, True))

        # 2. Pilha de Registradores
        y_r = 80
        W_REG = 200
        H_REG = 50
        GAP = 20

        # Barramentos A e B descem até os Latches
        # Calculamos onde começam os latches
        total_regs_h = len(self.stack_order) * (H_REG + GAP)
        Y_LATCHES = y_r + total_regs_h + 20

        # Desenhar Linhas Verticais A e B
        self.wire([(self.X_BUS_A, Y_TOP), (self.X_BUS_A, Y_LATCHES)], color=ca, width=4)
        self.create_text(*self.t(self.X_BUS_A, Y_TOP-20), text="Bus A", font=self.get_font(14, True))

        self.wire([(self.X_BUS_B, Y_TOP), (self.X_BUS_B, Y_LATCHES + 150)], color=cb, width=4) # Vai mais longe (até o MAR)
        self.create_text(*self.t(self.X_BUS_B, Y_TOP-20), text="Bus B", font=self.get_font(14, True))

        # Desenhar cada registrador
        for name, idx in self.stack_order:
            # Lógica
            is_dest = (sig and sig.enc and sig.c == idx)
            is_src_a = (sig and sig.a == idx)
            is_src_b = (sig and sig.b == idx)
            bg = self.C_ACTIVE if (is_dest or is_src_a or is_src_b) else "white"

            # Input C (Seta da Esquerda)
            c_in = cc if is_dest else self.C_OFF
            self.wire([(self.X_BUS_C, y_r), (self.X_REGS - W_REG/2, y_r)], color=c_in, width=2, arrow=tk.LAST if is_dest else None)
            if is_dest: self.dot(self.X_BUS_C, y_r, c_in)

            # Output A (Seta Superior)
            c_out_a = self.C_BUS_A if is_src_a else self.C_OFF
            self.wire([(self.X_REGS + W_REG/2, y_r - 10), (self.X_BUS_A, y_r - 10)], color=c_out_a, width=2, arrow=tk.LAST)
            if is_src_a: self.dot(self.X_BUS_A, y_r - 10, c_out_a)

            # Output B (Seta Inferior)
            c_out_b = self.C_BUS_B if is_src_b else self.C_OFF
            self.wire([(self.X_REGS + W_REG/2, y_r + 10), (self.X_BUS_B, y_r + 10)], color=c_out_b, width=2, arrow=tk.LAST)
            if is_src_b: self.dot(self.X_BUS_B, y_r + 10, c_out_b)

            # Caixa
            val_txt = None
            if name not in ["0", "+1", "-1", "AMASK", "SMASK"]:
                val_txt = f"{self.reg_values.get(name, 0):04X}"
            self.rect(self.X_REGS, y_r, W_REG, H_REG, fill=bg, text=name, val=val_txt)
            
            y_r += H_REG + GAP

        # 3. Latches (Abaixo dos Registradores)
        self.rect(self.X_BUS_A, Y_LATCHES + 20, 80, 40, fill=self.C_LATCH)
        self.create_text(*self.t(self.X_BUS_A, Y_LATCHES + 20), text="Latch A", font=self.get_font(10))

        self.rect(self.X_BUS_B, Y_LATCHES + 20, 80, 40, fill=self.C_LATCH)
        self.create_text(*self.t(self.X_BUS_B, Y_LATCHES + 20), text="Latch B", font=self.get_font(10))

        # 4. MAR e MBR (Componentes Inferiores)
        Y_MAR_CONN = Y_LATCHES + 100 # Conexão do MAR ocorre abaixo dos latches
        Y_COMPONENTS = Y_MAR_CONN + 40

        # -- MAR --
        is_mar = (sig and sig.mar)
        c_mar = self.C_BUS_B if is_mar else self.C_OFF
        
        self.rect(self.X_MAR_MBR, Y_COMPONENTS, 160, 50, fill=self.C_ACTIVE if is_mar else "white", 
                  text="MAR", val=f"{self.reg_values.get('MAR',0):04X}")
        
        # Conexão Bus B -> MAR (Linha Horizontal Longa)
        self.wire([(self.X_BUS_B, Y_MAR_CONN), (self.X_MAR_MBR + 80, Y_MAR_CONN), (self.X_MAR_MBR + 80, Y_COMPONENTS)], 
                  color=c_mar, arrow=tk.LAST)
        if is_mar: self.dot(self.X_BUS_B, Y_MAR_CONN, c_mar)

        # -- MBR --
        y_mbr = Y_COMPONENTS + 80
        is_mbr_load = (sig and sig.mbr)
        is_mbr_out = (sig and sig.amux)
        bg_mbr = self.C_ACTIVE if (is_mbr_load or is_mbr_out) else "white"

        self.rect(self.X_MAR_MBR, y_mbr, 160, 50, fill=bg_mbr, 
                  text="MBR", val=f"{self.reg_values.get('MBR',0):04X}")

        # 5. AMUX (Abaixo dos Latches)
        y_amux = Y_LATCHES + 120
        x_amux = self.X_BUS_A - 40
        self.trapezoid(x_amux, y_amux, 120, 60, 40, text="AMUX")

        # Entrada 0: Latch A
        c_latch_a = ca if (sig and not sig.amux) else self.C_OFF
        self.wire([(self.X_BUS_A, Y_LATCHES + 40), (self.X_BUS_A, y_amux), (x_amux + 20, y_amux)], 
                  color=c_latch_a, arrow=tk.LAST)
        self.create_text(*self.t(x_amux + 30, y_amux - 10), text="0", font=self.get_font(9))

        # Entrada 1: MBR (Saída do MBR para o AMUX)
        c_mbr_amux = self.C_BUS_A if is_mbr_out else self.C_OFF
        # Rota: MBR -> Direita (passa por cima do Bus C) -> Sobe -> Entrada AMUX
        self.wire([
            (self.X_MAR_MBR + 80, y_mbr),   # Sai do MBR
            (x_amux - 30, y_mbr),           # Vai até perto do AMUX
            (x_amux - 30, y_amux)           # Sobe para entrada 1
        ], color=c_mbr_amux, arrow=tk.LAST)
        self.create_text(*self.t(x_amux - 40, y_amux - 10), text="1", font=self.get_font(9))


        # 6. ULA
        y_ula = y_amux + 80
        x_ula = (self.X_BUS_B + x_amux) / 2
        
        flags = None
        if self.registers_ref:
            n = (self.registers_ref.AC >> 15) & 1
            z = 1 if self.registers_ref.AC == 0 else 0
            flags = f"N={n}\nZ={z}"
        
        self.ula_shape(x_ula, y_ula, fill="white", text="ULA", subtext=flags)
        
        # Entradas ULA
        c_ula_a = self.C_BUS_A if sig else self.C_OFF
        self.wire([(x_amux, y_amux + 40), (x_ula - 30, y_ula)], color=c_ula_a, arrow=tk.LAST)

        c_ula_b = self.C_BUS_B if sig else self.C_OFF
        self.wire([(self.X_BUS_B, Y_LATCHES + 40), (self.X_BUS_B, y_ula), (x_ula + 30, y_ula)], 
                  color=c_ula_b, arrow=tk.LAST)

        # 7. Shifter
        y_shift = y_ula + 120
        self.rect(x_ula, y_shift, 120, 40, text="Shifter")
        # ULA -> Shifter
        self.wire([(x_ula, y_ula + 100), (x_ula, y_shift - 20)], color=cc, arrow=tk.LAST)

        # 8. Loop Inferior (Shifter -> Bus C e MBR)
        y_loop = y_shift + 50
        
        # Sai do Shifter e desce
        self.wire([(x_ula, y_shift + 20), (x_ula, y_loop)], color=cc)
        
        # Linha Horizontal (Base do Loop)
        x_mbr_in = self.X_MAR_MBR + 80
        self.wire([(x_ula, y_loop), (x_mbr_in, y_loop)], color=cc)
        
        # O "T" Invertido para o Bus C
        self.wire([(self.X_BUS_C, y_loop), (self.X_BUS_C, Y_BOT_LOOP - 50)], color=cc)
        self.dot(self.X_BUS_C, y_loop, cc) # Ponto de conexão

        # Perna para o MBR (Entrada)
        c_mbr_in = cc if (sig and sig.enc and sig.c == 1) else self.C_OFF
        self.wire([(x_mbr_in, y_loop), (x_mbr_in, y_mbr + 25)], color=c_mbr_in, arrow=tk.LAST)