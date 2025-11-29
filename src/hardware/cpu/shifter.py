"""
Deslocador (Shifter) do MIC-1.
Processa o resultado da ULA antes de ser escrito no barramento C.
"""

from src.common.constants import ShifterOp, MASK_16BIT

class Shifter:
    def shift(self, op: int, value: int) -> int:
        """
        Aplica o deslocamento de bits conforme o sinal de controle.
        """
        result = value & MASK_16BIT

        if op == ShifterOp.NO_SHIFT.value:
            return result
        
        elif op == ShifterOp.RIGHT.value:
            # Deslocamento Aritmético à Direita (Mantém sinal? O MIC-1 padrão costuma usar lógico aqui, 
            # mas vamos assumir lógico (>>>) para simplificar operações de bits comuns).
            return (result >> 1) & MASK_16BIT
            
        elif op == ShifterOp.LEFT.value:
            # Deslocamento à Esquerda (Multiplicação por 2)
            # O bit 15 é perdido, entra 0 no bit 0.
            return (result << 1) & MASK_16BIT
        
        return result