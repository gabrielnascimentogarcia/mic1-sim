"""
Visualização do Caminho de Dados (Datapath) do MIC-1.
Layout: Fiel à Imagem de Referência (Grid Rígido e Organizado).
"""

import tkinter as tk
import ctypes

class DatapathView(tk.Canvas):
    def __init__(self, master, registers, **kwargs):
        super().__init__(master, bg='white', highlightthickness=0, **kwargs)
        self.registers_ref = registers
        
        # Tenta melhorar a nitidez no Windows
        try: ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except: pass

        # --- MUNDO VIRTUAL (1000 x 1800) ---
        self.W = 1000.0
        self.H = 1800.0
        
        self.reg_names = [
            ("MAR", 0), ("MBR", 1), ("PC", 2), ("SP", 3), 
            ("AC", 4), ("IR", 5), ("TIR", 6), 
            ("0", 7), ("+1", 8), ("-1", 9), ("AMASK", 10), ("SMASK", 11)
        ]
        
        # --- CORES ---
        self.C_BG = "white"
        self.C_INK = "black"
        self.C_BUS_IDLE = "#444444"
        self.C_LATCH = "#DDDDDD"
        
        # Cores Vibrantes para Sinais Ativos
        self.C_ACT_A = "#2980b9"   # Azul
        self.C_ACT_B = "#27ae60"   # Verde
        self.C_ACT_C = "#c0392b"   # Vermelho
        self.C_ACT_ALU = "#f1c40f" # Amarelo

        self.current_signals = None
        self.current_reg_values = {}
        
        self.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        self.draw(event.width, event.height)

    def update_state(self, signals, registers_state):
        self.current_signals = signals
        self.current_reg_values = registers_state
        self.draw(self.winfo_width(), self.winfo_height())

    def draw(self, w, h):
        self.delete("all")
        if w < 50 or h < 50: return

        # --- 1. MATRIZ DE ESCALA (Fit Window) ---
        MARGIN = 20
        scale = min((w - 2*MARGIN)/self.W, (h - 2*MARGIN)/self.H)
        off_x = MARGIN + (w - 2*MARGIN - (self.W * scale)) / 2
        off_y = MARGIN + (h - 2*MARGIN - (self.H * scale)) / 2

        def t(x, y): return (x * scale) + off_x, (y * scale) + off_y
        
        def rect(x, y, w, h, fill="white", outline="black", width=2):
            self.create_rectangle(t(x, y), t(x+w, y+h), fill=fill, outline=outline, width=width*scale)

        def line(coords, fill="black", width=2, arrow=None):
            pts = [t(x, y) for x, y in coords]
            flat = [v for p in pts for v in p]
            self.create_line(flat, fill=fill, width=width*scale, arrow=arrow, capstyle=tk.ROUND, joinstyle=tk.MITER)

        def text(x, y, txt, size=24, bold=False, anchor="center", color="black"):
            sz = int(size * scale)
            font = ("Arial", -max(10, sz), "bold" if bold else "normal")
            self.create_text(t(x, y), text=txt, font=font, anchor=anchor, fill=color)

        # --- 2. GRID DE LAYOUT ---
        X_BUS_C = 100
        X_REGS  = 400  # Centro dos registradores
        X_BUS_B = 700
        X_BUS_A = 800
        X_MBR_LINE = 920 # Linha extra na extrema direita
        
        Y_START = 80
        REG_H = 60
        REG_W = 260
        GAP = 20
        
        sig = self.current_signals

        # --- 3. BARRAMENTOS PRINCIPAIS ---
        total_regs_h = len(self.reg_names) * (REG_H + GAP)
        Y_END_REGS = Y_START + total_regs_h
        
        # Cores dinâmicas
        c_c = self.C_ACT_C if (sig and sig.enc) else self.C_BUS_IDLE
        c_a = self.C_ACT_A if (sig and not sig.amux) else self.C_BUS_IDLE
        c_b = self.C_ACT_B if sig else self.C_BUS_IDLE
        
        W_BUS = 8
        
        # Desenha Troncos Verticais
        line([(X_BUS_C, Y_START), (X_BUS_C, Y_END_REGS + 550)], fill=c_c, width=W_BUS) # C
        line([(X_BUS_B, Y_START), (X_BUS_B, Y_END_REGS + 50)], fill=c_b, width=W_BUS)  # B
        line([(X_BUS_A, Y_START), (X_BUS_A, Y_END_REGS + 50)], fill=c_a, width=W_BUS)  # A

        text(X_BUS_C, Y_START-30, "Bus C", 20, True, color="#555")
        text(X_BUS_B, Y_START-30, "Bus B", 20, True, color="#555")
        text(X_BUS_A, Y_START-30, "Bus A", 20, True, color="#555")

        # --- 4. REGISTRADORES ---
        curr_y = Y_START
        mbr_y = 0
        
        for name, idx in self.reg_names:
            # Estado Visual
            bg = "white"
            wc, wa, wb = "black", "black", "black"
            
            if sig:
                if sig.enc and sig.c == idx: 
                    bg = "#FADBD8"; wc = self.C_ACT_C
                
                # Se AMUX=0, destaca saída para Bus A
                src_a = sig.a
                if src_a == idx and not sig.amux: 
                    bg = "#D6EAF8" if bg == "white" else bg
                    wa = self.C_ACT_A
                
                # Saída para Bus B
                if sig.b == idx: 
                    bg = "#D5F5E3" if bg == "white" else bg
                    wb = self.C_ACT_B

            # Geometria
            xl, xr = X_REGS - REG_W/2, X_REGS + REG_W/2
            ym = curr_y + REG_H/2
            
            # Fios (Wires)
            # C -> Reg
            line([(X_BUS_C, ym), (xl, ym)], fill=wc, width=3, arrow=tk.LAST)
            
            # Reg -> B (Passa por cima de nada)
            line([(xr, ym+10), (X_BUS_B, ym+10)], fill=wb, width=3)
            self.create_oval(t(X_BUS_B-4, ym+6), t(X_BUS_B+4, ym+14), fill=wb, outline="")
            
            # Reg -> A (Passa por cima de B)
            line([(xr, ym-10), (X_BUS_A, ym-10)], fill=wa, width=3)
            self.create_oval(t(X_BUS_A-4, ym-14), t(X_BUS_A+4, ym-6), fill=wa, outline="")

            # Caixa
            rect(xl, curr_y, REG_W, REG_H, fill=bg)
            text(xl+15, ym, name, 22, True, "w")
            val = self.current_reg_values.get(name, 0)
            text(xr-15, ym, f"{val:04X}", 22, False, "e")
            
            if name == "MBR": mbr_y = ym
            
            curr_y += (REG_H + GAP)

        # --- 5. LATCHES E AMUX ---
        Y_LATCH = Y_END_REGS + 60
        LATCH_W, LATCH_H = 80, 50
        
        # Latch B (Fim Bus B)
        rect(X_BUS_B - LATCH_W/2, Y_LATCH, LATCH_W, LATCH_H, fill=self.C_LATCH)
        text(X_BUS_B, Y_LATCH + LATCH_H/2, "LB", 18, True)
        
        # Latch A (Fim Bus A)
        rect(X_BUS_A - LATCH_W/2, Y_LATCH, LATCH_W, LATCH_H, fill=self.C_LATCH)
        text(X_BUS_A, Y_LATCH + LATCH_H/2, "LA", 18, True)

        # AMUX
        Y_AMUX = Y_LATCH + 80
        X_AMUX = X_BUS_A - 30 
        AMUX_W = 100
        
        # Desenho AMUX (Trapézio)
        pts = [
            (X_AMUX-AMUX_W/2, Y_AMUX), (X_AMUX+AMUX_W/2, Y_AMUX),
            (X_AMUX+30, Y_AMUX+50), (X_AMUX-30, Y_AMUX+50)
        ]
        tk_pts = [v for p in pts for v in t(*p)]
        self.create_polygon(tk_pts, fill="white", outline="black", width=2*scale)
        text(X_AMUX, Y_AMUX+25, "AMUX", 16, True)

        # --- 6. CONEXÕES ESPECIAIS (MBR e AMUX) ---
        
        # Fio 1: Latch A -> AMUX (Entrada 0)
        c_la = self.C_ACT_A if (sig and not sig.amux) else "black"
        line([(X_BUS_A, Y_LATCH+LATCH_H), (X_BUS_A, Y_AMUX-10), (X_AMUX-20, Y_AMUX-10), (X_AMUX-20, Y_AMUX)], fill=c_la, width=3, arrow=tk.LAST)
        text(X_AMUX-25, Y_AMUX-20, "0", 12)

        # Fio 2: MBR -> AMUX (Entrada 1 - Fio Longo)
        if mbr_y > 0:
            c_mbr = self.C_ACT_A if (sig and sig.amux) else "#AAA"
            w_mbr = 4 if (sig and sig.amux) else 2
            
            # Rota: MBR -> Extrema Direita -> Desce tudo -> Entra no AMUX pela direita
            line([
                (X_REGS + REG_W/2, mbr_y), 
                (X_MBR_LINE, mbr_y), 
                (X_MBR_LINE, Y_AMUX-10), 
                (X_AMUX+20, Y_AMUX-10),
                (X_AMUX+20, Y_AMUX)
            ], fill=c_mbr, width=w_mbr, arrow=tk.LAST)
            text(X_AMUX+25, Y_AMUX-20, "1", 12)

        # --- 7. ULA ---
        Y_ALU = Y_AMUX + 90
        ALU_H = 100
        # Centro da ULA é entre Latch B e AMUX
        X_ALU = (X_BUS_B + X_AMUX) / 2
        
        # Conexões para ULA
        # Esq: Do AMUX
        c_alu_a = self.C_ACT_A if sig else "black"
        line([(X_AMUX, Y_AMUX+50), (X_ALU-30, Y_ALU)], fill=c_alu_a, width=3, arrow=tk.LAST)
        
        # Dir: Do Latch B
        c_alu_b = self.C_ACT_B if sig else "black"
        line([(X_BUS_B, Y_LATCH+LATCH_H), (X_BUS_B, Y_ALU)], fill=c_alu_b, width=3, arrow=tk.LAST)
        
        # Forma ULA
        p_alu = [
            (X_ALU-60, Y_ALU), (X_ALU+60, Y_ALU),
            (X_ALU+20, Y_ALU+ALU_H), (X_ALU-20, Y_ALU+ALU_H)
        ]
        tk_alu = [v for p in p_alu for v in t(*p)]
        f_alu = self.C_ACT_ALU if sig else "white"
        self.create_polygon(tk_alu, fill=f_alu, outline="black", width=2*scale)
        text(X_ALU, Y_ALU+40, "ULA", 28, True)
        
        if self.registers_ref:
            n = (self.registers_ref.AC >> 15) & 1
            z = 1 if self.registers_ref.AC == 0 else 0
            text(X_ALU, Y_ALU+75, f"N:{n} Z:{z}", 14, True)

        # --- 8. SHIFTER ---
        Y_SH = Y_ALU + ALU_H + 30
        rect(X_ALU-50, Y_SH, 100, 50, fill="white")
        text(X_ALU, Y_SH+25, "Shifter", 18)
        
        # ULA -> Shifter
        line([(X_ALU, Y_ALU+ALU_H), (X_ALU, Y_SH)], width=3, arrow=tk.LAST)
        
        # --- 9. FEEDBACK ---
        Y_LOOP = Y_SH + 80
        c_fb = self.C_ACT_C if (sig and sig.enc) else "black"
        
        line([
            (X_ALU, Y_SH+50), (X_ALU, Y_LOOP),
            (X_BUS_C, Y_LOOP), (X_BUS_C, Y_END_REGS + 550)
        ], fill=c_fb, width=4, arrow=tk.LAST)