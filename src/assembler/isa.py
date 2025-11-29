"""
Instruction Set Architecture (ISA) do MAC-1.
Fonte: Tabela "Microinstruções MAC-I", Página 1 do documento 'MAC I e MIC I.pdf'.
"""

from enum import Enum

class InstructionType(Enum):
    MEMORY_OP = 1    # Opcode (4 bits) + Endereço (12 bits) | Ex: LODD, JUMP
    CONST_OP = 2     # Opcode (8 bits) + Constante (8 bits) | Ex: INSP, DESP
    NO_OP = 3        # Opcode Fixo (16 bits)                | Ex: PSHI, RETN

# Dicionário de Instruções
# Chave: Mnemônico
# Valor: (Opcode Base, Tipo da Instrução)
MAC1_INSTRUCTIONS = {
    # --- Instruções de Acesso à Memória e Controle (4 bits superiores) ---
    "LODD": (0x0000, InstructionType.MEMORY_OP),  # Load Direct
    "STOD": (0x1000, InstructionType.MEMORY_OP),  # Store Direct
    "ADDD": (0x2000, InstructionType.MEMORY_OP),  # Add Direct
    "SUBD": (0x3000, InstructionType.MEMORY_OP),  # Subtract Direct
    "JPOS": (0x4000, InstructionType.MEMORY_OP),  # Jump on non-negative
    "JZER": (0x5000, InstructionType.MEMORY_OP),  # Jump on zero
    "JUMP": (0x6000, InstructionType.MEMORY_OP),  # Jump unconditional
    "LOCO": (0x7000, InstructionType.MEMORY_OP),  # Load Constant (0 <= x <= 4095)
    "LODL": (0x8000, InstructionType.MEMORY_OP),  # Load Local
    "STOL": (0x9000, InstructionType.MEMORY_OP),  # Store Local
    "ADDL": (0xA000, InstructionType.MEMORY_OP),  # Add Local
    "SUBL": (0xB000, InstructionType.MEMORY_OP),  # Subtract Local
    "JNEG": (0xC000, InstructionType.MEMORY_OP),  # Jump on negative
    "JNZE": (0xD000, InstructionType.MEMORY_OP),  # Jump unless zero
    "CALL": (0xE000, InstructionType.MEMORY_OP),  # Call procedure

    # --- Instruções Especiais (Prefixo 1111...) ---
    
    # Sem operandos (Opcodes completos de 16 bits)
    "PSHI": (0xF000, InstructionType.NO_OP),      # Push Indirect
    "POPI": (0xF200, InstructionType.NO_OP),      # Pop Indirect
    "PUSH": (0xF400, InstructionType.NO_OP),      # Push
    "POP":  (0xF600, InstructionType.NO_OP),      # Pop
    "RETN": (0xF800, InstructionType.NO_OP),      # Return
    "SWAP": (0xFA00, InstructionType.NO_OP),      # Swap AC, SP

    # Com constante de 8 bits (Prefixo de 8 bits)
    # Nota: A tabela mostra '11111100yyyyyyyy' para INSP. 11111100 bin = 0xFC hex.
    "INSP": (0xFC00, InstructionType.CONST_OP),   # Increment SP
    "DESP": (0xFE00, InstructionType.CONST_OP),   # Decrement SP
}