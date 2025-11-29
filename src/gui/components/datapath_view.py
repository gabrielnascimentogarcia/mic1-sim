import tkinter as tk
from tkinter import font

class DatapathView(tk.Canvas):
    def __init__(self, master, registers, **kwargs):
        super().__init__(master, bg='white', highlightthickness=0, **kwargs)
        self.registers_ref = registers

        # Mundo Virtual - AUMENTADO para evitar sobreposições
        self.VW = 1800
        self.VH = 1800

        # === POSIÇÕES HORIZONTAIS CORRIGIDAS ===
        self.X_TEXT_LEFT = 100           # Textos descritivos esquerda
        self.X_MAR_MBR = 280             # MAR/MBR
        self.X_BUS_ENTRY = 450           # Barramento de entrada (vertical)
        self.X_REG_LEFT = 520            # Borda esquerda registradores
        self.X_REG_CENTER = 680          # Centro registradores
        self.X_REG_RIGHT = 840           # Borda direita registradores
        self.X_BUS_A = 920               # Barramento A (linha vertical)
        self.X_BUS_B = 1050              # Barramento B (linha vertical)
        self.X_LATCH_A = 920             # Latch A (alinhado com Bus A)
        self.X_LATCH_B = 1050            # Latch B (alinhado com Bus B)
        self.X_AMUX = 985                # AMUX (entre os latches)
        self.X_ALU = 985                 # ALU
        self.X_SHIFTER = 985             # Shifter
        
        # Cores
        self.C_ACTIVE = "#FFFF99"
        self.C_COMPONENT = "#FFFFFF"

        self.signals = None
        self.reg_values = {}

        # Registradores
        self.stack_order = [
            ("PC", 2), ("AC", 4), ("SP", 3), ("IR", 5), ("TIR", 6),
            ("0", 7), ("+1", 8), ("-1", 9), 
            ("AMASK", 10), ("SMASK", 11),
            ("A", 12), ("B", 13), ("C", 14), 
            ("D", 15), ("E", 16), ("F", 17)
        ]

        self.bind("<Configure>", self.on_resize)

    def update_state(self, signals, reg_values):
        self.signals = signals
        self.reg_values = reg_values
        self.draw()

    def on_resize(self, event):
        self.draw()

    def t(self, x, y):
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 100 or h < 100:
            return 0, 0
        scale = min(w / self.VW, h / self.VH) * 0.95
        ox = (w - self.VW * scale) / 2
        oy = (h - self.VH * scale) / 2
        return ox + x * scale, oy + y * scale

    def font_get(self, size, bold=False):
        w, h = self.winfo_width(), self.winfo_height()
        s = min(w / self.VW, h / self.VH)
        fs = max(7, int(size * s * 2))
        return font.Font(family="Arial", size=fs, weight="bold" if bold else "normal")

    def box(self, x, y, w, h, fill="#FFF", txt="", val=""):
        x0, y0 = self.t(x - w/2, y - h/2)
        x1, y1 = self.t(x + w/2, y + h/2)
        self.create_rectangle(x0, y0, x1, y1, fill=fill, outline="#000", width=2)
        
        if txt:
            tx, ty = self.t(x - w/2 + 10, y)
            self.create_text(tx, ty, text=txt, anchor="w", font=self.font_get(9, True))
        
        if val:
            vx, vy = self.t(x + w/2 - 10, y)
            self.create_text(vx, vy, text=val, anchor="e", font=self.font_get(8))

    def line(self, pts, w=2):
        coords = []
        for px, py in pts:
            coords.extend(self.t(px, py))
        if len(coords) >= 4:
            self.create_line(coords, fill="#000", width=w)

    def arrow(self, x0, y0, x1, y1, w=2):
        px0, py0 = self.t(x0, y0)
        px1, py1 = self.t(x1, y1)
        self.create_line(px0, py0, px1, py1, fill="#000", width=w, 
                        arrow=tk.LAST, arrowshape=(8, 10, 3))

    def txt(self, x, y, text, size=8, bold=False):
        tx, ty = self.t(x, y)
        self.create_text(tx, ty, text=text, font=self.font_get(size, bold))

    def mux(self, x, y, w, h, label=""):
        w_top = w * 0.65
        pts = [
            self.t(x - w_top/2, y),
            self.t(x + w_top/2, y),
            self.t(x + w/2, y + h),
            self.t(x - w/2, y + h)
        ]
        flat = [c for p in pts for c in p]
        self.create_polygon(flat, fill="#FFF", outline="#000", width=2)
        if label:
            self.txt(x, y + h/2, label, 9, True)

    def alu_shape(self, x, y):
        w, h = 80, 110
        pts = [
            self.t(x - w, y),
            self.t(x - w*0.35, y + h*0.28),
            self.t(x + w*0.35, y + h*0.28),
            self.t(x + w, y),
            self.t(x + w*0.32, y + h),
            self.t(x - w*0.32, y + h)
        ]
        flat = [c for p in pts for c in p]
        self.create_polygon(flat, fill="#FFF", outline="#000", width=2)
        self.txt(x, y + h/2, "ALU", 11, True)

    def draw(self):
        self.delete("all")
        if self.winfo_width() < 100:
            return

        sig = self.signals

        # === POSIÇÕES VERTICAIS ===
        Y_TOP = 80
        Y_REG_START = 140
        REG_H = 40
        REG_GAP = 4
        REG_W = 300

        # Posições dos registradores
        reg_y = {}
        y = Y_REG_START
        for name, idx in self.stack_order:
            reg_y[idx] = y
            y += REG_H + REG_GAP

        Y_REG_END = y - REG_GAP
        Y_MAR = Y_REG_START + 100
        Y_MBR = Y_MAR + 100
        Y_LATCHES = Y_REG_END + 80
        Y_AMUX = Y_LATCHES + 120
        Y_ALU = Y_AMUX + 150
        Y_SHIFTER = Y_ALU + 150
        Y_BOTTOM = Y_SHIFTER + 100

        # === BARRAMENTO VERTICAL PRINCIPAL (ENTRADA) ===
        self.line([(self.X_BUS_ENTRY, Y_TOP), (self.X_BUS_ENTRY, Y_BOTTOM)], w=4)

        # === TEXTOS DESCRITIVOS ===
        self.txt(self.X_TEXT_LEFT, Y_MAR - 20, "Para o barramento", 7)
        self.txt(self.X_TEXT_LEFT, Y_MAR - 5, "de endereços", 7)
        
        self.txt(self.X_TEXT_LEFT, Y_MBR - 20, "Para o barramento", 7)
        self.txt(self.X_TEXT_LEFT, Y_MBR - 5, "de dados", 7)

        # === MAR ===
        is_mar = (sig and sig.mar)
        self.box(self.X_MAR_MBR, Y_MAR, 100, 50, 
                fill=self.C_ACTIVE if is_mar else self.C_COMPONENT,
                txt="MAR", val=f"{self.reg_values.get('MAR', 0):03X}")
        
        # Label M4
        self.txt(self.X_TEXT_LEFT, Y_MAR, "M4", 7)
        self.arrow(self.X_MAR_MBR - 55, Y_MAR, self.X_MAR_MBR - 50, Y_MAR, w=1)

        # === MBR ===
        is_mbr_write = (sig and sig.mbr)
        is_mbr_read = (sig and sig.amux == 1)
        self.box(self.X_MAR_MBR, Y_MBR, 100, 50,
                fill=self.C_ACTIVE if (is_mbr_write or is_mbr_read) else self.C_COMPONENT,
                txt="MBR", val=f"{self.reg_values.get('MBR', 0):04X}")
        
        # Labels M0 e M1
        self.txt(self.X_TEXT_LEFT, Y_MBR - 10, "M0", 7)
        self.arrow(self.X_BUS_ENTRY, Y_MBR - 10, self.X_MAR_MBR - 50, Y_MBR - 10, w=1)
        
        self.txt(self.X_TEXT_LEFT, Y_MBR + 10, "M1", 7)
        self.arrow(self.X_MAR_MBR + 50, Y_MBR + 10, self.X_MAR_MBR + 100, Y_MBR + 10, w=1)

        # === REGISTRADORES ===
        for name, idx in self.stack_order:
            y_reg = reg_y[idx]
            
            is_write = (sig and sig.enc and sig.c == idx)
            is_read_a = (sig and sig.a == idx)
            is_read_b = (sig and sig.b == idx)
            
            fill = self.C_ACTIVE if (is_write or is_read_a or is_read_b) else self.C_COMPONENT
            
            val = ""
            if name not in ["0", "+1", "-1", "AMASK", "SMASK", "A", "B", "C", "D", "E", "F"]:
                val = f"{self.reg_values.get(name, 0):04X}"
            
            self.box(self.X_REG_CENTER, y_reg, REG_W, REG_H, fill=fill, txt=name, val=val)
            
            # Entrada (esquerda)
            if is_write:
                self.arrow(self.X_BUS_ENTRY, y_reg, self.X_REG_LEFT, y_reg, w=2)
            else:
                self.line([(self.X_BUS_ENTRY, y_reg), (self.X_REG_LEFT, y_reg)], w=1)
            
            # Saídas duplas paralelas (direita)
            y_top = y_reg - 10
            y_bot = y_reg + 10
            
            # Para Bus A (superior)
            if is_read_a:
                self.arrow(self.X_REG_RIGHT, y_top, self.X_BUS_A, y_top, w=1)
            else:
                self.line([(self.X_REG_RIGHT, y_top), (self.X_BUS_A, y_top)], w=1)
            
            # Para Bus B (inferior)
            if is_read_b:
                self.arrow(self.X_REG_RIGHT, y_bot, self.X_BUS_B, y_bot, w=1)
            else:
                self.line([(self.X_REG_RIGHT, y_bot), (self.X_BUS_B, y_bot)], w=1)

        # === BARRAMENTOS VERTICAIS A e B ===
        self.line([(self.X_BUS_A, Y_REG_START - 30), (self.X_BUS_A, Y_LATCHES - 20)], w=3)
        self.line([(self.X_BUS_B, Y_REG_START - 30), (self.X_BUS_B, Y_LATCHES - 20)], w=3)

        # === LABELS L0 e L1 ===
        y_labels = Y_LATCHES - 40
        self.txt(self.X_BUS_A + 50, y_labels, "L0", 7)
        self.arrow(self.X_BUS_A, y_labels, self.X_BUS_A + 35, y_labels, w=1)
        
        self.txt(self.X_BUS_B + 50, y_labels, "L1", 7)
        self.arrow(self.X_BUS_B, y_labels, self.X_BUS_B + 35, y_labels, w=1)

        # === LATCHES ===
        self.box(self.X_LATCH_A, Y_LATCHES, 90, 45, fill="#E8E8E8", txt="Latch A")
        self.box(self.X_LATCH_B, Y_LATCHES, 90, 45, fill="#E8E8E8", txt="Latch B")

        # === AMUX ===
        self.mux(self.X_AMUX, Y_AMUX, 90, 70, "AMUX")
        
        # Entrada A0 (Latch A)
        self.txt(self.X_AMUX - 60, Y_AMUX + 20, "A0", 7)
        self.line([
            (self.X_LATCH_A, Y_LATCHES + 23),
            (self.X_LATCH_A, Y_AMUX + 20),
            (self.X_AMUX - 38, Y_AMUX + 20)
        ], w=2)
        
        # Entrada do MBR
        y_mbr_route = Y_AMUX + 50
        self.line([
            (self.X_MAR_MBR + 50, Y_MBR + 10),
            (self.X_AMUX - 120, Y_MBR + 10),
            (self.X_AMUX - 120, y_mbr_route),
            (self.X_AMUX - 38, y_mbr_route)
        ], w=2)

        # === ALU ===
        self.alu_shape(self.X_ALU, Y_ALU)
        
        # Flags
        if self.registers_ref:
            n = (self.registers_ref.AC >> 15) & 1
            z = 1 if self.registers_ref.AC == 0 else 0
            self.txt(self.X_ALU + 100, Y_ALU + 35, f"N", 8)
            self.txt(self.X_ALU + 100, Y_ALU + 50, f"Z", 8)
        
        # Entrada F0 (AMUX)
        self.txt(self.X_ALU - 100, Y_ALU + 30, "F0", 7)
        self.line([
            (self.X_AMUX, Y_AMUX + 70),
            (self.X_AMUX, Y_ALU + 20),
            (self.X_ALU - 65, Y_ALU + 30)
        ], w=2)
        
        # Entrada F1 (Latch B)
        self.txt(self.X_ALU + 100, Y_ALU + 15, "F1", 7)
        self.line([
            (self.X_LATCH_B, Y_LATCHES + 23),
            (self.X_LATCH_B, Y_ALU + 30),
            (self.X_ALU + 65, Y_ALU + 30)
        ], w=2)

        # === SHIFTER ===
        self.box(self.X_SHIFTER, Y_SHIFTER, 110, 50, txt="Deslocador")
        
        # S0 e S1
        self.txt(self.X_SHIFTER - 75, Y_SHIFTER, "S0", 7)
        self.txt(self.X_SHIFTER + 75, Y_SHIFTER, "S1", 7)
        
        self.arrow(self.X_ALU, Y_ALU + 110, self.X_ALU, Y_SHIFTER - 25, w=3)

        # === RETORNO ===
        self.line([
            (self.X_SHIFTER, Y_SHIFTER + 25),
            (self.X_SHIFTER, Y_BOTTOM),
            (self.X_BUS_ENTRY, Y_BOTTOM),
            (self.X_BUS_ENTRY, Y_TOP)
        ], w=4)
        
        self.txt(self.X_SHIFTER - 100, Y_BOTTOM + 20, "Saída de dados", 7)