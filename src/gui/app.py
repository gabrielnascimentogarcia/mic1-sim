"""
Aplicação Principal (GUI) do Simulador MIC-1.
Integra o Hardware com a Interface Gráfica Tkinter.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Importações do Hardware
from src.hardware.cpu.control import ControlUnit
from src.hardware.cpu.datapath import Datapath
from src.hardware.cpu.registers import Registers
from src.hardware.memory.ram import MainMemory
from src.hardware.memory.cache import DirectCache
from src.hardware.memory.manager import MemoryManager

# Importações de Ferramentas
from src.assembler.parser import AssemblyParser
from src.assembler.codegen import CodeGenerator
from src.common.constants import AMASK

# Importação da View
from src.gui.components.datapath_view import DatapathView

class Mic1SimulatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador MIC-1 / MAC-1 (Prof. Gabriel Garcia)")
        self.geometry("1200x800")
        
        # --- 1. Inicialização do Hardware ---
        self.init_hardware()
        
        # --- 2. Interface Gráfica ---
        self.create_widgets()
        
        # --- 3. Estado da Simulação ---
        self.running = False
        self.speed = 1000 # ms
        self.after_id = None
        
        # Atualiza a tela inicial
        self.refresh_view()

    def init_hardware(self):
        """Instancia e conecta todos os componentes do computador."""
        # Memória
        self.ram = MainMemory()
        self.cache = DirectCache()
        self.mmu = MemoryManager(self.ram, self.cache)
        
        # CPU
        self.registers = Registers()
        self.control_unit = ControlUnit()
        self.datapath = Datapath(self.registers)
        
        # Carregar Microprograma Padrão (Hardcoded ou de arquivo)
        # POR ENQUANTO: Vamos carregar um microprograma vazio ou de teste
        # Na versão final, carregaremos o mic1.rom aqui
        pass

    def create_widgets(self):
        """Monta o layout da janela."""
        
        # Layout Principal: Esquerda (Controles/Memória) | Direita (Datapath)
        main_paned = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # --- Painel Esquerdo ---
        left_frame = ttk.Frame(main_paned, width=300)
        main_paned.add(left_frame)
        
        # Controles
        control_group = ttk.LabelFrame(left_frame, text="Controle de Execução")
        control_group.pack(fill=tk.X, pady=5)
        
        btn_load = ttk.Button(control_group, text="Carregar Programa (.asm)", command=self.load_program)
        btn_load.pack(fill=tk.X, padx=5, pady=2)
        
        self.btn_step = ttk.Button(control_group, text="Passo (Clock)", command=self.step_clock)
        self.btn_step.pack(fill=tk.X, padx=5, pady=2)
        
        self.btn_run = ttk.Button(control_group, text="Executar (Run)", command=self.toggle_run)
        self.btn_run.pack(fill=tk.X, padx=5, pady=2)

        btn_reset = ttk.Button(control_group, text="Reset", command=self.reset_simulation)
        btn_reset.pack(fill=tk.X, padx=5, pady=2)

        # Visualizador de Memória
        mem_group = ttk.LabelFrame(left_frame, text="Memória Principal (RAM)")
        mem_group.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Lista com Scrollbar
        self.mem_list = tk.Listbox(mem_group, font=("Consolas", 10))
        scroll = ttk.Scrollbar(mem_group, orient=tk.VERTICAL, command=self.mem_list.yview)
        self.mem_list.configure(yscrollcommand=scroll.set)
        
        self.mem_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # --- Painel Direito (Datapath Visual) ---
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame)
        
        lbl_dp = ttk.Label(right_frame, text="Visualização da Microarquitetura", font=("Arial", 12, "bold"))
        lbl_dp.pack(pady=5)
        
        # Instancia nossa classe desenhista
        self.datapath_view = DatapathView(right_frame, self.registers)
        self.datapath_view.pack(fill=tk.BOTH, expand=True)

    def load_program(self):
        """Abre arquivo .asm, monta e carrega na RAM."""
        file_path = filedialog.askopenfilename(filetypes=[("Assembly MAC-1", "*.asm")])
        if not file_path: return
        
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            
            # 1. Parse e Codegen
            parser = AssemblyParser()
            codegen = CodeGenerator()
            
            parsed = parser.parse(code)
            binary = codegen.generate(parsed)
            
            # 2. Carrega na RAM
            self.ram.load_program(binary, start_address=0)
            
            # 3. Atualiza interface
            self.refresh_memory_view()
            messagebox.showinfo("Sucesso", "Programa carregado com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro de Montagem", str(e))

    def step_clock(self):
        """Executa um ciclo de clock do sistema."""
        # 1. Busca microinstrução (Fetch)
        self.control_unit.fetch()
        
        # 2. Decodifica
        signals = self.control_unit.decode()
        
        # 3. Executa Datapath (Operações internas)
        self.datapath.run_cycle(signals)
        
        # 4. Operações de Memória (Se RD/WR ativos)
        # O Datapath não acessa memória diretamente no meu design anterior, 
        # quem controla isso é a Unidade de Controle através de sinais para MAR/MBR.
        # Precisamos conectar o MBR/MAR à MMU aqui no loop principal ou dentro do Datapath.
        # Design Padrão MIC-1: Acesso ocorre no fim do ciclo.
        
        if signals.rd:
            # Leitura: MBR = Mem[MAR]
            addr = self.registers.MAR
            data = self.mmu.read(addr)
            self.registers.MBR = data # Atualiza MBR direto (bypass simulado)
            
        if signals.wr:
            # Escrita: Mem[MAR] = MBR
            addr = self.registers.MAR
            val = self.registers.MBR
            self.mmu.write(addr, val)

        # 5. Atualiza MPC
        # Lógica de Microsequenciamento (Next Address Logic)
        # Esta lógica é complexa e envolve as flags N/Z da ULA.
        # Precisa ser implementada no ControlUnit ou aqui.
        # Para simplificar agora: Vamos assumir addr puro ou lógica básica.
        next_addr = signals.addr # Padrão
        
        # Lógica de Desvio (COND)
        # COND: 0=NoJump, 1=JumpN, 2=JumpZ, 3=Jump Always (simulando High bit)
        if signals.cond == 1 and self.datapath.alu.N:
            next_addr = next_addr | 0x100 # Exemplo de lógica OR do diagrama
        elif signals.cond == 2 and self.datapath.alu.Z:
            next_addr = next_addr | 0x100
        
        self.control_unit.update_mpc(next_addr)

        # 6. Atualiza Interface
        self.refresh_view(signals)

    def toggle_run(self):
        if self.running:
            self.running = False
            self.btn_run.config(text="Executar (Run)")
            if self.after_id: self.after_cancel(self.after_id)
        else:
            self.running = True
            self.btn_run.config(text="Pausar")
            self.run_loop()

    def run_loop(self):
        if self.running:
            self.step_clock()
            self.after_id = self.after(self.speed, self.run_loop)

    def reset_simulation(self):
        self.init_hardware()
        self.refresh_view()

    def refresh_view(self, last_signals=None):
        # Atualiza Datapath
        self.datapath_view.update_state(last_signals, self.registers.debug_state())
        
        # Atualiza Memória (Só visível)
        # Otimização: atualizar apenas se mudou ou periodicamente
        pass

    def refresh_memory_view(self):
        self.mem_list.delete(0, tk.END)
        # Mostra os primeiros 100 endereços para não travar
        dump = self.ram.dump(0, 100)
        for i, val in enumerate(dump):
            self.mem_list.insert(tk.END, f"[{i:04X}]: {val:04X}")

# Entry Point
if __name__ == "__main__":
    app = Mic1SimulatorApp()
    app.mainloop()