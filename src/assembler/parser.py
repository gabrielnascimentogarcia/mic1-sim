"""
Parser do Assembly MAC-1.
Responsável por ler o código fonte, remover comentários, identificar rótulos
e validar a sintaxe básica (mnemônico + operandos).
"""

import re
from typing import List, Dict, Optional, Tuple
from src.assembler.isa import MAC1_INSTRUCTIONS, InstructionType

class AssemblerError(Exception):
    """Exceção customizada para erros de sintaxe no Assembly."""
    def __init__(self, line_num: int, message: str):
        super().__init__(f"Erro na linha {line_num}: {message}")

class ParsedLine:
    """Estrutura de dados que representa uma linha de código processada."""
    def __init__(self, line_num: int, label: Optional[str], mnemonic: str, operand: Optional[str]):
        self.line_num = line_num
        self.label = label        # Ex: "START" em "START: LODD 5"
        self.mnemonic = mnemonic  # Ex: "LODD"
        self.operand = operand    # Ex: "5", "LOOP_ADDR", "0xFF"

    def __repr__(self):
        return f"Line {self.line_num}: Label={self.label}, Op={self.mnemonic}, Arg={self.operand}"

class AssemblyParser:
    def __init__(self):
        # Regex para capturar: (Label:)? (Mnemônico) (Operando)? (Comentário)?
        # Explicação:
        # ^\s* -> Inicio da linha, ignorando espaços
        # (?P<label>\w+:\s*)?   -> Grupo Label opcional (letras + :)
        # (?P<mnem>\w+)?        -> Grupo Mnemônico (letras)
        # \s* -> Espaços
        # (?P<op>[^;\s]+)?      -> Grupo Operando opcional (qualquer coisa que não seja espaço ou ;)
        self.line_regex = re.compile(r"^\s*(?P<label>\w+:)?\s*(?P<mnem>\w+)?\s*(?P<op>[^;\s]+)?")

    def parse(self, source_code: str) -> List[ParsedLine]:
        """
        Processa o código fonte completo e retorna uma lista de objetos ParsedLine.
        """
        parsed_lines = []
        lines = source_code.split('\n')

        for i, line in enumerate(lines):
            line_num = i + 1
            # Remover comentários (tudo após ';') e espaços extras
            clean_line = line.split(';')[0].strip()
            
            if not clean_line:
                continue  # Linha vazia ou apenas comentário

            match = self.line_regex.match(clean_line)
            if not match:
                raise AssemblerError(line_num, "Sintaxe inválida.")

            label = match.group('label')
            mnemonic = match.group('mnem')
            operand = match.group('op')

            # Limpeza do label (remover o ':')
            if label:
                label = label.strip().replace(':', '')

            # Se a linha só tem label (ex: "LOOP:"), o mnemônico é None.
            # Mas se tiver mnemônico, precisamos validar.
            if mnemonic:
                mnemonic = mnemonic.upper()
                self._validate_syntax(line_num, mnemonic, operand)
                
                parsed_lines.append(ParsedLine(line_num, label, mnemonic, operand))
            elif label:
                # Caso especial: Linha só com label. 
                # Trataremos associando este label à próxima instrução no CodeGen.
                parsed_lines.append(ParsedLine(line_num, label, None, None))

        return parsed_lines

    def _validate_syntax(self, line_num: int, mnemonic: str, operand: Optional[str]):
        """Verifica se o mnemônico existe e se a quantidade de operandos está correta."""
        
        if mnemonic not in MAC1_INSTRUCTIONS:
            raise AssemblerError(line_num, f"Instrução desconhecida '{mnemonic}'.")

        opcode, instr_type = MAC1_INSTRUCTIONS[mnemonic]

        # Validação baseada no tipo da instrução (ISA)
        if instr_type == InstructionType.NO_OP:
            if operand is not None:
                raise AssemblerError(line_num, f"A instrução '{mnemonic}' não aceita operandos.")
        
        elif instr_type in (InstructionType.MEMORY_OP, InstructionType.CONST_OP):
            if operand is None:
                raise AssemblerError(line_num, f"A instrução '{mnemonic}' exige um operando.")