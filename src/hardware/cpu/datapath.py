"""
Caminho de Dados (Datapath) do MIC-1.
Gerencia os barramentos A, B e C e a execução do ciclo de dados.
"""

from src.hardware.cpu.registers import Registers
from src.hardware.cpu.alu import ArithmeticLogicUnit
from src.hardware.cpu.shifter import Shifter
from src.hardware.cpu.control import ControlSignals

class Datapath:
    def __init__(self, registers: Registers):
        self.registers = registers
        self.alu = ArithmeticLogicUnit()
        self.shifter = Shifter()
        
        # Mapeamento numérico dos registradores para os Barramentos A, B e C.
        # Fonte: Microprograma e arquitetura padrão MIC-1.
        # 0=MAR, 1=MBR, 2=PC, 3=SP, 4=AC, 5=IR, 6=TIR, 7=0, 8=+1, 9=-1, 10=AMASK, 11=SMASK
        self.reg_map = {
            0: 'MAR', 1: 'MBR', 2: 'PC', 3: 'SP', 4: 'AC', 
            5: 'IR',  6: 'TIR'
            # 7 a 11 são constantes geradas dinamicamente
        }

    def run_cycle(self, signals: ControlSignals):
        """
        Executa um ciclo completo do datapath baseado nos sinais de controle.
        1. Lê registradores para os Barramentos A e B.
        2. Executa ULA.
        3. Executa Shifter.
        4. Escreve resultado via Barramento C (se habilitado ou via sinais dedicados).
        """
        
        # --- 1. Leitura dos Barramentos A e B ---
        val_a = self._read_bus_a(signals.a)
        val_b = self._read_bus_b(signals.b)

        # Se AMUX=1, o Latch A recebe MBR (sobrepõe a seleção do registrador A)
        # Diagrama: MUX seleciona entre "Saída do Banco de Registradores" e "MBR"
        if signals.amux:
            val_a = self.registers.MBR

        # --- 2. Execução da ULA ---
        alu_result = self.alu.execute(signals.alu, val_a, val_b)

        # --- 3. Execução do Deslocador ---
        shifter_result = self.shifter.shift(signals.sh, alu_result)

        # --- 4. Escrita nos Registradores ---
        
        # CORREÇÃO: O MAR e MBR possuem sinais de escrita dedicados (independente do ENC)
        # Isso garante que instruções como "MAR := PC" funcionem mesmo sem selecionar MAR no bus C.
        if signals.mar:
            self.registers.write('MAR', shifter_result)
            
        if signals.mbr:
            self.registers.write('MBR', shifter_result)

        # Escrita padrão do Barramento C (controlada pelo decodificador 4-pra-16)
        if signals.enc:
            self._write_bus_c(signals.c, shifter_result)

    def _read_bus_a(self, reg_index: int) -> int:
        """Lê o valor para o barramento A (Habilitado pelo campo A)."""
        # Apenas registradores podem ser lidos no bus A no MIC-1 padrão (sem constantes)
        if reg_index in self.reg_map:
            return self.registers.read(self.reg_map[reg_index])
        return 0 # Índice inválido ou não conectado

    def _read_bus_b(self, reg_index: int) -> int:
        """Lê o valor para o barramento B (Registradores ou Constantes)."""
        # Tratamento de constantes (Indices 7 a 11)
        if reg_index == 7: return 0
        if reg_index == 8: return 1
        if reg_index == 9: return -1 & 0xFFFF # Representação de -1 em 16 bits
        if reg_index == 10: return 0x0FFF     # AMASK
        if reg_index == 11: return 0x00FF     # SMASK
        
        if reg_index in self.reg_map:
            return self.registers.read(self.reg_map[reg_index])
        return 0

    def _write_bus_c(self, reg_index: int, value: int):
        """Escreve o valor do barramento C no registrador de destino."""
        if reg_index in self.reg_map:
            self.registers.write(self.reg_map[reg_index], value)