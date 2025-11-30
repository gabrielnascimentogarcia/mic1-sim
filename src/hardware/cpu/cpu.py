from src.hardware.memory.manager import MemoryManager
from src.hardware.cpu.datapath import Datapath
from src.hardware.cpu.control import ControlUnit
from src.hardware.cpu.registers import Registers
from src.hardware.cpu.firmware import CONTROL_STORE

class CPU:
    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager
        self.registers = Registers()
        self.datapath = Datapath(self.registers)
        self.control_unit = ControlUnit()
        
        # Carrega o firmware padrão ao iniciar
        self.control_unit.load_firmware(CONTROL_STORE)

    def step(self):
        """Executa UM ciclo de clock (uma microinstrução)."""
        
        # 1. Busca Microinstrução (Fetch Microcode) do endereço atual (MPC)
        self.control_unit.fetch()
        mir = self.control_unit.decode()
        
        # 2. Executa Datapath (Operações de hardware: ULA, Shifter, Registradores)
        self.datapath.run_cycle(mir)
        
        # 3. Interação com Memória (Baseado nos sinais do MIR)
        if mir.rd:
            # Leitura: MAR -> MBR
            # Na simulação, a leitura é instantânea, disponibilizando para o próximo ciclo
            addr = self.registers.MAR
            val = self.memory.read(addr)
            self.registers.MBR = val
            
        if mir.wr:
            # Escrita: MBR -> Memória[MAR]
            addr = self.registers.MAR
            val = self.registers.MBR
            self.memory.write(addr, val)

        # 4. Atualiza MPC (Sequenciamento) para a próxima microinstrução
        # Pega flags da ULA para decidir pulos condicionais
        n_flag = self.datapath.alu.N
        z_flag = self.datapath.alu.Z
        ir_val = self.registers.IR
        
        next_addr = self.control_unit.get_next_mpc(mir, n_flag, z_flag, ir_val)
        self.control_unit.update_mpc(next_addr)

    def run_debug(self, steps=20):
        """Roda X passos e imprime estado (para testes manuais no terminal)."""
        print(f"{'MPC':<5} | {'PC':<5} | {'AC':<5} | {'IR':<20} | {'Microinstrução'}")
        for _ in range(steps):
            print(f"{self.control_unit.MPC:<5} | {self.registers.PC:<5} | {self.registers.AC:<5} | {bin(self.registers.IR):<20} | ...")
            self.step()