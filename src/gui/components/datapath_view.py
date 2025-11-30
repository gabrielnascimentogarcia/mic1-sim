import tkinter as tk
from tkinter import font

class DatapathView(tk.Canvas):
    def __init__(self, master, registers, **kwargs):
        super().__init__(master, bg='white', highlightthickness=0, **kwargs)
        self.registers_ref = registers

        # --- MUNDO VIRTUAL (Sistema de Coordenadas Fixo) ---
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

        # --- Ordem Estrita da Imagem (Cima para Baixo) ---
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
        """Transforma coordenadas virtuais em coordenadas de tela (com escala)."""
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
        
        # --- SETAS N e Z ---
        # Seta N
        snx, sny = self.t(x + 130, y - 20)
        enx, eny = self.t(x + 170, y - 20)
        self.create_line(snx, sny, enx, eny, width=2, fill="black", arrow=tk.LAST, arrowshape=(8, 10, 3))

        # Seta Z
        szx, szy = self.t(x + 95, y + 20)
        ezx, ezy = self.t(x + 170, y + 20)
        self.create_line(szx, szy, ezx, ezy, width=2, fill="black", arrow=tk.LAST, arrowshape=(8, 10, 3))
        
        nx, ny = self.t(x + w_top/2 + 30, y - 20)
        zx, zy = self.t(x + w_top/2 + 30, y + 20)
        self.create_text(nx, ny, text="N", font=self.font_get(12, True))
        self.create_text(zx, zy, text="Z", font=self.font_get(12, True))

    def draw(self):
        self.delete("all")
        if self.winfo_width() < 10: return

        # === 1. CÁLCULO DE GEOMETRIA GERAL ===
        
        # Posição X dos Latches
        start_x_latches = self.X_CENTER + (self.REG_WIDTH / 2) + 80
        bus_a_x = start_x_latches + (self.LATCH_W / 2)       
        bus_b_x = bus_a_x + self.LATCH_W + 20                
        
        # Posição X do Barramento C
        bus_c_x = 420

        # Posição Y final (Latches)
        num_regs = len(self.register_order)
        last_reg_y = self.Y_START + (num_regs - 1) * (self.REG_HEIGHT + self.REG_GAP)
        
        VERTICAL_MARGIN = 50 
        latches_y = last_reg_y + (self.REG_HEIGHT / 2) + VERTICAL_MARGIN + (self.LATCH_H / 2)

        # Altura dos Barramentos Verticais A e B
        bus_top_y = self.Y_START - 60 
        bus_bottom_y = latches_y - (self.LATCH_H / 2)

        # === 2. DESENHAR BARRAMENTOS VERTICAIS (BUS A e BUS B) ===
        # Bus A
        xa_screen, ya_top = self.t(bus_a_x, bus_top_y)
        _, ya_bot = self.t(bus_a_x, bus_bottom_y)
        self.create_line(xa_screen, ya_top, xa_screen, ya_bot, width=3, fill="black", arrow=tk.LAST, arrowshape=(8, 10, 3))

        # Bus B
        xb_screen, yb_top = self.t(bus_b_x, bus_top_y)
        _, yb_bot = self.t(bus_b_x, bus_bottom_y)
        self.create_line(xb_screen, yb_top, xb_screen, yb_bot, width=3, fill="black", arrow=tk.LAST, arrowshape=(8, 10, 3))


        # === 3. DESENHAR REGISTRADORES E CONEXÕES HORIZONTAIS ===
        current_y = self.Y_START
        reg_right_x = self.X_CENTER + (self.REG_WIDTH / 2)
        reg_left_x = self.X_CENTER - (self.REG_WIDTH / 2)

        for label, key in self.register_order:
            display_val = 0
            if isinstance(key, int): display_val = key & 0xFFFF 
            elif key == "AMASK": display_val = 0x0FFF
            elif key == "SMASK": display_val = 0x00FF
            else: display_val = self.reg_values.get(key, 0)
            
            self.draw_box(self.X_CENTER, current_y, self.REG_WIDTH, self.REG_HEIGHT, label, display_val)

            # --- SAÍDAS -> Bus A e Bus B ---
            y_out_a = current_y - 12
            x_start_scr, y_start_a_scr = self.t(reg_right_x, y_out_a)
            x_end_a_scr, _ = self.t(bus_a_x, y_out_a)
            self.create_line(x_start_scr, y_start_a_scr, x_end_a_scr, y_start_a_scr, 
                             width=2, fill="black", arrow=tk.LAST, arrowshape=(8, 10, 3))

            y_out_b = current_y + 12
            x_start_scr, y_start_b_scr = self.t(reg_right_x, y_out_b)
            x_end_b_scr, _ = self.t(bus_b_x, y_out_b) 
            self.create_line(x_start_scr, y_start_b_scr, x_end_b_scr, y_start_b_scr, 
                             width=2, fill="black", arrow=tk.LAST, arrowshape=(8, 10, 3))
            
            # --- ENTRADA <- Bus C ---
            x_bus_c_scr, y_reg_scr = self.t(bus_c_x, current_y)
            x_reg_in_scr, _ = self.t(reg_left_x, current_y)
            self.create_line(x_bus_c_scr, y_reg_scr, x_reg_in_scr, y_reg_scr, 
                             width=2, fill="black", arrow=tk.LAST, arrowshape=(8, 10, 3))

            current_y += self.REG_HEIGHT + self.REG_GAP


        # === 4. DESENHAR LATCHES ===
        self.draw_box(bus_a_x, latches_y, self.LATCH_W, self.LATCH_H, "Latch A", value=None)
        self.draw_box(bus_b_x, latches_y, self.LATCH_W, self.LATCH_H, "Latch B", value=None)


        # === 5. MAR e MBR (Esquerda) ===
        y_below_latches = latches_y + (self.LATCH_H / 2) + 80
        mar_y = y_below_latches + (self.MAR_MBR_H / 2)
        mbr_y = mar_y + self.MAR_MBR_H + 20
        
        val_mar = self.reg_values.get("MAR", 0)
        val_mbr = self.reg_values.get("MBR", 0)
        self.draw_box(self.X_MAR_MBR, mar_y, self.MAR_MBR_W, self.MAR_MBR_H, "MAR", val_mar)
        self.draw_box(self.X_MAR_MBR, mbr_y, self.MAR_MBR_W, self.MAR_MBR_H, "MBR", val_mbr)

        # --- NOVO: CONEXÃO LATCH B -> MAR (Ramificação) ---
        # Sai da linha vertical do Latch B (na altura do MAR) e vai para a direita do MAR
        mar_right_x = self.X_MAR_MBR + (self.MAR_MBR_W / 2)
        
        x_bus_b_scr, y_mar_scr = self.t(bus_b_x, mar_y)
        x_mar_in_scr, _ = self.t(mar_right_x, mar_y)
        
        # Desenha a linha da direita para a esquerda (Bus B -> MAR)
        self.create_line(x_bus_b_scr, y_mar_scr, x_mar_in_scr, y_mar_scr, 
                         width=2, fill="black", arrow=tk.LAST, arrowshape=(8, 10, 3))
        # --------------------------------------------------


        # === 6. AMUX, ALU e DESLOCADOR ===
        y_base_MBR = mbr_y + (self.MAR_MBR_H / 2)
        
        # AMUX alinhado com Bus A
        amux_x = bus_a_x
        amux_y = y_base_MBR + 60 
        
        # Conexão Latch A -> AMUX
        latch_a_bottom_y = latches_y + (self.LATCH_H / 2)
        amux_top_y = amux_y - 25 
        xa_start, ya_start = self.t(bus_a_x, latch_a_bottom_y)
        xa_end, ya_end = self.t(amux_x, amux_top_y)
        self.create_line(xa_start, ya_start, xa_end, ya_end, width=2, fill="black", arrow=tk.LAST, arrowshape=(8, 10, 3))

        # Conexão MBR -> AMUX (L deitado)
        mbr_right_x = self.X_MAR_MBR + (self.MAR_MBR_W / 2)
        amux_in_x = amux_x - 40 
        
        x_mbr_out_scr, y_mbr_out_scr = self.t(mbr_right_x, mbr_y)
        x_turn_scr, _ = self.t(amux_in_x, mbr_y)
        
        self.create_line(x_mbr_out_scr, y_mbr_out_scr, x_turn_scr, y_mbr_out_scr, width=2, fill="black")
        
        _, y_amux_top_scr = self.t(amux_in_x, amux_top_y)
        self.create_line(x_turn_scr, y_mbr_out_scr, x_turn_scr, y_amux_top_scr, 
                         width=2, fill="black", arrow=tk.LAST, arrowshape=(8, 10, 3))

        self.draw_box(amux_x, amux_y, self.LATCH_W, 50, "AMUX", value=None)

        # ALU 
        alu_center_x = (bus_a_x + bus_b_x) / 2
        alu_center_y = amux_y + 100 
        
        # Conexão AMUX -> ALU
        amux_bottom_y = amux_y + 25
        alu_top_y = alu_center_y - 40
        x_start_amux, y_start_amux = self.t(amux_x, amux_bottom_y)
        x_end_alu, y_end_alu = self.t(amux_x, alu_top_y) 
        self.create_line(x_start_amux, y_start_amux, x_end_alu, y_end_alu, width=2, fill="black", arrow=tk.LAST, arrowshape=(8, 10, 3))

        # Conexão Latch B -> ALU
        latch_b_bottom_y = latches_y + (self.LATCH_H / 2)
        xb_start, yb_start = self.t(bus_b_x, latch_b_bottom_y)
        xb_end, yb_end = self.t(bus_b_x, alu_top_y) 
        self.create_line(xb_start, yb_start, xb_end, yb_end, width=2, fill="black", arrow=tk.LAST, arrowshape=(8, 10, 3))

        self.draw_alu_shape(alu_center_x, alu_center_y)

        # Shifter
        shifter_y = alu_center_y + 120
        
        # Conexão ALU -> SHIFTER
        alu_bottom_y = alu_center_y + 40
        shifter_top_y = shifter_y - 25
        x_alu_shifter_start, y_alu_shifter_start = self.t(alu_center_x, alu_bottom_y)
        x_alu_shifter_end, y_alu_shifter_end = self.t(alu_center_x, shifter_top_y)
        self.create_line(x_alu_shifter_start, y_alu_shifter_start, x_alu_shifter_end, y_alu_shifter_end, 
                         width=2, fill="black", arrow=tk.LAST, arrowshape=(8, 10, 3))

        self.draw_box(alu_center_x, shifter_y, 250, 50, "Shifter", value=None)

        # === 7. CONEXÃO DE RETORNO (SHIFTER -> MBR e BUS C) ===
        shifter_bottom_y = shifter_y + 25
        mbr_bottom_y = mbr_y + 25 

        # 1. Desce um pouco (margem inferior)
        margin_y = shifter_bottom_y + 40
        x_shifter_scr, y_shifter_bot_scr = self.t(alu_center_x, shifter_bottom_y)
        _, y_margin_scr = self.t(alu_center_x, margin_y)
        
        self.create_line(x_shifter_scr, y_shifter_bot_scr, x_shifter_scr, y_margin_scr, width=2, fill="black")

        # 2. Linha Horizontal (Feedback)
        x_mbr_scr, _ = self.t(self.X_MAR_MBR, margin_y)
        self.create_line(x_shifter_scr, y_margin_scr, x_mbr_scr, y_margin_scr, width=2, fill="black")

        # 3. Sobe até o fundo do MBR
        _, y_mbr_bot_scr = self.t(self.X_MAR_MBR, mbr_bottom_y)
        self.create_line(x_mbr_scr, y_margin_scr, x_mbr_scr, y_mbr_bot_scr, 
                         width=2, fill="black", arrow=tk.LAST, arrowshape=(8, 10, 3))

        # --- BUS C (Vertical) ---
        xc_start, yc_start = self.t(bus_c_x, margin_y)
        xc_end, yc_end = self.t(bus_c_x, self.Y_START)
        self.create_line(xc_start, yc_start, xc_end, yc_end, width=3, fill="black")