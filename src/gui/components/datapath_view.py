import tkinter as tk
from tkinter import font

class DatapathView(tk.Canvas):
    def __init__(self, master, registers, **kwargs):
        super().__init__(master, bg='white', highlightthickness=0, **kwargs)
        self.registers_ref = registers

        # --- MUNDO VIRTUAL ---
        self.VW = 1400  
        self.VH = 1600
        
        self.X_CENTER = 600  

        # === DIMENSÕES DOS REGISTRADORES ===
        self.REG_WIDTH = 250   
        self.REG_HEIGHT = 50   
        self.REG_GAP = 15      
        self.Y_START = 50      

        # === DIMENSÕES DOS LATCHES ===
        self.LATCH_W = 150     
        self.LATCH_H = 40
        
        # === DIMENSÕES MAR E MBR ===
        self.MAR_MBR_W = 220   
        self.MAR_MBR_H = 50
        self.X_MAR_MBR = 250   

        # --- Ordem Estrita da Imagem ---
        self.register_order = [
            ("PC", "PC"), ("AC", "AC"), ("SP", "SP"), ("IR", "IR"), ("TIR", "TIR"),
            ("0", 0), ("+1", 1), ("-1", -1), ("AMASK", "AMASK"), ("SMASK", "SMASK"),
            ("A", "A"), ("B", "B"), ("C", "C"), ("D", "D"), ("E", "E"), ("F", "F")
        ]

        self.signals = None
        self.reg_values = {}
        self.bind("<Configure>", self.on_resize)

    def update_state(self, signals, reg_values):
        self.signals = signals
        self.reg_values = reg_values
        self.draw()

    def on_resize(self, event):
        self.draw()

    def t(self, x, y):
        w_real = self.winfo_width()
        h_real = self.winfo_height()
        if w_real < 10 or h_real < 10: return 0, 0
        scale = min(w_real / self.VW, h_real / self.VH) * 0.90
        ox = (w_real - self.VW * scale) / 2
        oy = (h_real - self.VH * scale) / 2
        return ox + x * scale, oy + y * scale

    def font_get(self, size, bold=False):
        w_real = self.winfo_width()
        scale = w_real / self.VW if self.VW > 0 else 1
        final_size = max(7, int(size * scale)) 
        return font.Font(family="Arial", size=final_size, weight="bold" if bold else "normal")

    def draw_box(self, x, y, w, h, label, value=None, bg="#FFFFFF"):
        x0, y0 = self.t(x - w/2, y - h/2)
        x1, y1 = self.t(x + w/2, y + h/2)
        self.create_rectangle(x0, y0, x1, y1, fill=bg, outline="black", width=2)
        
        FONT_SIZE = 12 
        if value is not None:
            tx, ty = self.t(x - w/2 + 20, y)
            self.create_text(tx, ty, text=label, anchor="w", font=self.font_get(FONT_SIZE, True))
            vx, vy = self.t(x + w/2 - 20, y)
            display_text = f"{value:04X}" if isinstance(value, int) else str(value)
            self.create_text(vx, vy, text=display_text, anchor="e", font=self.font_get(FONT_SIZE))
        else:
            cx, cy = self.t(x, y)
            self.create_text(cx, cy, text=label, anchor="center", font=self.font_get(FONT_SIZE, True))

    def draw_alu_shape(self, x, y):
        w_top = 300
        w_bottom = 150
        h = 80
        
        p1 = self.t(x - w_top/2, y - h/2)    
        p2 = self.t(x + w_top/2, y - h/2)    
        p3 = self.t(x + w_bottom/2, y + h/2) 
        p4 = self.t(x - w_bottom/2, y + h/2) 
        
        self.create_polygon(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], p4[0], p4[1], 
                            fill="white", outline="black", width=2)
        
        cx, cy = self.t(x, y)
        self.create_text(cx, cy, text="ALU", font=self.font_get(14, True))
        
        nx, ny = self.t(x + w_top/2 + 30, y - 20)
        zx, zy = self.t(x + w_top/2 + 30, y + 20)
        self.create_text(nx, ny, text="N", font=self.font_get(12, True))
        self.create_text(zx, zy, text="Z", font=self.font_get(12, True))

    def draw(self):
        self.delete("all")
        if self.winfo_width() < 10: return

        # 1. Registradores Centrais
        current_y = self.Y_START
        for label, key in self.register_order:
            display_val = 0
            if isinstance(key, int): display_val = key & 0xFFFF 
            elif key == "AMASK": display_val = 0x0FFF
            elif key == "SMASK": display_val = 0x00FF
            else: display_val = self.reg_values.get(key, 0)
            self.draw_box(self.X_CENTER, current_y, self.REG_WIDTH, self.REG_HEIGHT, label, display_val)
            current_y += self.REG_HEIGHT + self.REG_GAP
        
        # 2. Latches
        y_pos_F_center = current_y - self.REG_HEIGHT - self.REG_GAP
        y_base_F = y_pos_F_center + (self.REG_HEIGHT / 2)

        VERTICAL_MARGIN = 50 
        latches_y = y_base_F + VERTICAL_MARGIN + (self.LATCH_H / 2)
        start_x_latches = self.X_CENTER + (self.REG_WIDTH / 2) + 80
        latch_a_x = start_x_latches + (self.LATCH_W / 2)
        latch_b_x = latch_a_x + self.LATCH_W + 20

        self.draw_box(latch_a_x, latches_y, self.LATCH_W, self.LATCH_H, "Latch A", value=None)
        self.draw_box(latch_b_x, latches_y, self.LATCH_W, self.LATCH_H, "Latch B", value=None)

        # 3. MAR e MBR (Esquerda)
        # Definindo a posição Y deles primeiro, pois o AMUX dependerá disso
        y_below_latches = latches_y + (self.LATCH_H / 2) + 80
        mar_y = y_below_latches + (self.MAR_MBR_H / 2)
        mbr_y = mar_y + self.MAR_MBR_H + 20
        
        val_mar = self.reg_values.get("MAR", 0)
        val_mbr = self.reg_values.get("MBR", 0)
        self.draw_box(self.X_MAR_MBR, mar_y, self.MAR_MBR_W, self.MAR_MBR_H, "MAR", val_mar)
        self.draw_box(self.X_MAR_MBR, mbr_y, self.MAR_MBR_W, self.MAR_MBR_H, "MBR", val_mbr)

        # === PASSO 5: AMUX, ALU e DESLOCADOR (Posicionamento Relativo ao MBR) ===

        # Cálcula a borda inferior do MBR
        y_base_MBR = mbr_y + (self.MAR_MBR_H / 2)

        # AMUX: Horizontalmente alinhado com Latch A, mas Verticalmente ABAIXO do MBR
        amux_x = latch_a_x
        # Gap de 60px abaixo do MBR
        amux_y = y_base_MBR + 60 
        
        self.draw_box(amux_x, amux_y, self.LATCH_W, 50, "AMUX", value=None)

        # ALU: Centralizada entre AMUX e Latch B (X), e abaixo do AMUX (Y)
        alu_center_x = (amux_x + latch_b_x) / 2
        # Gap de 100px entre AMUX e ALU
        alu_center_y = amux_y + 100 
        
        self.draw_alu_shape(alu_center_x, alu_center_y)

        # DESLOCADOR (Shifter): Abaixo da ALU com gap MAIOR para a seta
        # Gap aumentado para 120px
        shifter_y = alu_center_y + 120
        self.draw_box(alu_center_x, shifter_y, 250, 50, "Shifter", value=None)