"""
Definição do Microprograma (Firmware) do MIC-1.
Mapeia o ciclo de busca e as instruções MAC-1 para microinstruções de 32 bits.
"""

from src.common.constants import ALUOp, ShifterOp

# Endereços fixos na Memória de Controle
ADDR_FETCH = 0     # Início do ciclo de busca

# --- Auxiliar para criar a palavra de 32 bits ---
def micro_inst(amux=0, cond=0, alu=0, sh=0, mbr=0, mar=0, rd=0, wr=0, enc=0, c=0, b=0, a=0, addr=0):
    """Constrói um inteiro de 32 bits representando a microinstrução."""
    val = 0
    val |= (amux & 1) << 31
    val |= (cond & 3) << 29
    val |= (alu & 3)  << 27
    val |= (sh & 3)   << 25
    val |= (mbr & 1)  << 24
    val |= (mar & 1)  << 23
    val |= (rd & 1)   << 22
    val |= (wr & 1)   << 21
    val |= (enc & 1)  << 20
    val |= (c & 0xF)  << 16
    val |= (b & 0xF)  << 12
    val |= (a & 0xF)  << 8
    val |= (addr & 0xFF)
    return val

# --- O MICROPROGRAMA ---
CONTROL_STORE = [0] * 256

# ==============================================================================
# CICLO DE BUSCA (FETCH CYCLE)
# ==============================================================================

# Endereço 0: MAR := PC; rd;
CONTROL_STORE[0] = micro_inst(
    mar=1,      # Carrega MAR
    rd=1,       # Sinaliza leitura da RAM
    b=2,        # B = PC (2)
    alu=ALUOp.IDENTITY.value,
    enc=0,      # Apenas MAR
    addr=1      # Próximo passo: 1
)

# Endereço 1: PC := PC + 1; rd;
CONTROL_STORE[1] = micro_inst(
    rd=1,       # Mantém leitura ativa
    b=8,        # B = +1 (Constante)
    a=2,        # A = PC
    alu=ALUOp.ADD.value, # PC + 1
    c=2,        # Grava em PC
    enc=1,
    addr=2      # Próximo passo: 2
)

# Endereço 2: IR := MBR; DECODE!
# cond=3 sinaliza para o hardware pular para o endereço do Opcode (ex: 10, 20, 30...)
CONTROL_STORE[2] = micro_inst(
    amux=1,     # Seleciona MBR
    alu=ALUOp.IDENTITY.value,
    c=5,        # Grava em IR (5)
    enc=1,
    cond=3,     # <--- DECODE (Jump to Opcode)
    addr=0      # Ignorado quando cond=3
)

# ==============================================================================
# INSTRUÇÃO: LODD (Load Direct) - Opcode 0 -> Endereço 10
# Semântica: AC := Memory[Endereço]
# ==============================================================================

# 10: MAR := IR (Endereço); rd;
CONTROL_STORE[10] = micro_inst(
    a=5,        # A = IR
    alu=ALUOp.IDENTITY.value,
    mar=1,      # Grava no MAR
    rd=1,       # Inicia leitura da memória
    enc=0,
    addr=11
)

# 11: rd; (Ciclo de espera da memória)
CONTROL_STORE[11] = micro_inst(
    rd=1,
    addr=12
)

# 12: AC := MBR; goto 0 (Fetch)
CONTROL_STORE[12] = micro_inst(
    amux=1,     # Seleciona MBR
    alu=ALUOp.IDENTITY.value,
    c=4,        # Grava em AC (4)
    enc=1,
    addr=0      # Volta para o início (Fetch)
)