"""
Gerador de Código (Code Generator) para MAC-1.
Implementa a estratégia de 'Two-Pass Assembler' para resolver rótulos e gerar binário.
"""

from typing import List, Dict, Tuple
from src.assembler.parser import ParsedLine, AssemblerError
from src.assembler.isa import MAC1_INSTRUCTIONS, InstructionType
from src.common.constants import MASK_16BIT, AMASK, SMASK

class CodeGenerator:
    def __init__(self):
        self.symbol_table: Dict[str, int] = {}  # Mapeia Label -> Endereço de Memória
        self.current_address = 0

    def generate(self, lines: List[ParsedLine]) -> List[int]:
        """
        Executa os dois passos da montagem e retorna uma lista de inteiros (código de máquina).
        """
        # --- PASSO 1: Construir a Tabela de Símbolos ---
        self.current_address = 0
        self.symbol_table = {}

        for line in lines:
            # Se a linha tem um rótulo, salva o endereço atual associado a ele
            if line.label:
                if line.label in self.symbol_table:
                    raise AssemblerError(line.line_num, f"Rótulo duplicado: '{line.label}'.")
                self.symbol_table[line.label] = self.current_address

            # Se a linha tem uma instrução, ela ocupa 1 palavra de memória (incrementa endereço)
            if line.mnemonic:
                self.current_address += 1

        # --- PASSO 2: Gerar Código de Máquina ---
        machine_code: List[int] = []
        
        # Reinicia endereço apenas para controle de erro (opcional), mas a iteração é linear
        for line in lines:
            if not line.mnemonic:
                continue  # Linhas que só tinham rótulos não geram código sozinhas

            code = self._assemble_instruction(line)
            machine_code.append(code)

        return machine_code

    def _assemble_instruction(self, line: ParsedLine) -> int:
        """Converte uma única linha parseada em um inteiro de 16 bits."""
        base_opcode, instr_type = MAC1_INSTRUCTIONS[line.mnemonic]
        
        # 1. Instruções sem operandos (ex: PSHI, RETN)
        # O opcode já é a instrução completa de 16 bits.
        if instr_type == InstructionType.NO_OP:
            return base_opcode

        # 2. Instruções com Constante de 8 bits (ex: INSP 5)
        # Formato: [8 bits Opcode] [8 bits Constante]
        elif instr_type == InstructionType.CONST_OP:
            operand_val = self._parse_operand(line.operand)
            
            # Validação: Constante deve caber em 8 bits (0-255)
            if not (0 <= operand_val <= 0xFF):
                raise AssemblerError(line.line_num, f"Operando '{operand_val}' fora do limite de 8 bits (0-255).")
            
            # Combina opcode (ex: 0xFC00) com constante (ex: 0x05) -> 0xFC05
            return base_opcode | (operand_val & 0xFF)

        # 3. Instruções de Memória (ex: LODD 10, JUMP LOOP)
        # Formato: [4 bits Opcode] [12 bits Endereço]
        elif instr_type == InstructionType.MEMORY_OP:
            # O operando pode ser um número OU um rótulo
            if line.operand in self.symbol_table:
                address = self.symbol_table[line.operand]
            else:
                address = self._parse_operand(line.operand)

            # Validação: Endereço deve caber em 12 bits (0-4095)
            if not (0 <= address <= AMASK):
                raise AssemblerError(line.line_num, f"Endereço '{address}' fora do limite de 12 bits (0-4095).")

            # Combina opcode (ex: 0x0000) com endereço (ex: 0x00A) -> 0x000A
            return base_opcode | (address & AMASK)

        else:
            raise AssemblerError(line.line_num, "Tipo de instrução interno desconhecido.")

    def _parse_operand(self, operand_str: str) -> int:
        """Tenta converter string para inteiro (suporta decimal e hex 0x)."""
        try:
            # Tenta converter como inteiro (aceita '10', '0xFF', etc.)
            return int(operand_str, 0) 
        except ValueError:
            # Se falhar e não estava na tabela de símbolos (já verificado antes), é erro.
            raise ValueError(f"Operando inválido: '{operand_str}'")