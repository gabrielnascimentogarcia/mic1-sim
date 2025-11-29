"""
Unidade de Controle do MIC-1.
Responsável por armazenar o Microprograma e decodificar as microinstruções de 32 bits.
Baseado no diagrama da Página 3 do documento 'MAC I e MIC I.pdf'.
"""

from dataclasses import dataclass
from typing import List

@dataclass
class ControlSignals:
    """
    Representação decodificada de uma microinstrução (sinais elétricos).
    """
    amux: int   # 1 bit (0=Latch A, 1=MBR)
    cond: int   # 2 bits (Controle de pulo: 0=NoJump, 1=JumpN, 2=JumpZ, 3=Jump)
    alu: int    # 2 bits (Operação da ULA)
    sh: int     # 2 bits (Deslocador)
    mbr: bool   # 1 bit (Escrever no MBR?)
    mar: bool   # 1 bit (Escrever no MAR?)
    rd: bool    # 1 bit (Ler da Memória?)
    wr: bool    # 1 bit (Escrever na Memória?)
    enc: bool   # 1 bit (Enable C - Gravar nos registradores?)
    c: int      # 4 bits (Endereço do registrador de destino no Barramento C)
    b: int      # 4 bits (Endereço do registrador fonte no Barramento B)
    a: int      # 4 bits (Endereço do registrador fonte no Barramento A)
    addr: int   # 8 bits (Próximo endereço do MPC)

class ControlUnit:
    def __init__(self):
        # Memória de Controle: 256 palavras de 32 bits
        # Fonte: Diagrama "Memória de controle 256 x 32"
        self.control_store: List[int] = [0] * 256
        
        self.MPC = 0  # MicroProgram Counter (Endereço da microinstrução atual)
        self.MIR = 0  # MicroInstruction Register (Conteúdo da microinstrução atual)

    def load_firmware(self, microprogram: List[int]):
        """Carrega o array de inteiros (microcódigo) na memória de controle."""
        if len(microprogram) > 256:
            raise ValueError("O microprograma excede o tamanho da Memória de Controle (256 palavras).")
        
        for i, instruction in enumerate(microprogram):
            self.control_store[i] = instruction

    def fetch(self):
        """Busca a microinstrução apontada pelo MPC e coloca no MIR."""
        self.MIR = self.control_store[self.MPC]

    def decode(self) -> ControlSignals:
        """
        Decodifica o valor de 32 bits do MIR nos campos de controle individuais.
        A ordem dos bits segue estritamente o diagrama da Via de Dados.
        Bit 31 (Mais significativo) -> AMUX
        Bit 0  (Menos significativo) -> ADDR
        """
        mir = self.MIR

        # Extração de bits usando máscaras e shifts
        # Layout: [AMUX(1)|COND(2)|ALU(2)|SH(2)|MBR(1)|MAR(1)|RD(1)|WR(1)|ENC(1)|C(4)|B(4)|A(4)|ADDR(8)]
        
        addr = mir & 0xFF                 # Bits 0-7 (8 bits)
        a    = (mir >> 8) & 0xF           # Bits 8-11 (4 bits)
        b    = (mir >> 12) & 0xF          # Bits 12-15 (4 bits)
        c    = (mir >> 16) & 0xF          # Bits 16-19 (4 bits)
        
        enc  = bool((mir >> 20) & 0x1)    # Bit 20
        wr   = bool((mir >> 21) & 0x1)    # Bit 21
        rd   = bool((mir >> 22) & 0x1)    # Bit 22
        mar  = bool((mir >> 23) & 0x1)    # Bit 23
        mbr  = bool((mir >> 24) & 0x1)    # Bit 24
        
        sh   = (mir >> 25) & 0x3          # Bits 25-26 (2 bits)
        alu  = (mir >> 27) & 0x3          # Bits 27-28 (2 bits)
        cond = (mir >> 29) & 0x3          # Bits 29-30 (2 bits)
        amux = (mir >> 31) & 0x1          # Bit 31 (1 bit)

        return ControlSignals(
            amux=amux, cond=cond, alu=alu, sh=sh,
            mbr=mbr, mar=mar, rd=rd, wr=wr, enc=enc,
            c=c, b=b, a=a, addr=addr
        )

    def update_mpc(self, next_addr: int):
        """Atualiza o MPC para o próximo ciclo."""
        self.MPC = next_addr