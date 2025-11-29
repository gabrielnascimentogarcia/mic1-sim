"""
Definições de constantes fundamentais da arquitetura MAC-1 / MIC-1.
Baseado estritamente nos diagramas e microprogramas dos arquivos fornecidos.
"""

from enum import Enum

# --- Máscaras de Bits e Largura de Dados ---
# O diagrama da Via de Dados  mostra barramentos de 16 bits.
# AMASK (Address Mask) e SMASK (Small Mask/Constant Mask) são explicitamente citados no datapath.
BIT_WIDTH = 16
MASK_16BIT = 0xFFFF  # Garante que valores fiquem entre 0x0000 e 0xFFFF

AMASK = 0x0FFF       # 12 bits inferiores (para endereçamento de memória MAC-1) [cite: 2302]
SMASK = 0x00FF       # 8 bits inferiores (para constantes como em LOCO, INSP) [cite: 2302]

# --- Operações da ULA (ALU) ---
# O diagrama mostra 2 bits de controle para a ALU, permitindo 4 operações.
# As operações são inferidas do microprograma[cite: 2303]:
# - Soma (+): usado em ADDD, inc PC
# - And (band): usado em JZER, mascaramentos
# - Identidade (pass A): usado para mover dados (alu:=ir)
# - Inversão (inv): usado em SUBD (complemento de 1)
class ALUOp(Enum):
    ADD = 0         # A + B
    AND = 1         # A AND B
    IDENTITY = 2    # A (Pass-through)
    NOT = 3         # NOT A (Inversão bit a bit)

# --- Operações do Deslocador (Shifter) ---
# O diagrama mostra 2 bits de controle para o Deslocador.
# O microprograma menciona "Ishift"[cite: 2303].
class ShifterOp(Enum):
    NO_SHIFT = 0
    RIGHT = 1       # Deslocamento aritmético ou lógico (a definir na implementação lógica)
    LEFT = 2        # Deslocamento para esquerda
    # O quarto estado (3) é indefinido nos documentos, manteremos reservado.